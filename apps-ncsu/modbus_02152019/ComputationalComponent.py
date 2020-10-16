'''
Created on Mar 14, 2017

@author: riaps
'''
import zmq
from riaps.run.comp import Component
from riaps.run.exc import PortError
import uuid
import os
import time
from collections import namedtuple
from ModbusUartReqRepDevice import CommandFormat,ModbusCommands
import pydevd
import logging


''' Enable debugging to gather timing information on the code execution'''
debugMode = False

RegSet = namedtuple('RegSet', ['idx', 'value'])
InputRegs = namedtuple('InputRegs', ['outputCurrent','outputVolt','voltPhase','time'])

'''For Inverter control'''
HoldingRegs = namedtuple('HoldingRegs',['unused', 'startStopCmd', 'power','reactive_power'])
'''For RIAPS future
1.start/stop, 2.power command, 3. frequency shift from secondary control, 4. voltage magnitude shift from secondary control.
HoldingRegs = namedtuple('HoldingRegs',['startStopCmd', 'powerCmd', 'freqShift', 'voltMagShift']) 
'''
 
class ComputationalComponent(Component):
    def __init__(self, Ts, ip):
        super().__init__()
#        pydevd.settrace(host='192.168.1.103',port=5678)
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.inputRegs = InputRegs(RegSet(0,45),RegSet(1,56),RegSet(2,78),RegSet(3,91))
        self.holdingRegs = HoldingRegs(RegSet(0,0),RegSet(1,0),RegSet(2,0),RegSet(3,0))
        
        
        self.ip = ip
        self.ModbusPending = 0
        self.updated = 0
        self.display_counter = 0
        self.display_list = []
        self.display_counter_Q = 0
        '''Setup Commands  - for modbus'''
        self.readOrWrite = 0
        self.defaultNumOfRegs = 1
        self.dummyValue = [0]
        self.defaultNumOfDecimals = 0
        self.signedDefault = False
        
        '''algorithm variables - local measurement from modbus'''
        self.frequency  = 0
        self.voltageMag = 0
        self.mP  = 0
        self.reactivePower = 0
        
        '''algorithm variables - secondary control variable'''
        self.sum_OMEGASecondaryControlVariable = 0.0;
        self.OMEGASecondaryControlVariable = 0.0
        self.eSecondaryControlVariable = 0.0
 
        '''algorithm variables - parameters'''
        self.start_stop     = 0
        self.islanding_mode = 0
        self.sec_en = 0
        self.angle_en = 0
        self.Ts  = Ts
        
        ''' variables for voltage regulation DG '''
        self.VoltageRegulateDG = 0
        self.VoltageMagDiff = 0
        self.VoltageAngleDiff = 0
        
        if (self.ip == 112):
            self.VoltageRegulateDG = 1
        self.dataValues = { }
        
        self.debug_counter = 0	
        
        self.logger.info("ComputationalComponent: %s - starting" % str(self.pid)) 
               

    def on_clock(self):
        on_clock_start = time.time()
        now = self.clock.recv_pyobj() 
        
        if debugMode:
            self.logger.info("on_clock()[%s]: %s",str(self.pid),str(now))

        '''Request:  Commands to send over Modbus - one command used at a time'''
        
        '''Read/Write (holding only) a single register'''
        #self.command = CommandFormat(ModbusCommands.READ_INPUTREG,self.inputRegs.time.idx,self.defaultNumOfRegs,self.dummyValue,self.defaultNumOfDecimals,self.signedDefault) 
        #self.command = CommandFormat(ModbusCommands.READ_HOLDINGREG,self.holdingRegs.startStopCmd.idx,self.defaultNumOfRegs,self.dummyValue,self.defaultNumOfDecimals,self.signedDefault)
        #self.values = [83]
        #self.command = CommandFormat(ModbusCommands.WRITE_HOLDINGREG,self.holdingRegs.power.idx,self.defaultNumOfRegs,self.values,self.defaultNumOfDecimals,self.signedDefault)
   
        
        '''Read all input registers'''
        numRegsToRead = len(self.inputRegs)
        self.command = CommandFormat(ModbusCommands.READMULTI_INPUTREGS,self.inputRegs.outputCurrent.idx,numRegsToRead,self.dummyValue,self.defaultNumOfDecimals,self.signedDefault)
            
        msg = self.command  
        on_clock_modbus_measurement_start = time.time()     

        repMsg = self.sendModbusRequest(self.command)
        
        # Check if the Modbus Response is valid
        #if repMsg != -1 and repMsg != 999 and repMsg != -9999:
        if repMsg != None:
            on_clock_modbus_measurement_end_and_algorithm_start = time.time() 
            frequency, voltageMag, mP, reactivePower = repMsg
            self.frequency = 365 + 25*frequency/65535
            self.voltageMag = 250 + 250*voltageMag/65535
            self.mP = (mP - 32768)*10
            self.reactivePower =(reactivePower - 32768)*10
            self.updated = 1
        else:
            self.logger.info("Modbus either not ready or no value read")

        if (len(self.dataValues) != 0):
            sum_ReactivePower = 0.0
            self.sum_OMEGASecondaryControlVariable = 0;
        
            if self.display_counter_Q == 20:
                print ("self Q %s and other Q %s" %( str(self.reactivePower),str(self.dataValues)))
                self.display_counter_Q = 0
            self.display_counter_Q = self.display_counter_Q + 1
            
            if debugMode:
                self.logger.info("self Q %s and other Q %s", str(self.reactivePower),str(self.dataValues))
            #for other_id, (otherValue_OMEAG, otherValue_ReactivePower) in self.dataValues.items():
            for (otherValue_OMEAG, otherValue_ReactivePower) in self.dataValues.values():
                self.sum_OMEGASecondaryControlVariable += (self.OMEGASecondaryControlVariable - otherValue_OMEAG)
                sum_ReactivePower += (self.reactivePower - otherValue_ReactivePower)  
                #self.logger.info("calculation of %s: f diff %s and self Omega %s and other Omega %s and sum Omega %s", str(self.ip), str((self.frequency-376.9911184)),str(self.OMEGASecondaryControlVariable),str(otherValue_OMEAG),str(self.sum_OMEGASecondaryControlVariable))
            
            self.dataValues.clear()
                
            der_OMEGASecondaryControlVariable = ( (self.frequency-376.9911184)/6 * self.sec_en + self.sum_OMEGASecondaryControlVariable*4) * self.Ts*2 - 0.001*self.VoltageAngleDiff*self.VoltageRegulateDG*self.angle_en*self.sec_en* self.Ts/0.05
            
            
            #der_ReactivePower = ( (self.voltageMag-391)*self.VoltageRegulateDG * 1  + 0.001*(1-self.VoltageRegulateDG)*sum_ReactivePower) * self.Ts * self.sec_en
            
            der_ReactivePower = ( (-self.VoltageMagDiff)*self.VoltageRegulateDG /32.0  + 0.001*(1-self.VoltageRegulateDG)*sum_ReactivePower) * self.Ts * self.sec_en
            
            self.OMEGASecondaryControlVariable -= der_OMEGASecondaryControlVariable
            self.eSecondaryControlVariable -= der_ReactivePower
            
            if (self.sec_en == 0):
                self.OMEGASecondaryControlVariable = 0
                self.eSecondaryControlVariable = 0
                
            '''Write all holding registers'''       
            OMEGAToModbus = int( round ( ( self.OMEGASecondaryControlVariable+25  )*65535/50))
            if (OMEGAToModbus > 65535):
                OMEGAToModbus = 65535
            elif (OMEGAToModbus < 0):
                OMEGAToModbus = 0
                
            eToModbus = int( round ( (self.eSecondaryControlVariable+50 )*65535/100 ) )
            if (eToModbus > 65535):
                eToModbus = 65535
            elif (eToModbus < 0):
                eToModbus = 0
            
            status = self.start_stop
            
            if (self.islanding_mode == 1):
                status = status + 2
            
            if (self.sec_en == 1):
                status = status + 4

            if debugMode:
                self.logger.info("modbus command : %s",str(status))
            
            self.values = [status, OMEGAToModbus, eToModbus]
            self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS,0,3,self.values,self.defaultNumOfDecimals,self.signedDefault)
            
            on_clock_modbus_command_start = time.time() 

            repMsg = self.sendModbusRequest(self.command)
        
            # Check if the Modbus Response is valid
            #if repMsg == -1 or repMsg == -9999:
            if repMsg == None:
                self.logger.info("Modbus either not ready")

            on_clock_modbus_command_end = time.time() 
        
            #self.debug_counter = self.debug_counter +1
            
            self.updated = 1
        
        '''
        if (self.display_counter == 20):
            print (self.display_list)
            self.display_list = []
            self.display_counter = 0
            self.debug_counter =0
            self.updated = 1
        self.display_list.append((self.display_counter, self.debug_counter, self.frequency, self.sum_OMEGASecondaryControlVariable, self.OMEGASecondaryControlVariable))
        self.display_counter = self.display_counter+1
        '''

                
        if(self.updated):
            now = time.time()
            msg = (self.ip, now, self.OMEGASecondaryControlVariable, self.reactivePower, self.eSecondaryControlVariable, (self.OMEGASecondaryControlVariable+self.mP*0)* self.sec_en)
            self.thisReady.send_pyobj(msg)
        
        self.updated = 0        
        #self.logger.info("secondary controller update: fre %f and ang_diff %f", self.frequency, self.VoltageAngleDiff)
           
        on_clock_end = time.time()
        '''
        try:  

            time_modbus_mea = on_clock_modbus_measurement_end_and_algorithm_start - on_clock_modbus_measurement_start
            time_modbus_com = on_clock_modbus_command_end - on_clock_modbus_command_start
            time_all  = on_clock_end - on_clock_start
            time_algorithm  = time_all - time_modbus_mea - time_modbus_com
            
            filename = "t_cal"
            file = open(filename, "a")
            file.write(str(time_all)+'   '+str(time_modbus_mea)+'   '+str(time_modbus_com)+'   '+str(time_algorithm)+'\n')
            file.close()
            #self.logger.info("t cal: total %f, m_m %f, m_c %f, al %f", time_all, time_modbus_mea, time_modbus_com, time_algorithm)
        except UnboundLocalError:
            pass
        '''
        
        '''    
        if self.command.commandType == ModbusCommands.READ_INPUTREG or self.command.commandType == ModbusCommands.READ_HOLDINGREG:
            logMsg = "Register " + str(self.command.registerAddress) + " value is " + str(msg)
        elif self.command.commandType == ModbusCommands.READMULTI_INPUTREGS or self.command.commandType == ModbusCommands.READMULTI_HOLDINGREGS:
            logMsg = "Register " + str(self.command.registerAddress) + " values are " + str(msg)
        elif self.command.commandType == ModbusCommands.WRITE_HOLDINGREG:
            logMsg = "Wrote Register " + str(self.command.registerAddress)
        elif self.command.commandType == ModbusCommands.WRITEMULTI_HOLDINGREGS:
            logMsg = "Wrote Registers " + str(self.command.registerAddress) + " to " + str(self.command.registerAddress + self.command.numberOfRegs - 1)
            
        self.tx_modbusData.send_pyobj(logMsg)  # Send log data
        '''
    
    def on_nodeReady(self):
        msg = self.nodeReady.recv_pyobj()  # Receive (actorID,timestamp,value)
        #self.logger.info("on_otherReady():%s",str(msg))
        otherId,otherTimestamp,otherValue_OMEAG,otherValue_ReactivePower,otherValue_e, otherValue_Omega_P = msg #otherValue_ReactivePower
        if otherId != self.ip: #self.uuid was used for general operation
            self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower)   
            '''
            if self.ip == 111 :
                if otherId  == 112:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower)
            if self.ip == 112 :
                if otherId  == 111 or otherId  == 113:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower)
            if self.ip == 113 :
                if otherId  == 112 or otherId  == 114:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower)
            if self.ip == 114 :
                if otherId  == 113:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower)     
            '''        
        if debugMode:
            self.logger.info("data from %s: %s and self f %s", str(otherId), str(otherValue_OMEAG),str(self.frequency))
    
    
    def on_rx_phasorData(self):
        data = self.rx_phasorData.recv_pyobj()  
        if ( data['DIGITALS'] == 1 ):
            self.start_stop     = 1 
            self.islanding_mode = 0   
        elif ( data['DIGITALS'] == 2 ):
            self.start_stop     = 0 
            self.islanding_mode = 1 
        elif ( data['DIGITALS'] == 3 ):
            self.start_stop     = 1 
            self.islanding_mode = 1 
        else:
            self.start_stop     = 0 
            self.islanding_mode = 0
        
        if ( data['DIGITALS1'] == 1 ):
            self.sec_en   = 1 
            self.angle_en = 0              
        elif ( data['DIGITALS1'] == 2 ):
            self.sec_en   = 0 
            self.angle_en = 1 
        elif ( data['DIGITALS1'] == 3 ):
            self.sec_en   = 1 
            self.angle_en = 1 
        else:
            self.sec_en   = 0 
            self.angle_en = 0 
            
        #self.islanding_mode = 1 - data['DIGITALS']
        #self.sec_en = data['DIGITALS1']
        if debugMode:
            self.logger.info("Receive start/stop command from 110: %s",str(self.start_stop))
        if (self.VoltageRegulateDG == 1):   
            self.VoltageMagDiff = data['mag_diff']
            self.VoltageAngleDiff = data['angle_diff']
    
    '''
    def sendModbusRequest(self, requestMsg):
        # Init to invalid response value
        responseMsg = -1 
        try:
            if debugMode:
                self.logger.info("Send Modbus Request")
            if self.modbusReqPort.send_pyobj(requestMsg):
                responseMsg = self.modbusReqPort.recv_pyobj()
                if debugMode:
                    self.logger.info("Receive Modbus Response[%s]: %s",str(self.pid),repr(responseMsg))
        except zmq.error.ZMQError as e:
            if e.errno == zmq.EFSM:
                self.logger.info("EFSM error found")
            else:
                raise
                
        return responseMsg
    '''
    
    def sendModbusRequest(self, requestMsg):
        # Init to invalid response value
        rep = None
        try:
            self.modbusReqPort.send_pyobj(requestMsg)
            rep = self.modbusReqPort.recv_pyobj()
        except PortError as e:
            self.logger.info("on_clock:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_clock: port error received")
        #self.logger.info('[%d] recv rep: %s' % (self.pid,rep))
        return rep
        
    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)
        
        
        