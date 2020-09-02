'''
    GRunner Test Client
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
from rpyc.utils.factory import DiscoveryError
from riaps.run.comp import Component

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

GLACLIENT_ENDPOINT = 'inproc://gla-client'
GLACLIENT_DATA_ENDPOINT = 'inproc://gla-client-data'

class GLAClient(threading.Thread):
    SERVICENAME = 'RIAPS_GLA'
    RECONNECT = False
    def __init__(self,name,host,port,command):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.host = host
        self.port = port
        self.command = command
        self.bgsrv = None
        self.bgsrv_data_outer = None
        self.bgsrv_data_inner = None
        self.lock = RLock()
        self.poller = None
        self.subs = []
        self.conn = None
        self.context = zmq.Context()
    
    def login(self,retry = True):
        self.conn = None
        while True:
            try:
                addrs = rpyc.utils.factory.discover(GLAClient.SERVICENAME)
                for host,port in addrs:
                    try:
                        self.conn = rpyc.connect(host,port,
                                                 config = {"allow_public_attrs" : True})
                    except socket.error as e:
                        print("%s.%s: %s" %(str(host),str(port),str(e)))
                        pass
                    if self.conn: break
            except DiscoveryError:
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

    def publish(self,pub):
        with self.lock:
            self.conn.root.publish(pub)

    def setup(self):
        self.poller = zmq.Poller()
#         self.control = self.context.socket(zmq.PAIR)
        self.control = self.command.setupPlug(self)
        global GLACLIENT_ENDPOINT
#         self.control.connect(GLACLIENT_ENDPOINT)
        self.poller.register(self.control,zmq.POLLIN)
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
            if ok and len(self.subs) > 0:
                self.subscribe(self.subs)
            while ok:
                try:
                    sockets = dict(self.poller.poll())
                    for s in sockets:
                        if s == self.control:
                            msg = self.control.recv_pyobj()
                            self.publish(msg)
                        elif s == self.bgsrv_data_outer:
                            msg = self.bgsrv_data_outer.recv_pyobj()
                            self.control.send_pyobj(msg)
                        else:
                            pass
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
            print ('callback %s', str(msg))
            self.bgsrv_data_inner.send_pyobj(msg)
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

   
def control():  
        val = '1' if control.counter < control.duty else '0'
        control.counter = (control.counter + 1) % control.period
        return ("sw_loadshed", "sw_status", val, "")    # Command message
    
control.counter = 0
control.period = 20
control.duty = 10

class TespAgent(Component):
    def __init__(self, port, host):
        super(TespAgent, self).__init__()
        signal.signal(signal.SIGTERM,self.terminate)
        signal.signal(signal.SIGINT,self.terminate)
        self.host = host
        self.port = port
        
    def handleActivate(self):
        try:
            clientName = "client-%s" % str(os.getpid())
            self.theGRunner = GLAClient(clientName,self.host,self.port, self.command)
            self.theGRunner.subscribe([("n650", "distribution_load", "VA")]) # Subscribe
            self.theGRunner.start()         # Run the thread
            time.sleep(0.1)
            self.command.activate()
            
            self.running = True
            
        except Exception as e:
            logging.error('Exception: %s' % str(e))
            if self.theGRunner != None:
                self.theGRunner.stop()
                
    def terminate(self):
        self.running = False 
            
    def on_command(self):
        msg = self.command.recv_pyobj()
        if self.running:
            self.logger.info("received %s" % str(msg))
            self.sendrdg.send_pyobj(msg)
#             cmd = control()
#             self.logger.info(cmd)
#             self.command.send_pyobj(cmd)

    def on_recvcmd(self):
        msg = self.recvcmd.recv_pyobj()
#         self.gridagent.time_granted = self.gridagent.get_simulation_time(self.gridagent.time_granted + 10)
        self.logger.info("sending command to gridlab-d: %s" % str(msg))
        self.command.send_pyobj(msg)
        self.recvcmd.send_pyobj("ok")
            
    def __destroy__(self):
        self.running = False
        self.logger.info("%s - stopping tesp agent")
        self.theGRunner.join()
        self.theGRunner.stop()           
    
'''if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", type=int,default=0,help="server port number")
    parser.add_argument("-n","--host", type=str,default='',help="server host address")
    args = parser.parse_args()
#
    signal.signal(signal.SIGTERM,terminate)
    signal.signal(signal.SIGINT,terminate)
    context = zmq.Context()
    
    command = context.socket(zmq.PAIR)  # Command to GLAClient thread 
    command.bind(GLACLIENT_ENDPOINT)
    poller = zmq.Poller()
    poller.register(command, zmq.POLLIN)
                    
    try:
        clientName = "client-%s" % str(os.getpid())
        theGRunner = GLAClient(clientName,args.host,args.port, context)
        theGRunner.subscribe([("n650", "distribution_load", "VA")]) # Subscribe
        theGRunner.start()         # Run the thread

        running = True

        while running:
            sockets = dict(poller.poll(1000.0))
            if not running: break 
            for s in sockets:
                if s == command:
                    msg = command.recv_pyobj()
                    print(msg)
                else:
                    pass
            cmd = control()
            print(cmd)
            command.send_pyobj(cmd)
            if not running: break
    
        theGRunner.join()
    except Exception as e:
        logging.error('Exception: %s' % str(e))
        if theGRunner != None:
            theGRunner.stop()
    #print ("Unexpected error:", sys.exc_info()[0])
    os._exit(0)
    
    pass
    '''