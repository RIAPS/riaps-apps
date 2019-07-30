'''
ComputationalComponent Modbus-MQTT

Created on Jun 14, 2019

@author: Danny Crescimone
'''

import zmq
from riaps.run.comp import Component
from riaps.run.exc import PortError
import uuid
import os
from collections import namedtuple
from ModbusUartReqRepDevice import CommandFormat, ModbusCommands
import pydevd
import time
import logging

''' Enable debugging to gather timing information on the code execution'''
debugMode = True

RegSet = namedtuple('RegSet', ['idx', 'value'])
InputRegs = namedtuple('InputRegs', ['first', 'second', 'third', 'fourth'])

hReg1 = "start"
hReg2 = "power"

'''For Inverter control'''
HoldingRegs = namedtuple('HoldingRegs', [hReg1, hReg2])


class ComputationalComponent(Component):
    def __init__(self,dev):
        super().__init__()
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.inputRegs = InputRegs(RegSet(0,12), RegSet(1, 45), RegSet(2, 56), RegSet(3, 78))
        self.holdingRegs = HoldingRegs(RegSet(0, 0), RegSet(1, 0))

        self.message_sent = False

        '''Setup Commands'''
        self.type = dev  # should contain the Device typology name (for example "DCESD")
        self.numRegsToRead = len(self.inputRegs)
        self.defaultNumOfRegs = 1
        self.dummyValue = [0]
        self.defaultNumOfDecimals = 0
        self.signedDefault = False
        self.ModbusPending = 0
        self.ModbusReady = False
        self.logger.info("ComputationalComponent: %s - starting" % str(self.pid))

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock()[%s]: %s" % (str(self.pid), str(now)))

        if not self.ModbusReady:
            # Halt clock while waiting for the status
            self.clock.halt()
            self.logger.info("clock halted")
            # If status=true, set flag and restart clock
            try:
                msg = "readytest"
                if not self.message_sent:
                    self.modbusStatusReqPort.send_pyobj(msg)
                    self.logger.info("Modbus status requested")
                    self.message_sent = True
                if self.message_sent:
                    modStatus = self.modbusStatusReqPort.recv_pyobj()
                    self.logger.info("Modbus status received")
                    self.message_sent = False
                    if modStatus:
                        self.ModbusReady = True
                        self.logger.info("Modbus is ready, clock is restarted")
            except PortError as e:
                self.logger.error("on_clock-modbusStatusReq:port exception = %d" % e.errno)
                if e.errno in (PortError.EAGAIN, PortError.EPROTO):
                    self.logger.error("on_clock-modbusStatusReq: port error received")
            self.clock.launch()
            self.logger.info("clock restarted")
        else:
            '''Read all input registers''' #on_clock
            self.command = CommandFormat(ModbusCommands.READMULTI_INPUTREGS, self.inputRegs.first.idx, self.numRegsToRead,
                                         self.dummyValue, self.defaultNumOfDecimals, self.signedDefault)
            self.SendReq(self.command)

    def on_RecCommand(self):  # to handle the commands received by MQTT
        if self.ModbusReady:
            cmd = self.RecCommand.recv_pyobj()  # Dictionary from MQTT (to test)
            self.logger.info("Command received from MQTT : %s" % str(cmd))
            numRegsToWrite = len(cmd)  # to count how many holding registers it has to write

            if numRegsToWrite == 1:
                '''Read all the holding register'''
                if "read" in cmd:
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.holdingRegs.start.idx,
                                             len(self.holdingRegs), self.dummyValue, self.defaultNumOfDecimals, self.signedDefault)
                    self.SendReq(self.command)

                '''Write a single holding register'''
                if hReg1 in cmd:
                    self.values = [cmd[hReg1]]
                    self.logger.info("command received from SCADA: %s" % str(self.values)) 
                    self.command = CommandFormat(ModbusCommands.WRITE_HOLDINGREG, self.holdingRegs.start.idx,
                                                 numRegsToWrite, self.values, self.defaultNumOfDecimals, self.signedDefault)
                    self.SendReq(self.command)
                elif hReg2 in cmd:
                    if self.type == "LVSST/G":
                       cmd[hReg2] = cmd[hReg2] + 1500 #to convert the command for DSP
                    elif self.type == "DCESD":
                       cmd[hReg2] = cmd[hReg2] + 2500 #to convert the command for DSP
                    self.values = [cmd[hReg2]]
                    self.command = CommandFormat(ModbusCommands.WRITE_HOLDINGREG, self.holdingRegs.power.idx, numRegsToWrite,
                                         self.values, self.defaultNumOfDecimals, self.signedDefault)
                    self.SendReq(self.command)

            elif numRegsToWrite == 2:
                '''Write all holding register'''
                if(hReg1 in cmd) and (hReg2 in cmd):
                    if self.type == "LVSST/G":
                       cmd[hReg2] = cmd[hReg2] + 1500  # to convert the command for DSP
                    elif self.type == "DCESD":
                       cmd[hReg2] = cmd[hReg2] + 2500  # to convert the command for DSP  
                    self.values = [cmd[hReg1], cmd[hReg2]]
                    self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.holdingRegs.start.idx, numRegsToWrite, self.values,
                                         self.defaultNumOfDecimals, self.signedDefault)
                    self.SendReq(self.command)
                else:
                    self.logger.info("wrong command keys sent, they should be: <%s> and <%s>" % (hReg1,hReg2))

    def SendReq(self, msg):
        '''Send Command'''
        if self.ModbusPending == 0:
            if debugMode:
                self.cmdSendStartTime = time.perf_counter()
                self.logger.debug(
                    "on_clock()[%s]: Send command to ModbusUartDevice at %f" % (str(self.pid), self.cmdSendStartTime))
            try:
                self.modbusCommandReqPort.send_pyobj(msg)
                self.ModbusPending += 1
                self.logger.info("Modbus command sent")
            except PortError as e:
                self.logger.error("on_clock-modbusCommandReqPort:send exception = %d" % e.errno)
                if e.errno in (PortError.EAGAIN, PortError.EPROTO):
                    self.logger.error("on_clock-modbusCommandReqPort: port error received")
        else:
            self.logger.info("Modbus is pending. Try to send the command later")
            

    def on_modbusCommandReqPort(self):
        '''Receive Response'''
        try:
            msg = self.modbusCommandReqPort.recv_pyobj()
            self.ModbusPending -= 1
            self.logger.info("Modbus command response received")
        except PortError as e:
            self.logger.error("on_modbusCommandReqPort:receive exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN, PortError.EPROTO):
                self.logger.error("on_modbusCommandReqPort: port error received")

        if debugMode:
            self.cmdResultsRxTime = time.perf_counter()
            self.logger.debug(
                "on_modbusCommandReqPort()[%s]: Received Modbus data=%s from ModbusUartDevice at %f, time from cmd to data is %f ms" % (
                    str(self.pid), repr(msg), self.cmdResultsRxTime,
                    (self.cmdResultsRxTime - self.cmdSendStartTime) * 1000))


        if self.command.commandType == ModbusCommands.READMULTI_INPUTREGS:
            Cmsg = self.Convertions(msg)
            logMsg = "Register " + str(self.command.registerAddress) + " values are " + str(Cmsg)
            self.pubPort.send_pyobj(Cmsg) # message that go to MQTT
            self.logger.info("message send to MQTT: %s" % str(Cmsg))
        elif self.command.commandType == ModbusCommands.READMULTI_HOLDINGREGS:
            logMsg = "Register " + str(self.command.registerAddress) + " values are " + str(msg)
            #self.pubPort.send_pyobj(msg) # message that go to MQTT  # this is only for debugging fase
            self.logger.info("message send to MQTT: %s" % str(msg))             
        elif self.command.commandType == ModbusCommands.WRITE_HOLDINGREG:
            logMsg = "Wrote Register " + str(self.command.registerAddress)
        elif self.command.commandType == ModbusCommands.WRITEMULTI_HOLDINGREGS:
            logMsg = "Wrote Registers " + str(self.command.registerAddress) + " to " + str(
                self.command.registerAddress + self.command.numberOfRegs - 1)

        self.tx_modbusData.send_pyobj(logMsg)  # Send log data"""


    def Convertions(self, msg):  # Register value convertions

        d = {}

        if self.type == "LVSST/G":
           msg[0] = round(10000-msg[0]*20000/65535)  # AC side active power[W]
           msg[1] = round(msg[1]*10000/65535-5000)   # AC side reactive power[Var]
           msg[2] = round(msg[2]*500/65535)          # AC RMS voltage[V] 
           msg[3] = round(msg[3]*10000/65535-5000)   # DC side power[W]  
           for i in range(len(msg)):
              if (msg[i] > 0 and msg[i] < 30) or (msg[i] < 0 and msg[i] > -30):
                 msg[i] = 0 
           msg[2] = max(msg[2], 0)  # to saturate the data

           d = {"AC side Active Power[W]":msg[0],"AC side Reactive Power[Var]":msg[1],"AC RMS Voltage[V]":msg[2],"DC side Power[W]":msg[3]}

        elif self.type == "LVSST/L":
           msg[0] = round(msg[0]*200/65535)          # AC port1 voltage[V]
           msg[1] = round(msg[1]*6000/65535-3080)    # AC port1 active power[W]
           msg[2] = round(msg[2]*200/65535)          # AC port2 voltage[V]    
           msg[3] = round(msg[3]*6000/65535-3050)    # AC port2 active power[W]
           for i in range(len(msg)):
              if (msg[i] > 0 and msg[i] < 30) or (msg[i] < 0 and msg[i] > -30):
                 msg[i] = 0           
           for z in range(len(msg)):  # to saturate the data
               msg[z] = max(msg[z], 0)

           d = {"AC port1 Voltage[V]":msg[0],"AC port1 Active Power[W]":msg[1],"AC port2 Voltage[V]":msg[2],"AC port2 Power[W]":msg[3]}

        elif self.type == "DCESD":          
           msg[0] = round(msg[0]*10000/65535-5000)                  # Battery power[W]
           msg[1] = max(round(msg[1]*520/65535-20), 0)              # DC voltage[V]
           msg[2] = float("{0:.2f}".format((msg[2]*100/65535-50)/5))   # Battery current[A]
           for i in range(len(msg)-2):
              if (msg[i] > 0 and msg[i] < 35) or (msg[i] < 0 and msg[i] > -35):
                 msg[i] = 0           
           msg[1] = max(msg[1], 0)  # to saturate the data
           msg[3] = max(msg[3], 0)

           d = {"Battery Power[W]":msg[0],"DC Voltage[V]":msg[1],"Battery Current[A]":msg[2],"SoC[%]":msg[3]}  # Python Dictionary
			   
        return d


    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)
