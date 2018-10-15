# import riaps
from riaps.run.comp import Component
import logging
import os
import re
import zmq
import time
import urllib.request

class GenGridlabD(Component):
    def __init__(self,gldServer,
                 sensorObject,sensorParameter,sensorUnit,
                 actuatorObject,actuatorParameter,actuatorUnit):
        super(GenGridlabD, self).__init__()
        self.gldServer = gldServer
        self.sensorObject,self.sensorParameter,self.sensorUnit = \
             sensorObject,sensorParameter,sensorUnit
        self.actuatorObject,self.actuatorParameter,self.actuatorUnit = \
            actuatorObject,actuatorParameter,actuatorUnit
        self.queryString = self.gldServer+'/xml/'+self.sensorObject+'/'+self.sensorParameter
        self.queryUnitPattern = re.compile(r' %s'% self.sensorUnit)
        self.commandString = self.gldServer+'/xml/'+self.actuatorObject+'/'+self.actuatorParameter
        self.actuatorUnitPattern = re.compile(r' %s'% self.actuatorUnit)
        self.started = False
        
    def rpc(self,msg):
        '''
        Generic RPC on the Gridlab-D server
        '''
        try:
            with urllib.request.urlopen(msg) as response:
                html = response.read()
                return html
        except: 
            self.logger.info('Gridlab-D RPC failed')
            return None

    def launch(self):
        '''
        Launch the Gridlab-D sim (the server must be waiting for this)
        '''
        self.logger.info('Launching...')
        resp = self.rpc(self.gldServer+'/control/resume')
        # print ('Response: %s' % str(resp))

# Sample response
# b'<?xml version="1.0" encoding="UTF-8" ?>\n<property>\n\t<object>trip_meter1</object>\n\t<name>measured_real_power</name>\n\t<value>+4125.83 W</value>\n</property>\n'

    def query(self):
        '''
        Query an object property, throw away the unit from the end of the string
        '''
        resp = self.rpc(self.queryString)
    #    assert str(obj) in re.findall('<object>(.*)</object>',str(resp))
    #    assert str(prop) in re.findall('<name>(.*)</name>',str(resp))
        if resp != None:
            val = re.findall('<value>(.*)</value>',str(resp))[0]
            val = self.queryUnitPattern.sub('',val)
            return val
        else:
            return None

    def actuate(self,value):
        '''
        Set an object property, add the unit to the end of the string
        Value must be float
        '''
        command = self.commandString+'=%%20%s%%20%s' % (str(value),self.actuatorUnit)
        resp = self.rpc(command)
        if resp != None:
            while True:
                val = re.findall('<value>(.*)</value>',str(resp))[0]
                val = self.actuatorUnitPattern.sub('',val)
                # if float(value) == float(val): break
                break
                resp = self.rpc(self.commandString)
                if resp == None: return None
            return val
        else: 
            return None
    
    def halt(self):
        '''
        Shutdown the server
        '''
        self.logger.info('Stopping...')
        resp = self.rpc(self.gldServer+'/control/shutdown')
        # print ('Response: %s' % str(resp))

    def on_clock(self):
#         if not self.started:
#             self.launch()
#             self.started = True
        now = self.clock.recv_pyobj()   # Receive time (as float)
        # self.logger.info('on_clock():%s',now)
        sensorData = self.query()
        try:
            sensorData = float(sensorData)
        except:
            sensorData = 0.0
        self.logger.info("sensor = %f",sensorData)
        self.sensor.send_pyobj(sensorData)
    
    def on_actuator(self):
        msg = self.actuator.recv_pyobj()     # Receive actuator value
        value = msg
        self.logger.info("actuator: %f" % value)
        resp = self.actuate(value)
        self.logger.info("confirmed: %s" % resp)

    def __destroy__(self):
        self.logger.info("__destroy__")
        # self.halt()


