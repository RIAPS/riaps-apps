# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import capnp
import timersync_capnp
from enum import Enum


class AppState(Enum):
    INIT = 0        #Just started up, isn't yet trying to synchronize
    SYNC = 1        #Currently waiting until the synchronization point
    RUNNING = 2     #Synchronization point passed, all 'periodic' ports roughly in sync 

# riaps:keep_import:end

class TimerComp(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(TimerComp, self).__init__()
        
        self.state = AppState.INIT
        self.logger.info("TimerComp started!")
        
# riaps:keep_constr:end

# riaps:keep_clock:begin
    def on_periodic(self):
        currTime = self.periodic.recv_pyobj()
        
        if self.state is AppState.INIT:
            #Calculate how long to delay i.e. find next multiple of 10 seconds in Unix time
            #The '+2.0' is there to ensure the 1s periodic timer's internal thread will
            #reach an inactive state
            delay = (int(currTime+2.0)//10 + 1)*10 - currTime
            
            #Set and start sporadic timer
            self.syncDelay.setDelay(delay)
            self.syncDelay.launch()
            
            #Component is now waiting to synchronize, stop the periodic timer
            self.periodic.halt()
            self.state = AppState.SYNC
            
            self.logger.info("Delaying %s seconds..." % delay)
                 
            
        elif self.state is AppState.RUNNING:
            # Do synchronized task here
            self.logger.info("Synchronized timer: %s" % currTime)
        
        
# riaps:keep_clock:end

# riaps:keep_syncdelay:begin
    def on_syncDelay(self):
        currTime = self.syncDelay.recv_pyobj()
        
        
        #All TimerComp instances reach this point at the same time.
        if self.state is AppState.SYNC:     
            #Restart periodic timer
            self.periodic.launch()
            
            self.state = AppState.RUNNING
            self.logger.info("SYNCHRONIZED. Starting synchronized timer...")
            
# riaps:keep_syncdelay:end

# riaps:keep_impl:begin

# riaps:keep_impl:end