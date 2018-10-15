'''
Created on Apr 4, 2017

@author: riaps
'''
from riaps.run.comp import Component
import os


class ToggleGpioComponent(Component):
    def __init__(self):
        super().__init__()
        self.pid = os.getpid()
        self.setValue = 0  # default off
        self.logger.info("ToggleGpioComponent: %s - starting",str(self.pid))

    def on_currentGpioValue(self):
        msg = self.currentGpioValue.recv_pyobj() # Receive DataValue
        self.logger.info("on_currentGpioValue()[%s]: GPIO value=%s",str(self.pid),repr(msg))
        
    def on_toggle(self):
        msg = self.toggle.recv_pyobj()
        self.logger.info("on_toggle()[%s]: %s",str(self.pid),repr(msg))
        if self.setValue == 0:
            self.setValue = 1  
        else:
            self.setValue = 0
                
        self.writeGpioValue.send_pyobj(self.setValue)
        self.logger.info("on_toggle()[%s]: send write request, setValue=%d",str(self.pid), self.setValue)
        
    def on_readValue(self):
        msg = self.readValue.recv_pyobj()
        self.logger.info("on_readValue()[%s]: %s",str(self.pid),repr(msg))   
        msg = "Read"             
        self.pollGpioValue.send_pyobj(msg)
        self.logger.info("on_readValue()[%s]: send read request",str(self.pid))
        
