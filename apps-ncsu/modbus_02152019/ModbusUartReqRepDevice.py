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
import time


''' Enable debugging to gather timing information on the code execution'''
debugMode = False

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

class ModbusUartReqRepDevice(Component):
    def __init__(self,slaveaddress=0,port="UART2",baudrate=19200,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,serialTimeout=0.05): # defaults for Modbus spec
        super().__init__()


        self.pid = os.getpid()

        if port == 'UART1':
            self.port = '/dev/ttyO1'
        elif port == 'UART2':
            self.port = '/dev/ttyO2'
        elif port == 'UART3':
            self.port = '/dev/ttyO3'
        elif port == 'UART4':
            self.port = '/dev/ttyO4'
        elif port == 'UART5':
            self.port = '/dev/ttyO5'
        else:
            self.logger.error('__init__[%s]: Invalid UART argument, use UART1..5', self.pid)
            sys.exit(-1)

        self.port_config = PortConfig(self.port, baudrate, bytesize, parity, stopbits, serialTimeout)
        self.slaveAddressDecimal = slaveaddress
        self.modbus = SerialModbusComm(self,self.slaveAddressDecimal,self.port_config)
        self.modbusInit = False
        if debugMode:
            self.logger.info("Modbus settings %d @%s:%d %d%s%d [%d]", self.slaveAddressDecimal,self.port_config.portname,self.port_config.baudrate,self.port_config.bytesize,self.port_config.parity,self.port_config.stopbits,self.pid)

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.logger.info("on_clock()[%s]: %s" % (str(self.pid),now))

        if debugMode:
            t0 = time.perf_counter()
            self.logger.debug("on_clock()[%s]: Request Modbus start at %f",str(self.pid),t0)

        if self.modbusInit == False:
            self.modbusInit = True;
            self.modbus.startModbus()
#            pydevd.settrace(host='192.168.1.102',port=5678)

            if debugMode:
                t1 = time.perf_counter()
                self.logger.debug("on_clock()[%s]: Modbus ready at %f, time to start Modbus is %f ms",str(self.pid),t1,(t1-t0)*1000)

        self.clock.halt()


    def __destroy__(self):
        self.logger.info("__destroy__")
        self.modbus.stopModbus()


    '''    
    Receive a Modbus command request.  Process command and send back response.
    '''
    def on_modbusRepPort(self):
        '''Request Received'''
        commandRequest = self.modbusRepPort.recv_pyobj()

        if debugMode:
            self.modbusReqRxTime = time.perf_counter()
            self.logger.debug("on_modbusRepPort()[%s]: Request=%s Received at %f",str(self.pid),commandRequest,self.modbusReqRxTime)

        self.unpackCommand(commandRequest)
        responseValue = -1  # invalid response
        if self.modbus.isModbusAvailable() == True:
            responseValue = self.sendModbusCommand()

            if debugMode:
                t1 = time.perf_counter()
                self.logger.debug("on_modbusRepPort()[%s]: Send Modbus response=%s back to requester at %f",str(self.pid),responseValue,t1)

#        pydevd.settrace(host='192.168.1.102',port=5678)
        else:
            self.logger.debug("Modbus is not available")
            
        '''Send Results'''
        self.modbusRepPort.send_pyobj(responseValue)


    def unpackCommand(self,rxCommand):
        self.commmandRequested = rxCommand.commandType
        self.registerAddress = rxCommand.registerAddress
        self.numberOfRegs = rxCommand.numberOfRegs
        self.numberOfDecimals = rxCommand.numberOfDecimals
        self.signedValue = rxCommand.signedValue
        self.values = rxCommand.values


    def sendModbusCommand(self):
        value = 999  # large invalid value

        if debugMode:
            t0 = time.perf_counter()
            self.logger.debug("sendModbusCommand()[%s]: Sending command to Modbus library at %f",str(self.pid),t0)

        if self.commmandRequested == ModbusCommands.READ_INPUTREG:
            value = self.modbus.readInputRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s", ModbusCommands.READ_INPUTREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue))
        elif self.commmandRequested == ModbusCommands.READ_HOLDINGREG:
            value = self.modbus.readHoldingRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s", ModbusCommands.READ_HOLDINGREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue))
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

        if debugMode:
            t1 = time.perf_counter()
            self.logger.debug("sendModbusCommand()[%s]: Modbus library command complete at %f, time to interact with Modbus library is %f ms",str(self.pid),t1,(t1-t0)*1000)

        return value

