'''
Created on Apr 4, 2017

@author: Mary Metelko
'''

'''
The GPIO device component utilizes Adafruit_BBIO for control of the GPIO pins
Need to install this on the BBBs 
    $ sudo pip3 install Adafruit_BBIO
'''

from riaps.run.comp import Component
import logging
import os
import threading
import Adafruit_BBIO.GPIO as GPIO
import pydevd

    
class GpioDeviceThread(threading.Thread):
    def __init__(self, component):
        threading.Thread.__init__(self)     
        self.terminated = threading.Event()
        self.terminated.clear()
        self.component = component
        self.gpioAvailable = False
        self.readRequest = False
        self.writeRequest = False
        self.edgeTriggerEnable = False
        self.writeValue = -1  # invalid value
        self.pid = os.getpid()
        self.component.logger.info("GpioDeviceThread [%s]: init",self.pid)
        
        # Convert input configurations into enums that represent the requests
        if self.component.direction == 'IN':
            self.direction = GPIO.IN
        elif self.component.direction == 'OUT':
            self.direction = GPIO.OUT
        else:
            self.direction = GPIO.ALT0
            
        if self.component.pull_up_down == "PUD_UP":
            self.pull_up_down = GPIO.PUD_UP
        elif self.component.pull_up_down == "PUD_DOWN":
            self.pull_up_down = GPIO.PUD_DOWN
        else:
            self.pull_up_down = GPIO.PUD_OFF
            
        if self.component.trigger_edge == "RISING":
            self.trigger_edge = GPIO.RISING
        elif self.component.trigger_edge == "FALLING":
            self.trigger_edge = GPIO.FALLING
        else:
            self.trigger_edge = GPIO.BOTH       
    
    def run(self):
        # Ask parent port to make a plug for this end
        self.dataIn_plug = self.component.dataIn_queue.setupPlug(self)  
        self.dataOut_plug = self.component.dataOut_queue.setupPlug(self)
        
        if self.terminated.is_set(): return
        self.enableGpio()  # setup the requested GPIO
           
        while True:
            if self.terminated.is_set():
                self.disableGpio() 
                break
            
            if self.writeRequest:
                dataOut = self.dataOut_plug.recv_pyobj()
                
                if dataOut == 0 or dataOut == 1:  # the only valid numbers
                    GPIO.output(self.component.bbb_pin_name, dataOut)   
                    self.component.logger.info("GpioDeviceThread - value written to GPIO %s: %s", self.component.bbb_pin_name, dataOut)            
                else:
                    self.component.logger.info("GpioDeviceThread - invalid value (%d), nothing written to GPIO %s: %s", dataOut, self.component.bbb_pin_name)                              

                # send back data written
                self.dataIn_plug.send_pyobj(dataOut)
                self.writeRequest = False
                    
            elif self.readRequest:
                gpioValue = GPIO.input(self.component.bbb_pin_name)
                #self.component.logger.info("GpioDeviceThread - value read from GPIO %s: %s", self.component.bbb_pin_name, gpioValue)            
                self.dataIn_plug.send_pyobj(gpioValue)
                self.readRequest = False   
                
            
            #MM TODO:  This option will be developed after the initial release of this device.  For now we just want to read/write when requested.        
            elif self.edgeTriggerEnable:  
                #event_detected or wait_for_edge
                self.component.logger.info("GpioDeviceThread - trigger GPIO=%s, edge=%s",self.component.bbb_pin_name, self.component.trigger_edge)
                
            else:
                pass                                                                                   
                                  
    def requestGpioWrite(self):
        self.writeRequest = True
        self.component.logger.info("GpioDeviceThread - write request received")
        
    def requestGpioRead(self):
        self.readRequest = True
        #self.component.logger.info("GpioDeviceThread - read request received")
           
    def requestEdgeTrigger(self):
        self.component.logger.info("GpioDeviceThread - edge triggering request received")
        # MM TODO:  feature to come later
        # expect to use - add_event_detect()
        # self.edgeTriggerEnable = True
        
    def enableGpio(self):
        self.component.logger.info("GpioDeviceThread setting up GPIO=%s: direction=%s resistor=%s trigger=%s ivalue=%d delay=%d [%d]", self.component.bbb_pin_name, self.component.direction, self.component.pull_up_down, self.component.trigger_edge, self.component.initial_value, self.component.setup_delay, self.pid)
        GPIO.setup(self.component.bbb_pin_name, self.direction, self.pull_up_down, self.component.initial_value, self.component.setup_delay)     
        self.component.logger.info("GpioDeviceThread GPIO=%s setup and available for use", self.component.bbb_pin_name)
        self.gpioAvailable = True
      
    def isGpioAvailable(self):
        return self.gpioAvailable
        
    def disableGpio(self):
        #if self.edgeTriggerEnable:   MM TODO:  feature to come later
            # remove_event_detect   
        GPIO.cleanup(self.component.bbb_pin_name)  
        self.component.logger.info("GpioDeviceThread - disabled GPIO: %s",self.component.bbb_pin_name) 
                
    def terminate(self):
        self.terminated.set()

'''
GPIO Device Options:
  Pin name: connector and pin used on the BBB - P8_pin# or P9_pin# (required input)
  direction: pin direction - IN or OUT (required input)
  pull_up_down: BBB pin resistor configuration - PUD_OFF (default), PUD_UP or PUD_DOWN
  trigger_edge: which edge to trigger on - RISING, FALLING, BOTH
  initial_value: if GPIO is OUT direction, then this initial value will be set - default = 0
  setup_delay: time in milliseconds to wait after exporting GPIO pin to give udev some time to set file permissions - default = 60 ms, should not use over 1000 ms
  
  Note:  edge triggering, initial value and delay setup will not be implemented in the initial release of this device component (MM)
'''
class GpioDeviceComponent(Component):
    def __init__(self, bbb_pin_name='P8_11', direction='OUT', pull_up_down='PUD_OFF', trigger_edge='RISING', initial_value=0, setup_delay=120):
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        self.pid = os.getpid()
        self.bbb_pin_name = bbb_pin_name      
        self.direction = direction
        self.pull_up_down = pull_up_down
        self.trigger_edge = trigger_edge
        self.initial_value = initial_value
        self.setup_delay = setup_delay  
        self.logger.info("GpioDeviceComponent @%s: %s %s %s ivalue=%d delay=%d [%d]", self.bbb_pin_name, self.direction, self.pull_up_down, self.trigger_edge, self.initial_value, self.setup_delay, self.pid)
        self.gpioDeviceThread = None                    # Cannot manipulate GPIOs in constructor or start threads 
                

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        #self.logger.info("on_clock()[%s]: %s",str(self.pid),now)
        
        if self.gpioDeviceThread == None:
            self.gpioDeviceThread = GpioDeviceThread(self)           
            self.gpioDeviceThread.start()
            self.dataIn_queue.activate()
            self.dataOut_queue.activate()
            
        if self.gpioDeviceThread.isGpioAvailable():
            #gpioReadRequest = self.readGpio.recv_pyobj()
            #self.logger.info("on_readGpio()[%s]: %s",str(self.pid),repr(gpioReadRequest))
            self.gpioDeviceThread.requestGpioRead()
        else:
            self.logger.info("on_readGpio()[%s]: GPIO not available yet",str(self.pid))

    def __destroy__(self):
        self.logger.info("__destroy__")
        
    def on_dataIn_queue(self):                         # Internally triggered op
        dataValue = self.dataIn_queue.recv_pyobj()     # Receive in component data queue
        #self.logger.info("on_dataIn_queue()[%s]: %d",str(self.pid),dataValue) 
        msg = str(dataValue)
        self.reportedData.send_pyobj(msg)
        self.logger.info("on_dataIn_queue(): published GPIO value = %s",msg)
        
    '''def on_readGpio(self):
        if self.gpioDeviceThread.isGpioAvailable():
            gpioReadRequest = self.readGpio.recv_pyobj()
            self.logger.info("on_readGpio()[%s]: %s",str(self.pid),repr(gpioReadRequest))
            self.gpioDeviceThread.requestGpioRead()
        else:
            self.logger.info("on_readGpio()[%s]: GPIO not available yet",str(self.pid))

    def on_writeGpio(self):
        if self.gpioDeviceThread.isGpioAvailable():
            gpioWriteValue = self.writeGpio.recv_pyobj()
            self.logger.info("on_writeGpio()[%s]: %s",str(self.pid),repr(gpioWriteValue))
            self.dataOut_queue.send_pyobj(gpioWriteValue)
            self.logger.info("on_writeGpio(): sending data to GPIO=%s", self.bbb_pin_name)
            self.gpioDeviceThread.requestGpioWrite()  
        else:
            self.logger.info("on_writeGpio()[%s]: GPIO not available yet",str(self.pid))'''