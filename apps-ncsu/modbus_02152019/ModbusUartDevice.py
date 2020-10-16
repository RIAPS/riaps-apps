'''
Created on Mar 14, 2017

@author: riaps

This module utilizes the MinimalModbus (which utilizes pySerial).
Both need to be installed in the development environment.
    $ sudo pip3 install minimalmodbus  (which should install pySerial)
'''

from riaps.run.comp import Component
import logging
import os
import serial
from serialModbusLib.serialModbusComm import SerialModbusComm,PortConfig
from collections import namedtuple
from enum import Enum
#import pydevd


class ModbusCommands(Enum):
    READ_BIT = 1
    READ_INPUTREG = 2
    READ_HOLDINGREG = 3
    READMULTI_INPUTREGS = 4
    READMULTI_HOLDINGREGS = 5
    WRITE_BIT = 6
    WRITE_HOLDINGREG = 7
    WRITEMULTI_HOLDINGREGS = 8

CommandFormat = namedtuple('CommandFormat', ['commandType','registerAddress','numberOfRegs','values','numberOfDecimals','signedValue'])
    
class ModbusUartDevice(Component):
    def __init__(self,slaveaddress=0,port="ttyO1",baudrate=19200,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,serialTimeout=0.05): # defaults for Modbus spec
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        self.pid = os.getpid()
        self.port_config = PortConfig("/dev/" + port, baudrate, bytesize, parity, stopbits, serialTimeout)        
        self.slaveAddressDecimal = slaveaddress
        self.modbus = SerialModbusComm(self,self.slaveAddressDecimal,self.port_config)
        self.modbusReady = False
        self.logger.info("Modbus settings %d @%s:%d %d%s%d [%d]", self.slaveAddressDecimal,self.port_config.portname,self.port_config.baudrate,self.port_config.bytesize,self.port_config.parity,self.port_config.stopbits,self.pid)       

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.logger.info("on_clock()[%s]: %s",str(self.pid),now)        
        
        if self.modbusReady == False:
            self.modbus.startModbus()
#            pydevd.settrace(host='192.168.1.102',port=5678)
            self.modbusReady = True
                    
    def __destroy__(self):
        self.logger.info("__destroy__")
        self.modbus.stopModbus()
        
    '''    
    Receive a Modbus command request.  Process command and send back response.
    '''
    def on_modbusRepPort(self):                
        '''Request Received'''         
        commandRequest = self.modbusRepPort.recv_pyobj()     
        #self.logger.info("on_modbusRepPort()[%s]: %s",str(self.pid),commandRequest) 

        self.unpackCommand(commandRequest)
        responseValue = -1  # invalid response 
        if self.modbusReady == True:
            responseValue = self.sendModbusCommand()
        
        #wait until get the response or timeout
        '''Send Results'''
        self.modbusRepPort.send_pyobj(responseValue)
#        pydevd.settrace(host='192.168.1.102',port=5678)
        #self.logger.info("on_modbusRepPort()[%s]: %s,",str(self.pid),responseValue)        
        
    def unpackCommand(self,rxCommand):
        self.commmandRequested = rxCommand.commandType
        self.registerAddress = rxCommand.registerAddress
        self.numberOfRegs = rxCommand.numberOfRegs
        self.numberOfDecimals = rxCommand.numberOfDecimals
        self.signedValue = rxCommand.signedValue
        self.values = rxCommand.values
        
    def sendModbusCommand(self):
        value = 999  # large invalid value
        
        if self.commmandRequested == ModbusCommands.READ_INPUTREG:
            value = self.modbus.readInputRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s", ModbusCommands.READ_INPUTREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue))
        elif self.commmandRequested == ModbusCommands.READ_HOLDINGREG:
            value = self.modbus.readHoldingRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
            self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s", ModbusCommands.READ_HOLDINGREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue))
        elif self.commmandRequested == ModbusCommands.READMULTI_INPUTREGS:
            value = self.modbus.readMultiInputRegValues(self.registerAddress, self.numberOfRegs)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d", ModbusCommands.READMULTI_INPUTREGS.name,self.registerAddress,self.numberOfRegs)
        elif self.commmandRequested == ModbusCommands.READMULTI_HOLDINGREGS:
            value = self.modbus.readMultiHoldingRegValues(self.registerAddress, self.numberOfRegs)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d", ModbusCommands.READMULTI_HOLDINGREGS.name,self.registerAddress,self.numberOfRegs)
        elif self.commmandRequested == ModbusCommands.WRITE_HOLDINGREG:
            self.modbus.writeHoldingRegister(self.registerAddress, self.values[0], self.numberOfDecimals, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, value=%d, numberOfDecimals=%d, signed=%s",ModbusCommands.WRITE_HOLDINGREG.name,self.registerAddress,self.values[0],self.numberOfDecimals,str(self.signedValue))
        elif self.commmandRequested == ModbusCommands.WRITEMULTI_HOLDINGREGS:
            self.modbus.writeHoldingRegisters(self.registerAddress, self.values)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d",ModbusCommands.WRITEMULTI_HOLDINGREGS.name,self.registerAddress)
            #self.logger.info("ModbusUartDevice: Values - %s", str(self.values).strip('[]'))        
        return value
        
