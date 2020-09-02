'''
    Example controller that uses GridlabD device
'''

from riaps.run.comp import Component
import os
import time
import random
from riaps.run.exc import PortError

class Controller(Component):
    def __init__(self, sensor,actuator,priority):
        super(Controller, self).__init__()
        self.logger.info("Controller.__init__ ()")
        # Obj - Object name, Attr - Attribute it is interested in, Unit - Unit of Measurement
        self.sObj,self.sAttr,self.sUnit = sensor.split('.')
        self.aObj,self.aAttr,self.aUnit = actuator.split('.')
        self.control_counter = 0
        self.control_period = 20    # random.randin t(20,30)
        self.control_duty = 10      # random.randint(10,20)
        self.pending = 0 
        self.first = True
        self.lastValue = None
        self.global_status = {} # dictionary containing information about priority, switch, actor uuid and send time stamps of other controllers
        self.node_state = {} # dictionary containing the last known node state, the actor uuid of all peers.
        self.status = '' # initial switch status is unknown
        self.priority = priority
        self.thresh_u = 2.59e06 # upper threshold for load
        self.thresh_l = 2.4e06 # lower threshold for load
        self.retrycountu = 0
        self.retrycountl = 0
        self.maxretry = 5 # no. of simulation steps to wait for the grid to stabilize before taking control action
        self.uuid = ""
        self.timeout = 120 
#         self.total_count = total_count
#         self.join_count = 0
        self.wait = 0
        self.maxwait = 3 # no. of simulation steps to wait for all peers to connect
        self.waitcounth = 0
        self.waitcountl = 0
        self.waittimeout = 10 # waiting timeout for peers to issue control commands
    
    def handleActivate(self):
        self.logger.info("handleActivate()")
        self.uuid = self.getUUID()
        self.trigger.setDelay(120.0)
        self.trigger.launch()
        
    def on_trigger(self):
        self.logger.info("on_trigger()")
        _discard = self.trigger.recv_pyobj()
#         self.trigger.halt()
#         self.updatestatus.send_pyobj({self.priority : self.status})
        if self.pending == 0:
            
            if self.status == '':
                msg = ['query', (self.aObj,'phase_A_state',self.aUnit)] # query the last known switch status
            else: 
                msg = ['sub', (self.sObj,self.sAttr,self.sUnit)] # send the initial subscription request
#             self.logger.info("before sending sub req")
            try:
                
                self.command.send_pyobj(msg)
            # handle exceptions such as request timeout
            except PortError as e:
                self.logger.info("send exception : error code %s" % e.errno)
                self.trigger.setDelay(30.0)
                self.trigger.launch()
            # if the send operation is successful
            else:
                self.logger.info("on_trigger: msg=%s" % str(msg))
                self.pending += 1
                if not self.status == '':
                    self.updatestatus.send_pyobj({self.priority : (self.status, self.uuid)})
                    time.sleep(0.5)
                    self.sendnodeinfo.send_pyobj({self.uuid : (self.aObj, 'on')})
                    self.trigger.halt()
                else:
                    self.trigger.setDelay(30.0)
                    self.trigger.launch()
    
    # handler for reply received from device component
    def on_command(self):
        _msg = self.command.recv_pyobj()            
        self.logger.info("on_command(): resp = %s" % str(_msg))
        if _msg[0] == self.aObj: # if query item was the switch status
            switch = str(_msg[2])
            if switch == 'CLOSED':
                self.status = '1'
            elif switch == 'OPEN':
                self.status = '0'
        else:
            self.trigger.halt()
        self.pending -= 1
#         self.updatestatus.send_pyobj({self.priority : (self.status, self.uuid)})
#         time.sleep(0.5)
#         self.sendnodeinfo.send_pyobj({self.uuid : (self.aObj, 'on')})
    
    def control(self):  
        value = '1' if self.control_counter < self.control_duty else '0'
        self.control_counter = (self.control_counter + 1) % self.control_period
        return value
    
    # control logic algorithm
    def controlswitch(self, power):
        # calculate the number of peers that are connected and are in "on" state
        counton = sum(1 for tup in self.node_state.values() if tup[1] == "on")
        # wait till switch info is received from all "on" pairs or till timeout occurs
        if len(self.global_status) >= counton or self.wait >= self.maxwait:
            # if the real part of the load exceeds the threshold 
            if power > self.thresh_u:
                self.logger.info("Power consumption threshold exceeded !!!!")
                wait = False
                # search if a lower priority switch is present that is still connected
                for key,value in self.global_status.items():
                    self.logger.info("value = %s" % str(value))
                    if not self.node_state[value[1]][1] == "on":
                        continue
                    
                    if key > self.priority and value[0]== '1':
                        self.logger.info("Waiting for lower priority switch")
                        wait = True # lower priority switch exists
                        break
                if wait:
                    # wait for lower priority switch until timeout
                    if self.waitcounth >= self.waittimeout:
                        self.waitcounth = 0
                        val = '0'
                        self.logger.info("lower priority switch not responding, timeout occurred")
                        self.wait = 0
                    else:
                        # wait till timeout occurs
                        val = self.status
                        self.waitcounth +=1
    
                else:
                    # the given switch is the current lowest priority switch
                    self.waitcounth = 0
                    # wait for few instants for simulation to stabilize
                    if self.retrycountu >= self.maxretry:
                        val = '0'
                        self.retrycountu = 0
                        self.wait = 0 
                    else:
                        self.retrycountu += 1
                        val = self.status
                        self.logger.info("waiting for actuation to take effect")
            
            # if the real power goes below a threshold apply same logic but in reverse order of priority            
            elif power < self.thresh_l:
                self.logger.info("Power consumption lowered")
                wait = False
                for key,value in self.global_status.items():
                    
                    if self.node_state[value[1]][1] is "off":
                        continue
                    if key < self.priority and value[0] == '0':
                        self.logger.info("Waiting for higher priority switch")
                        wait = True
                        break
                if wait:
                    if self.waitcountl >= self.waittimeout:
                        self.waitcountl = 0
                        val = '1'
                        self.logger.info("higher priority switch not responding, timeout occurred")
                        self.wait = 0
                    else:
                        val = self.status
                        self.waitcountl +=1
                    
    
                else:
                    self.waitcountl = 0
                    if self.retrycountl >= self.maxretry:
                        val = '1'
                        self.retrycountl = 0
                        self.wait = 0
                    else:
                        self.retrycountl += 1
                        val = self.status
                        self.logger.info("waiting for actuation to take effect")
                
            else:
                val = self.status
                
        elif self.wait < self.maxwait:
            self.wait += 1
            msg = []
            for uuid in self.node_state.keys():
                if self.node_state[uuid][1]== 'on':
                    if uuid not in [x for v in self.global_status.values() for x in v]:
                        msg.append(uuid)
            if len(msg) > 0:
                self.logger.info("requesting status from %s" % str(msg))           
                self.resendinfo.send_pyobj(msg) #request node to resend info
            val = self.status
            
#         elif len(self.global_status) == 0 and self.wait == self.maxwait:
#             self.logger.info("node %s seems to be isolated, taking safety measures.." % self.aObj)
#             if power > self.thresh_u:
#                 self.logger.info("Power consumption threshold exceeded !!!!")
#                 val = '0'
        
        # waiting for sll connected peers to send their switch statuses    
        else:
            self.logger.info("global_status: %d, node_state: %d" % (len(self.global_status), counton))
            val = self.status
            
        return val
    
    
    # handler for measurement data received from simulation via device component    
    def on_data(self):
        msg = self.data.recv_pyobj()
        self.logger.info("on_data(): recv=%s" % str(msg))
#         self.updatestatus.send_pyobj({self.priority : (self.status, self.uuid)})
        time.sleep(0.5)
#         value = self.control()
#         if value != self.lastValue:
#             while self.pending > 0: self.on_command()
#             cmd = ['pub', (self.aObj,self.aAttr,value,self.aUnit)]
#             self.command.send_pyobj(cmd)
#             self.pending += 1
#             self.lastValue = value
        power = msg[2] # get measurement value
        self.logger.info(str(power))
#         if power.real > self.threshold:
        value =self.controlswitch(power.real) # calculate the control action
        # send new switch information if any change occurs
        if value != self.status:
            while self.pending > 0: self.on_command()
            cmd = ['pub', (self.aObj,self.aAttr,value,self.aUnit)]  
            self.logger.info("%s" % str(cmd))
            try:
                self.command.send_pyobj(cmd)
            except PortError as e:
                self.logger.info("send exception : error code %s" % e.errno)
            else:    
                self.pending += 1
                self.status = value
            self.updatestatus.send_pyobj({self.priority : (self.status, self.uuid)})
        
    
    # handler for switch status received from peers        
    def on_receivestatus(self):
        msg = self.receivestatus.recv_pyobj()
        self.logger.info( "on_receivestatus(): %s" % str(msg))
        send_time = self.receivestatus.get_sendTime()
        priority = list(msg.keys())
        priority = int(priority[0])
        if priority == self.priority:
            pass
        else:
            self.global_status[priority] = (msg[priority][0], msg[priority][1], send_time)
            self.logger.info("received information on other switches")
    
    # peer state change handler        
    def handlePeerStateChange(self, state, uuid):
        change = False
        # discard own messages
        if uuid is not self.uuid:
            self.logger.info("peer %s state changed to %s" % (uuid, state))
            # if the peer is already sent its state before then modify the same entry
            if uuid in self.node_state:
                if not self.node_state[uuid][1] == state:
                    self.logger.info("Controller node for %s is %s" % (self.node_state[uuid][0], state))
                    change = True
                if change:
                    self.node_state[uuid] = (self.node_state[uuid][0], state)
                self.logger.info("end of peer state")
            # new peer discovered
            else:
                self.logger.info("Discovered new node %s" % uuid)
                self.node_state[uuid] = ("unknown", state)
    
    # handler for node state messages from peers            
    def on_recvnodeinfo(self):
        info = self.recvnodeinfo.recv_pyobj()
#         self.logger.info("Received node state message %s" % str(info))
        keyid = list(info.keys())[0]
#         self.logger.info("keyid = %s" % keyid)
        # discard messages from itself
        if not info[keyid][0] == self.aObj:
            self.logger.info("Received status message %s" % str(info))
            self.node_state[keyid] = (info[keyid][0], info[keyid][1])
#             self.logger.info(str(self.node_state))


    # timer to periodically check if any switch information is old and request resend        
    def on_check(self):
        now = self.check.recv_pyobj()
        self.logger.info("checking for stale values")
        msg = []
        for key,value in list(self.global_status.items()):
#             self.logger.info("entry: %s" % str(value))
#             self.logger.info("difference: %f" % (now - value[2]))
            if now - value[2] > self.timeout:
                self.logger.info("entry %s:%s is stale" % (str(key), str(value)))
                self.node_state[value[1]] = (self.node_state[value[1]][0],"unknown")
                msg.append(value[1])
                
            if len(msg)> 0:
                self.logger.info("requesting status from %s" % str(msg))
                self.resendinfo.send_pyobj(msg)
            
#     def on_ready(self):l
#         msg = self.ready.recv_pyobj()
#         self.logger.info("device up")
#         self.trigger.launch()
    
    # Network Interface change handler. If NIC is down then the controller tries to turn off the switch as a safety measure.
    def handleNICStateChange(self, state):
        self.logger.info("%s NIC state %s" % (self.aObj, state))
        if state == 'off':
            cmd = ['pub', (self.aObj,self.aAttr,'0',self.aUnit)]
            try:
                self.command.send_pyobj(cmd)
            except PortError as e:
                    self.logger.info("send exception : error code %s" % e.errno)
            else:    
                self.pending += 1
                self.status = '0'
    
    
    # handler when a resend request arrives            
    def on_recvresendinfo(self):
        info = self.recvresendinfo.recv_pyobj()
        if self.uuid in info:
            self.logger.info("%s resending status message" % self.aObj)
            self.updatestatus.send_pyobj({self.priority : (self.status, self.uuid)})
        
    def __destroy__(self):
        self.logger.info("Controller.__destroy__()")                         
