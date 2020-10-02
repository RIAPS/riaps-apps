'''
Created on Nov 11, 2019

@author: riaps

This module utilizes the umodbus.
Both need to be installed in the development environment.
    $ sudo pip3 install umodbus 
'''

from riaps.run.comp import Component
import logging
import os
from collections import namedtuple
from enum import Enum
import time
from tcpModbusLib.tcpModbusComm import TcpModbusComm,PortConfig

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

CommandFormat = namedtuple('CommandFormat', ['commandType','registerAddress','numberOfRegs','values', 'signedValue'])

class ModbusTcpReqRepDevice(Component):
    def __init__(self,slaveaddress=3,ipaddress = '192.168.10.110', port =502,serialTimeout=0.05): # defaults for Modbus spec
        super().__init__()


        self.pid = os.getpid()
        self.port_config = PortConfig(ipaddress, port, serialTimeout)
        self.modbus = TcpModbusComm(self,slaveaddress,self.port_config)
        self.modbusInit = False
        if debugMode:
            self.logger.info("Modbus settings %d @%s:%d %d [%d]", self.slaveaddress,self.port_config.ip, self.port_config.port, self.port_config.timeout, self.pid)

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
        self.values = rxCommand.values
        self.signedValue = rxCommand.signedValue


    def sendModbusCommand(self):
        value = 999  # large invalid value

        if debugMode:
            t0 = time.perf_counter()
            self.logger.debug("sendModbusCommand()[%s]: Sending command to Modbus library at %f",str(self.pid),t0)


        if self.commmandRequested == ModbusCommands.READMULTI_INPUTREGS:
            value = self.modbus.readMultiInputRegValues(self.registerAddress, self.numberOfRegs, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d", ModbusCommands.READMULTI_INPUTREGS.name,self.registerAddress,self.numberOfRegs)
        elif self.commmandRequested == ModbusCommands.READMULTI_HOLDINGREGS:
            value = self.modbus.readMultiHoldingRegValues(self.registerAddress, self.numberOfRegs, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d, numOfRegs=%d", ModbusCommands.READMULTI_HOLDINGREGS.name,self.registerAddress,self.numberOfRegs)
        elif self.commmandRequested == ModbusCommands.WRITEMULTI_HOLDINGREGS:
            value = self.modbus.writeHoldingRegisters(self.registerAddress, self.values, self.signedValue)
            #self.logger.info("ModbusUartDevice: sent command %s, register=%d",ModbusCommands.WRITEMULTI_HOLDINGREGS.name,self.registerAddress)
            #self.logger.info("ModbusUartDevice: Values - %s", str(self.values).strip('[]'))

        if debugMode:
            t1 = time.perf_counter()
            self.logger.debug("sendModbusCommand()[%s]: Modbus library command complete at %f, time to interact with Modbus library is %f ms",str(self.pid),t1,(t1-t0)*1000)

        return value

