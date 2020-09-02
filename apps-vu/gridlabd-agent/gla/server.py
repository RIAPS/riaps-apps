'''
Client service implementation

@author: riaps
'''
import os
import time
import threading
import logging
# import ssl
import zmq
import rpyc
from rpyc import async_
from rpyc.utils.server import ThreadedServer
import netifaces
# from rpyc.utils.authenticators import SSLAuthenticator

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

theAgent = None

class Client(object):
    '''
     Client represents a connected RIAPS device component 
    '''
    def __init__(self, name, callback,parent):
        self.name = name
        self.stale = False
        self.callback = callback
        self.parent = parent
        self.log("+ %s" %(self.name,))

    def logout(self):
        '''
        Logs out a node from service. Called when connection to the RIAPS node is lost. 
        '''
        if self.stale:
            return
        self.stale = True
        self.callback = None
        self.log("- %s " % (self.name,))    
                
    def log(self, text):
        '''
        Adds a log message to the GUI
        '''
        self.parent.logger.info(text)
        # self.socket.send_pyobj(text)


    def callClient(self,arg):
        '''
        Prototypical call on a client
        '''
        res = None
        if self.callback != None:
            res = self.callback(('callClient',arg))
        return res
    
    def sendClient(self,obj,param,value,stamp):
        res = None
        if self.callback != None:
            res = self.callback(('sendClient',obj,param,value,stamp))
        return res
    
            
class Service(rpyc.Service):
    '''
    Service implementation (rpyc service)
    '''
    
    ALIASES = ["RIAPS_GLA"]              # Registry name for the service
    
    STOPPING = None
    
    def on_connect(self,_conn = None):
        '''
        Called when a client connects. Subsequently the client must login. 
        '''
        if Service.STOPPING: return
        self.client = None
        self.logger = logging.getLogger(__name__)

    def discard(self):
        '''
        Discard the client
        '''
        if self.client:
            self.client.logout()
            theAgent.unsubscribe(self.client)
            theAgent.delClient(self.client.name)
            self.client = None
        
    def on_disconnect(self,_conn = None):
        '''
        Called when a client disconnects
        '''
        if Service.STOPPING: return
        self.discard()

    def exposed_login(self,clientName,callback):
        '''
        Log into the service. 
        clientName must be a globally unique name for the client
        callback is a client-side callback function that takes one argument 
        '''
        if Service.STOPPING: return
        global theAgent
        if (self.client and not self.client.stale) or theAgent.isClient(clientName):
            self.logger.warn("discarding client %s",clientName)
            self.discard()
        self.client = Client(clientName, async_(callback),self)   # Register client's callback
        theAgent.addClient(clientName,self.client)      
        return ('ok',)  # Reply to the client
    
    def subscribe(self,sub):
        '''
        Client subscribes to messages
        sub is a tuple of names: (object,attribute,unit)
        '''
        theAgent.subscribe(self.client,sub)
        
    def query(self, query):
        '''
        Client queries for a value
        query is a tuple of names: (object,attribute,unit)
        '''
        result = theAgent.query(self.client,query)
        return result
    
    def publish(self,pub):
        '''
        Client publishes a message
        pub is a tuple: (object,attribute,value,unit)
        '''
        theAgent.publish(self.client,pub)

def getHostIP():
    ipAddressList = []
    ifNames = netifaces.interfaces()      
    for ifName in ifNames:
        ifInfo = netifaces.ifaddresses(ifName)
        if netifaces.AF_INET in ifInfo:
            ifAddrs = ifInfo[netifaces.AF_INET]
            ifAddr = ifAddrs[0]['addr']
            if ifAddr == '127.0.0.1':
                continue
            else:
                ipAddressList.append(ifAddr)
    return ipAddressList[0]

class ServiceThread(threading.Thread):
    '''
    Control server main execution thread.
    Note: ThreadedServer launches a new thread for every connection.  
    '''
    def __init__(self,grunner,host,port):
        threading.Thread.__init__(self)
        global theAgent
        theAgent = grunner
        self.host = host
        self.port = port

    def run(self):
        '''
        Runs the rpyc ThreadedServer with the service implementation.
        NOTE: it expects a rpyc service registry running 
        '''
#         self.auth = SSLAuthenticator(keyFile, certFile,
#                                      cert_reqs=ssl.CERT_REQUIRED, ca_certs=theAgent.certFile,
#                                      ) if Config.SECURITY else None
        if self.host == "":
            self.host = getHostIP()
        self.server = ThreadedServer(Service,hostname=self.host, port=self.port,
                                     # authenticator = self.auth,
                                     auto_register=True,
                                     protocol_config = {"allow_public_attrs" : True})
        self.server.start()
        time.sleep(0.010)
        
    def stop(self):
        '''
        Terminates the service. Called when the program exits. 
        '''
        Service.STOPPING = True
        self.server.close()


