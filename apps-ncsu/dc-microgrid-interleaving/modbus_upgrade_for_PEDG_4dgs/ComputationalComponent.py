'''
Created on Mar 14, 2017

@author: riaps
'''

from riaps.run.comp import Component
import uuid
import os
import time
from collections import namedtuple
from ModbusUartReqRepDevice import CommandFormat,ModbusCommands
import pydevd
from math import acos
pi = 3.141592
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
        
        self.I1mag = 0
        self.I1ph  = 0
        self.phase_shift = {}
        self.counter_shift = 0
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
        
        self.logger.info("ComputationalComponent: %s - starting",str(self.pid)) 
               

    def on_clock(self):
        now = self.clock.recv_pyobj() 
        #self.logger.info("on_clock()[%s]: %s",str(self.pid),str(now))

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
        if self.modbusReqPort.send_pyobj(msg):
             self.ModbusPending += 1
             #self.logger.info('[%d] send req: %s with pending %d' % (self.pid, msg, self.ModbusPending))
             
        '''Receive Response'''
        if self.ModbusPending > 0 :
            msg = self.modbusReqPort.recv_pyobj()
            self.ModbusPending -= 1
            #self.logger.info("on_modbusReqPort()[%s]: %s",str(self.pid),repr(msg))
#        pydevd.settrace(host='192.168.1.102',port=5678)
            I1mag, I1ph, mP, reactivePower = msg
            self.I1mag = 50*I1mag/65535
            self.I1ph = 4*I1ph/65535 - 2
            #self.mP = (mP - 32768)*10
            #self.reactivePower =(reactivePower - 32768)*10
            self.updated = 1
            self.logger.info("received from modbus [%s, %s, %s]", (self.I1mag),(I1ph),(self.I1ph))
            
        self.phase_shift[self.ip] = 0
        
        if (len(self.dataValues) == 2):
            self.logger.info('received 2 point from others')
            self.dataValues[self.ip] = (self.I1mag, self.I1ph)
            
            #MagPhsortedFromMag = sorted( dataValues.values(),  reverse=True )
            IPsortedFromMag = sorted( self.dataValues, key=self.dataValues.__getitem__,  reverse=True )
            
            I1mag_1 = self.dataValues[IPsortedFromMag[0]][0]
            I1mag_2 = self.dataValues[IPsortedFromMag[1]][0]
            I1mag_3 = self.dataValues[IPsortedFromMag[2]][0]
            I1ph_1  = self.dataValues[IPsortedFromMag[0]][1]
            I1ph_2  = self.dataValues[IPsortedFromMag[1]][1]
            I1ph_3  = self.dataValues[IPsortedFromMag[2]][1]
            
            if (I1mag_1 > I1mag_2 + I1mag_3):       
                self.phase_shift[IPsortedFromMag[1]] = pi +I1ph_1
                self.phase_shift[IPsortedFromMag[2]] = pi +I1ph_1
            else :
                beta  = acos((I1mag_1*I1mag_1+I1mag_2*I1mag_2-I1mag_3*I1mag_3)/2/I1mag_1/I1mag_2)
                alpha = acos((I1mag_1*I1mag_1+I1mag_3*I1mag_3-I1mag_2*I1mag_2)/2/I1mag_1/I1mag_3)
                self.phase_shift[IPsortedFromMag[1]] = pi-I1ph_1+I1ph_2-beta;  
                self.phase_shift[IPsortedFromMag[2]] = pi-I1ph_1+I1ph_3+alpha;
                
                
        elif (len(self.dataValues) == 3):
            self.logger.info('received 3 point from others')
            self.dataValues[self.ip] = (self.I1mag, self.I1ph)
            
            #MagPhsortedFromMag = sorted( dataValues.values(),  reverse=True )
            IPsortedFromMag = sorted( self.dataValues, key=self.dataValues.__getitem__,  reverse=True )
            print (IPsortedFromMag)
            I1mag_1 = self.dataValues[IPsortedFromMag[0]][0]
            I1mag_2 = self.dataValues[IPsortedFromMag[1]][0]
            I1mag_3 = self.dataValues[IPsortedFromMag[2]][0]
            I1mag_4 = self.dataValues[IPsortedFromMag[3]][0]
            I1ph_1  = self.dataValues[IPsortedFromMag[0]][1]
            I1ph_2  = self.dataValues[IPsortedFromMag[1]][1]
            I1ph_3  = self.dataValues[IPsortedFromMag[2]][1]
            I1ph_4  = self.dataValues[IPsortedFromMag[3]][1]
            
            if (I1mag_1 > I1mag_2 + I1mag_3 + I1mag_4):       
                self.phase_shift[IPsortedFromMag[1]] = pi+I1ph_1 
                self.phase_shift[IPsortedFromMag[2]] = pi+I1ph_1
                self.phase_shift[IPsortedFromMag[3]] = pi+I1ph_1
            else :
                self.phase_shift[IPsortedFromMag[0]] = 0
                self.phase_shift[IPsortedFromMag[3]] = pi+I1ph_1
                (phaseShift2, phaseShift3) = self.TriangleAlgorithm(I1mag_1-I1mag_4, I1ph_1, I1mag_2, I1ph_2, I1mag_3, I1ph_3)
                #beta  = acos((I1mag_1*I1mag_1+I1mag_2*I1mag_2-I1mag_3*I1mag_3)/2/I1mag_1/I1mag_2)
                #alpha = acos((I1mag_1*I1mag_1+I1mag_3*I1mag_3-I1mag_2*I1mag_2)/2/I1mag_1/I1mag_3)
                self.phase_shift[IPsortedFromMag[1]] = phaseShift2; 
                self.phase_shift[IPsortedFromMag[2]] = phaseShift3;
            
            
        self.dataValues.clear()
            
        self.counter_shift = self.phase_shift[self.ip]*40000/2/pi
            
        print (self.phase_shift)
            
        OMEGAToModbus = int( round (self.counter_shift))
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
                
        self.values = [status, OMEGAToModbus, eToModbus]
        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS,0,3,self.values,self.defaultNumOfDecimals,self.signedDefault)
		
        msg = self.command  
        
        if self.modbusReqPort.send_pyobj(msg):
            self.ModbusPending += 1
            #self.logger.info('[%d] send req: %s with pending %d' % (self.pid, msg, self.ModbusPending))
             
        '''Receive Response'''
        if self.ModbusPending > 0 :
            msg = self.modbusReqPort.recv_pyobj()
            self.ModbusPending -= 1
         
        
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
            msg = (self.ip, self.I1mag, self.I1ph)
            self.thisReady.send_pyobj(msg)
        
        self.updated = 0        
        #self.logger.info("secondary controller update: fre %f and ang_diff %f", self.frequency, self.VoltageAngleDiff)
           

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
        otherId, otherValue_I1mag, otherValue_I1ph = msg #otherValue_ReactivePower
        if otherId != self.ip: #self.uuid was used for general operation
            self.dataValues[otherId] = (otherValue_I1mag, otherValue_I1ph)
            self.logger.info("data from %s: mag=%s and  phase=%s", str(otherId), str(otherValue_I1mag),str(otherValue_I1ph))
    
    
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
        
        if (self.VoltageRegulateDG == 1):   
            self.VoltageMagDiff = data['mag_diff']
            self.VoltageAngleDiff = data['angle_diff']
        
    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)
        
    def TriangleAlgorithm(self, I1mag_1, I1ph_1, I1mag_2, I1ph_2, I1mag_3, I1ph_3):
        
        beta  = acos((I1mag_1*I1mag_1+I1mag_2*I1mag_2-I1mag_3*I1mag_3)/2/I1mag_1/I1mag_2)      
        alpha = acos((I1mag_1*I1mag_1+I1mag_3*I1mag_3-I1mag_2*I1mag_2)/2/I1mag_1/I1mag_3)
        phaseShift2 = pi-I1ph_1+I1ph_2-beta;  
        phaseShift3 = pi-I1ph_1+I1ph_3+alpha;
        return (phaseShift2, phaseShift3)
        
        
        
        
        
        
        
        
        
        