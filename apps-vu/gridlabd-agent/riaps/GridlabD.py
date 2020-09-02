'''
    GridlabD RIAPS device (via gridlab-agent) 
'''

import time
import sys
import os,signal
import logging
import socket
import traceback
import argparse
import threading
from threading import RLock
import zmq
import rpyc
import rpyc.core
import rpyc.utils
from riaps.utils import spdlog_setup
import spdlog
from rpyc.utils.factory import DiscoveryError
from riaps.run.comp import Component
# from apt_offline_core.AptOfflineMagicLib import NONE

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

GLACLIENT_ENDPOINT = 'inproc://gla-client'
GLACLIENT_DATA_ENDPOINT = 'inproc://gla-client-data'

class GLAClient(threading.Thread):
    SERVICENAME = 'RIAPS_GLA'
    RECONNECT = False
    def __init__(self,owner,name,host,port,trigger):
        threading.Thread.__init__(self)
        self.owner = owner
        loggerName = self.owner.getActorName() + '.' + self.owner.getName() + '.' + 'GLAClient'
        self.logger = spdlog.ConsoleLogger(loggerName,True,True,False)
        self.logger.set_pattern(spdlog_setup.global_pattern)
        self.name = name
        self.host = host
        self.port = port
        self.relay = None 
        self.trigger = trigger
        self.bgsrv = None
        self.bgsrv_data_outer = None
        self.bgsrv_data_inner = None
        self.lock = RLock()
        self.poller = None
        self.subs = []
        self.queries = []
        self.conn = None
        self.context = zmq.Context()
    
    def login(self,retry = True):
        self.logger.info("login()")
        self.conn = None
        self.logger.info("here")
        while True:
            try:
                addrs = rpyc.utils.factory.discover(GLAClient.SERVICENAME)
                self.logger.info(str(addrs))
                for host,port in addrs:
                    try:
                        self.conn = rpyc.connect(host,port,
                                                 config = {"allow_public_attrs" : True})
                    except socket.error as e:
                        print("%s.%s: %s" %(str(host),str(port),str(e)))
                        pass
                    if self.conn: break
            except DiscoveryError:
                self.logger.info("Discovery Error")
                pass
            if self.conn: break
            if self.host and self.port:
                try:
                    self.conn = rpyc.connect(self.host,self.port,
                                             config = {"allow_public_attrs" : True})
                except socket.error as e:
                    print("%s.%s: %s" %(str(host),str(port),str(e)))
                    pass
            if self.conn: break
            if retry == False:
                return False
            else:
                time.sleep(5)
                continue
        self.bgsrv = rpyc.BgServingThread(self.conn,self.handleBgServingThreadException)
        resp = None
        try:       
            resp = self.conn.root.login(self.name,self.callback)
        except:
            traceback.print_exc()
            pass
        return type(resp) == tuple and resp[0] == 'ok'


    def subscribe(self,subs):
        if self.conn:
            with self.lock: 
                for sub in subs:
                    self.conn.root.subscribe(sub)
        else:
            self.subs = subs

    def publish(self,pubs):
        if self.conn:
            with self.lock:
                for pub in pubs:
                    self.conn.root.publish(pub)
        else:
            self.pubs = pubs
            
    def query(self, queries):
        if self.conn:
            with self.lock: 
                for query in queries:
                    result = self.conn.root.query(query)
                    self.callback(result) # send query result back
        else:
            self.queries = queries

    def setup(self):
        self.logger.info("setup()")
        self.relay = self.trigger.setupPlug(self)
        self.poller = zmq.Poller()
        self.poller.register(self.relay,zmq.POLLIN)
        self.bgsrv_data_outer = self.context.socket(zmq.PAIR)
        global GLACLIENT_DATA_ENDPOINT
        self.bgsrv_data_outer.bind(GLACLIENT_DATA_ENDPOINT)
        self.poller.register(self.bgsrv_data_outer,zmq.POLLIN)
        
    def run(self):
        self.setup()
        self.killed = False
        while True:
            if self.killed: break
            ok = self.login(True)
            self.logger.info("run: loop...")
            while ok:
                try:
                    sockets = dict(self.poller.poll(1000.0))
                    toDelete = []
                    for s in sockets:
                        if s == self.relay:
                            msg = self.relay.recv_pyobj()
                            # msg = [ 'sub'  , ( 'obj', 'attr', 'unit' ) ... ] -- Subscribe   
                            # msg = [ 'pub'  , ( 'obj', 'attr', 'unit' ) ... ] -- Publish
                            self.logger.info("run: relay recv = %s" % str(msg))
                            cmd = msg[0]
                            if cmd == 'sub':
                                self.subscribe(msg[1:])
                            elif cmd == 'pub': 
                                self.publish(msg[1:])
                            elif cmd == 'query':
                                self.query(msg[1:])
                            else:
                                self.logger.error('run: error in command: %s' % str(msg))
                        elif s == self.bgsrv_data_outer:
                            msg = self.bgsrv_data_outer.recv_pyobj()
                            self.logger.info("run: sending data = %s" % str(msg))
                            self.relay.send_pyobj(msg)
                        else:
                            pass
                        toDelete += [s]
                    for s in toDelete:
                        del sockets[s]
                except:
                    traceback.print_exc()
                    ok = False
                if self.killed or (self.bgsrv == None and self.conn == None): break
            if self.killed: break
            if GLAClient.RECONNECT:
                self.logger.info("Connection to controller lost - retrying")
                continue
            else:
                break
        pass
    
    def setupBgSocket(self):
        global GLACLIENT_DATA_ENDPOINT
        self.bgsrv_data_inner = self.context.socket(zmq.PAIR)
        self.bgsrv_data_inner.connect(GLACLIENT_DATA_ENDPOINT)
        
    def handleBgServingThreadException(self):
        self.bgsrv = None
        self.conn = None
        self.bgsrv_data_inner.close()
        self.bgsrv_data_inner = None
        
    def callback(self,msg):
        '''
        Callback from server - runs in the the background server thread  
        '''
        assert type(msg) == tuple
        if self.bgsrv_data_inner == None: self.setupBgSocket()
        
        reply = None
        try: 
            cmd = msg[0]
            # print ('callback %s' % str(msg))
            if cmd == 'sendClient' or cmd == 'ans':
                self.bgsrv_data_inner.send_pyobj(msg)
            else:
                pass
        except:
            info = sys.exc_info()
            self.logger.error("Error in callback '%s': %s %s" % (cmd, info[0], info[1]))
            traceback.print_exc()
            raise
        return reply

    def stop(self):
        self.logger.info("stopping")
        self.killed = True
        self.logger.info("stopped")

class GridlabD(Component):
    def __init__(self, host='', port=0):
        super(GridlabD, self).__init__()
        self.logger.info("__init__()")
        self.host = host
        self.port = port
        self.glaClient = None
        
    def handleActivate(self):
        self.logger.info("handleActivate()")
        try:
#             clientName = "GLA-%s" % str(hex(int.from_bytes(self.getActorID(),'big')))
            clientName = "GLA-%s" % str(os.getpid())
            self.glaClient = GLAClient(self,clientName,self.host,self.port,self.relay)
            self.glaClient.start()         # Run the thread
            time.sleep(0.1)
            self.relay.activate()
            self.running = True
        except Exception as e:
            self.logger.error('Exception: %s' % str(e))
            if self.glaClient != None:
                self.glaClient.stop()
            
    def on_command(self):
        msg = self.command.recv_pyobj()
        self.logger.info("on_command(): %s" % str(msg))
        cmd = msg[0]
        if not self.running:
            self.logger.info("GLA Client not running")
            return
        if cmd == 'pub' : 
            # msg = [ 'pub'  , ( 'obj', 'attr', 'unit' ) ... ] -- Publish
            self.relay.send_pyobj(msg)
            self.command.send_pyobj('ok')
        elif cmd == 'sub':
            # msg = [ 'sub'  , ( 'obj', 'attr', 'unit' ) ... ] -- Subscribe   
            self.relay.send_pyobj(msg)
            self.command.send_pyobj('ok')
            
        elif cmd == 'query':
            # msg = [ 'sub'  , ( 'obj', 'attr', 'unit' ) ... ] -- Subscribe   
            self.relay.send_pyobj(msg)
#             self.command.send_pyobj('ok')
        
        else:
            self.logger.error("GridlabdD.on_command: unknown command: %s" % str(msg))
    
    def on_relay(self):
        msg = self.relay.recv_pyobj()
        self.logger.info("on_relay(): recv = %s" % str(msg))
        cmd = msg[0]
        if cmd == 'sendClient':
            self.logger.info("recvd: %s" % str(msg))
            data = msg[1:]
            self.data.send_pyobj(data)
        elif cmd == 'ans':
            self.logger.info("recvd: %s" % str(msg))
            ans = msg[1:]
            self.command.send_pyobj(ans)
        else:
            pass
        
#     def on_notify(self):
#         now = self.notify.recv_pyobj()
#         self.ready.send_pyobj(now)

    def __destroy__(self):
        self.running = False
        self.logger.info("terminating GLA Client")
        self.glaClient.join()
        self.glaClient.stop()
        
        