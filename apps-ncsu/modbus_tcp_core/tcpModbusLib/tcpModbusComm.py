'''
Created on Nov 19, 2019

@author: riaps

This modbus device interface will read input registers and reads/writes holding registers of slave devices with modbus tcp.  
At this time, it does not read/write coils.
'''

#!/usr/bin/env python
import socket

from umodbus import conf
from umodbus.client import tcp

from collections import namedtuple
import sys
from enum import Enum, unique




#import pydevd

'''serialTimeout is defined in seconds'''    
PortConfig = namedtuple('PortConfig', ['ip', 'port', 'timeout'])

''' 
Function Codes (per Modbus Spec)
'''
@unique
class FunctionCodes(Enum):
    READ_COIL = 1
    READ_BIT = 2
    READ_HOLDINGREG = 3
    READ_INPUTREG = 4
    WRITE_BIT = 5
    WRITE_HOLDINGREG = 6
    WRITEMULTI_COILS = 15
    WRITEMULTI_HOLDINGREGS = 16


class TcpModbusComm(object):
    '''
    This library will interface with umodbus with communications over a tcp/ip.
    
    Note:  The 
    '''

    def __init__(self,component,slaveAddress,portConfig):
        '''
        Constructor
        '''
        self.port_config = portConfig
        self.slaveAddress = slaveAddress
        self.portOpen = False   
        
    '''
    Allow user to start initiation of the Modbus and opening of the UART port    
        Defaults: 
            mode='rtu'  (versus 'ascii')
            CLOSE_PORT_AFTER_EACH_CALL=False
            precalculate_read_size=True - if False, serial port reads until timeout, instead of specific number of bytes
            handle_local_echo=False
    '''    
    
    def isModbusAvailable(self):
        return self.portOpen
        
    def startModbus(self):       
        try: #here 'sock' only works for one connection
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.port_config.ip, self.port_config.port))
            self.portOpen = True
            print("TcpModbusComm - open startModbus: " + self.port_config.ip + ", " + str(self.port_config.port))
            #self.modbusInstrument.debug = True
        except serial.SerialException: # change this to proper exception, about TCP
            print("TcpModbusComm - unable to startModbus: " + self.port_config.portname + ", " + str(self.port_config.port))
            self.sock.close()         
            sys.exit(-1)

        '''
        Only port setting that is expected to be different from the default MODBUS settings is baudrate and timeout
        '''
        #self.modbusInstrument.serial.timeout = self.port_config.serialTimeout
              
        
    '''
    The user should stop the Modbus when their component ends (or wants to stop it).  This will also close the TCP/IP port.
    '''
    def stopModbus(self):
        self.sock.close()
        self.portOpen = False
 
 
    '''
    Read multiple Slave Input Registers (16-bit per register)
    Arguments:  
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        numberOfRegs     (int): The number of registers to read
    Returns: register dataset: list of int       
    '''

    
    def readMultiInputRegValues(self,registerAddress,numberOfRegs, signed):
        value = -9999
        try:
            conf.SIGNED_VALUES = signed
            message = tcp.read_input_registers(slave_id=self.slaveAddress, starting_address=registerAddress, quantity=numberOfRegs)
            value = tcp.send_message(message, self.sock)
        except IOError: #change errors to TCP specific
            print("TcpModbusComm IOError: Failed to read input registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        except TypeError:
            print("TcpModbusComm TypeError: Failed to read input registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        return value
 
    '''
    Read multiple Slave Holding Registers (16-bit per register)
    Arguments:  
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        numberOfRegs     (int): The number of registers to read
    Returns: register dataset: list of int       
    '''
    def readMultiHoldingRegValues(self,registerAddress,numberOfRegs, signed):
        value = -9999
        try:
            conf.SIGNED_VALUES = signed
            message  = tcp.read_holding_registers(slave_id=self.slaveAddress, starting_address=registerAddress, quantity=numberOfRegs)
            value = tcp.send_message(message, self.sock)           
        except IOError:
            print("TcpModbusComm IOError: Failed to read holding registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        except TypeError:
            print("TcpModbusComm TypeError: Failed to read holding registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        return value
         
              
    '''  
    Write multiple Slave holding register values (16 bits per register)
    Agruments:
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        values   (list of int): The values to write - number of registers written is based on the length of the 'values' list
    Returns: None
    
    Note:  Command uses FunctionCode.writeHoldingRegs (16)
    '''  
    def writeHoldingRegisters(self,registerAddress,values, signed):
        value = -9990
        try:
            conf.SIGNED_VALUES = signed
            message  = tcp.write_multiple_registers(self.slaveAddress, registerAddress, values)
            value = tcp.send_message(message, self.sock)
        except IOError:
            print("TcpModbusComm IOError: Failed to write holding registers - address=" + str(registerAddress))   #MM TODO:  add number of values   
        except TypeError:
            print("TcpModbusComm TypeError: Failed to write holding registers - address=" + str(registerAddress))   #MM TODO:  add number of values   
        return value      
          
    
        
        
        