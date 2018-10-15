# import riaps
from riaps.run.comp import Component
import logging
import os
import zmq
import time
import urllib

class GenController(Component):
    def __init__(self,
                 upperThreshold,upperValue,
                 lowerThreshold,lowerValue,
                 initialValue):
        super(GenController, self).__init__()
        self.value = initialValue
        self.upperThreshold,self.upperValue,self.lowerThreshold,self.lowerValue = \
            upperThreshold,upperValue,lowerThreshold,lowerValue

    def on_sensor(self):
        self.logger.info("Sending = %f" % self.value)
        self.actuator.send_pyobj(self.value)
        sensorValue = self.sensor.recv_pyobj()
        self.logger.info("Received = %f" % sensorValue)
        if sensorValue > self.upperThreshold and self.value == self.lowerValue:
            self.value = self.upperValue
        elif sensorValue <= self.lowerThreshold and self.value == self.upperValue:
            self.value = self.lowerValue

    def __destroy__(self):
        self.logger.info("__destroy__")



