'''
Created on May 29, 2019

@author: riaps
'''
# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import time
import os
import capnp
import weathermonitor_capnp
#import pydevd
# riaps:keep_import:end

class TempSensor(Component):
# riaps:keep_constr:begin
    def __init__(self):
        super(TempSensor, self).__init__()
        self.pid = os.getpid()
        #pydevd.settrace(host='192.168.1.101',port=5678)
        self.temperature = 65
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting TempSensor, %s" % (str(self.pid),str(now)))
        self.logger.info("Initial temp:%d, %s" % (self.temperature,str(now)))
# riaps:keep_constr:end

# riaps:keep_clock:begin
    def on_clock(self):
        now = time.ctime(int(time.time()))
        msg = self.clock.recv_pyobj()
        self.temperature = self.temperature + 1
        tmsg = weathermonitor_capnp.TempData.new_message()
        tmsg.temperature = self.temperature
        tmsgBytes = tmsg.to_bytes()
        self.logger.info("on_clock(): Temperature - %s, PID %s, %s" % (tmsg.temperature,str(self.pid),str(now)))
        try:
            self.ready.send(tmsgBytes)
        except PortError as e:
            self.logger.error("on_clock:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.error("on_clock: port error received")

# riaps:keep_clock:end

# riaps:keep_impl:begin
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping TempSensor, %s" % (str(self.pid),now))
# riaps:keep_impl:end
