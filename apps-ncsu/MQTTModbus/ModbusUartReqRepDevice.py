'''
Created on Mar 14, 2017

@author: riaps

This module utilizes the MinimalModbus (which utilizes pySerial).
Both need to be installed in the development environment.
    $ sudo pip3 install minimalmodbus  (which should install pySerial)
'''

from riaps.run.comp import Component
#import logging
import os
import serial
from serialModbusLib.serialModbusComm import SerialModbusComm,PortConfig
from collections import namedtuple
from enum import Enum
#import pydevd
import time
import sys


''' Enable debugging to gather timing information on the code execution'''
debugMode = True

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
        self.statusRequestPending = 0
        self.commandRequestPending = 0

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
            self.logger.error("__init__[%s]: Invalid UART argument, use UART1..5" % self.pid)

        self.port_config = PortConfig(self.port, baudrate, bytesize, parity, stopbits, serialTimeout)
        self.slaveAddressDecimal = slaveaddress
        self.modbus = SerialModbusComm(self.slaveAddressDecimal,self.port_config)
        self.logger.info("Modbus settings %d @%s:%d %d%s%d [%d]" % (self.slaveAddressDecimal,self.port_config.portname,self.port_config.baudrate,self.port_config.bytesize,self.port_config.parity,self.port_config.stopbits,self.pid))
        self.modbus.startModbus()
        self.logger.info("Modbus started")

    def __destroy__(self):
        self.modbus.stopModbus()
        self.logger.info("__destroy__")

    '''
    Receive a Modbus status request.  Send back state of the modbusReady flag
    '''
    def on_modbusStatusRepPort(self):
        self.logger.info("start on_modbusStatusReqPort")
        try:
            statusRequest = self.modbusStatusRepPort.recv_pyobj()
            self.statusRequestPending += 1
            self.logger.info("Request for Modbus device status received")
        except PortError as e:
            self.logger.error("on_modbusStatusRepPort:receive exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.error("on_modbusStatusRepPort: port error received")

        if self.statusRequestPending == 1:
            try:
                msg = self.modbus.isModbusAvailable()
                if msg:
                    self.logger.info("Modbus is available")
                    self.modbusStatusRepPort.send_pyobj(str(msg))
                    self.statusRequestPending -= 1
                    self.logger.info("Response for Modbus device status sent")
                else:
                    self.logger.info("Modbus is not available")

            except PortError as e:
                self.logger.error("on_modbusStatusRepPort:send exception = %d" % e.errno)
                if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                    self.logger.error("on_modbusStatusRepPort: port error received")
        elif self.statusRequestPending > 1:
            # This should not happen if the requesting component has the appropriate error handling for request/reply
            self.logger.info("A status request is pending, no additional request was made")


    '''
    Receive a Modbus command request.  Process command and send back response.
    '''
    def on_modbusCommandRepPort(self):
        '''Request Received'''
        try:
            commandRequest = self.modbusCommandRepPort.recv_pyobj()
            self.commandRequestPending += 1
            self.logger.debug("Request for Modbus device command received")
            #if debugMode:
            #    self.modbusReqRxTime = time.perf_counter()
            #    self.logger.debug("modbusCommandRepPort()[%s]: Request=%s Received at %f" % (str(self.pid),commandRequest,self.modbusReqRxTime))

        except PortError as e:
            self.logger.error("on_modbusCommandRepPort:receive exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.error("on_modbusCommandRepPort: port error received")

        if self.commandRequestPending == 1:
            self.unpackCommand(commandRequest)
            responseValue = -1  # invalid response
            if self.modbus.isModbusAvailable() == True:
                self.logger.debug("Sending command to Modbus interface")
                responseValue = self.sendModbusCommand()
                self.logger.debug("Modbus Response received by device")
                #if debugMode:
                #    t1 = time.perf_counter()
                #    self.logger.debug("modbusCommandRepPort()[%s]: Send Modbus response=%s back to requester at %f" % (str(self.pid),responseValue,t1))
            else:
                self.logger.info("Modbus is not available")

            '''Send Results'''
            try:
                self.modbusCommandRepPort.send_pyobj(responseValue)
                self.commandRequestPending -= 1
                self.logger.debug("Response for Modbus device command sent")
            except PortError as e:
                self.logger.error("on_modbusCommandRepPort:send exception = %d" % e.errno)
                if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                    self.logger.error("on_modbusCommandRepPort: port error received")

        elif self.commandRequestPending > 1:
            # This should not happen if the requesting component has the appropriate error handling for request/reply
            self.logger.info("A command request is pending, no additional request was made")



    def unpackCommand(self,rxCommand):
        self.commmandRequested = rxCommand.commandType
        self.registerAddress = rxCommand.registerAddress
        self.numberOfRegs = rxCommand.numberOfRegs
        self.numberOfDecimals = rxCommand.numberOfDecimals
        self.signedValue = rxCommand.signedValue
        self.values = rxCommand.values


    def sendModbusCommand(self):
        value = 999  # large invalid value

        #if debugMode:
        #    t0 = time.perf_counter()
        #    self.logger.debug("sendModbusCommand()[%s]: Sending command to Modbus library at %f" % (str(self.pid),t0))
        self.logger.debug("sendModbusCommand(): Sending command to Modbus library")

        try:
            if self.commmandRequested == ModbusCommands.READ_INPUTREG:
                value = self.modbus.readInputRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s" % (ModbusCommands.READ_INPUTREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue)))
            elif self.commmandRequested == ModbusCommands.READ_HOLDINGREG:
                value = self.modbus.readHoldingRegValue(self.registerAddress, self.numberOfDecimals, self.signedValue)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d, numOfDecimals=%d, signed=%s" % (ModbusCommands.READ_HOLDINGREG.name,self.registerAddress,self.numberOfDecimals,str(self.signedValue)))
            elif self.commmandRequested == ModbusCommands.READMULTI_INPUTREGS:
                value = self.modbus.readMultiInputRegValues(self.registerAddress, self.numberOfRegs)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d" % (ModbusCommands.READMULTI_INPUTREGS.name,self.registerAddress,self.numberOfRegs))
            elif self.commmandRequested == ModbusCommands.READMULTI_HOLDINGREGS:
                value = self.modbus.readMultiHoldingRegValues(self.registerAddress, self.numberOfRegs)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d" % (ModbusCommands.READMULTI_HOLDINGREGS.name,self.registerAddress,self.numberOfRegs))
            elif self.commmandRequested == ModbusCommands.WRITE_HOLDINGREG:
                self.modbus.writeHoldingRegister(self.registerAddress, self.values[0], self.numberOfDecimals, self.signedValue)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d, value=%d, numberOfDecimals=%d, signed=%s" % (ModbusCommands.WRITE_HOLDINGREG.name,self.registerAddress,self.values[0],self.numberOfDecimals,str(self.signedValue)))
            elif self.commmandRequested == ModbusCommands.WRITEMULTI_HOLDINGREGS:
                self.modbus.writeHoldingRegisters(self.registerAddress, self.values)
                self.logger.debug("ModbusUartDevice: sent command %s, register=%d" % (ModbusCommands.WRITEMULTI_HOLDINGREGS.name,self.registerAddress))
                self.logger.debug("ModbusUartDevice: Values - %s" % str(self.values).strip('[]'))
        except Exception as e:
            self.logger.error("ModbusUartDevice: Exception thrown during Modbus command action - %s" % e)

        #if debugMode:
        #    t1 = time.perf_counter()
        #    self.logger.debug("sendModbusCommand()[%s]: Modbus library command complete at %f, time to interact with Modbus library is %f ms" % (str(self.pid),t1,(t1-t0)*1000))

        return value
