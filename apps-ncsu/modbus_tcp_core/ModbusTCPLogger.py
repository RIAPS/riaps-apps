'''
Created on Nov 27, 2019

@author: riaps
'''
from riaps.run.comp import Component
import os

class ModbusTCPLogger(Component):
    def __init__(self):
        super().__init__()
        self.pid = os.getpid()
        self.logger.info("%s - Starting modbusTCPlogger" % str(self.pid))
   
    def on_clock(self):
        now = self.clock.recv_pyobj() 
        self.logger.info("On_clock()[%s]: %s :::::::::::::::::UPDATED VALUES INCOMING::::::::::::::::::::::" % (str(self.pid), str(now)))
    
    def on_rx_modbusTCPData(self):
        msg = self.rx_modbusTCPData.recv_pyobj()
        ##self.logger.info("on_rx_modbusTCPData()[%s]: %s" % (str(self.pid), repr(msg)))
        Item=msg.items()
        #self.logger.info("::::::::: Last Updated values ::::::::::")
        for k in (Item):                                                
            ##print('VARIABLE :' ,k[0], 'VALUE :' , k[1])               #Variable , Value
            self.logger.info("Received on_rx_modbusTCPData()[%s]: %s:%s" % (str(self.pid), repr(k[0]), repr(k[1])))
            
            