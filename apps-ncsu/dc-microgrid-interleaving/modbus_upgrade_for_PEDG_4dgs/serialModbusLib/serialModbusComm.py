'''
Created on Mar 16, 2017

@author: riaps

This modbus device interface will read input registers and reads/writes holding registers of slave devices.  
At this time, it does not read/write coils.
'''

import minimalmodbus
import serial
from collections import namedtuple
import sys
from enum import Enum, unique
#import pydevd

'''serialTimeout is defined in seconds'''    
PortConfig = namedtuple('PortConfig', ['portname', 'baudrate', 'bytesize', 'parity', 'stopbits', 'serialTimeout'])

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


class SerialModbusComm(object):
    '''
    This library will interface with minimalmodbus with communications over a serial interface.
    
    Note:  The 
    '''

    def __init__(self,component,slaveAddressDecimal,portConfig):
        '''
        Constructor
        '''
        self.port_config = portConfig
        self.slaveAddress = slaveAddressDecimal
        self.portOpen = False   
        
    '''
    Allow user to start initiation of the Modbus and opening of the UART port    
        Defaults: 
            mode='rtu'  (versus 'ascii')
            CLOSE_PORT_AFTER_EACH_CALL=False
            precalculate_read_size=True - if False, serial port reads until timeout, instead of specific number of bytes
            handle_local_echo=False
    '''    
    def startModbus(self):       
        try:
            self.modbusInstrument = minimalmodbus.Instrument(self.port_config.portname,self.slaveAddress)  # defaults as RTU mode
            self.portOpen = True
            print("SerialModbusComm - open startModbus: " + self.port_config.portname + ", " + str(self.port_config.baudrate) + ", " + str(self.port_config.bytesize) + ", " + self.port_config.parity + ", " + str(self.port_config.stopbits) + ", " + str(self.port_config.serialTimeout))
            #self.modbusInstrument.debug = True
        except serial.SerialException:
            print("SerialModbusComm - unable to startModbus: " + self.port_config.portname + ", " + str(self.port_config.baudrate) + ", " + str(self.port_config.bytesize) + ", " + self.port_config.parity + ", " + str(self.port_config.stopbits) + ", " + str(self.port_config.serialTimeout))
            self.modbusInstrument.serial.close()           
            sys.exit(-1)

        '''
        Only port setting that is expected to be different from the default MODBUS settings is baudrate and timeout
        '''
        self.modbusInstrument.serial.baudrate = self.port_config.baudrate
        self.modbusInstrument.serial.timeout = self.port_config.serialTimeout
        
        print("SerialModbusComm - startModbus: " + self.port_config.portname + ", " + str(self.slaveAddress) + ", " + str(self.port_config.baudrate))      
        
    '''
    The user should stop the Modbus when their component ends (or wants to stop it).  This will also close the UART port.
    '''
    def stopModbus(self):
        self.modbusInstrument.serial.close()
        self.portOpen = False
    
    '''
    Read a Slave Input Register (16-bit)
    Arguments:  
        registerAddress  (int): The slave register address (use decimal numbers, not hex).
        numberOfDecimals (int): The number of decimals for content conversion.  Example 77.0 would be register value of 770, 
                                numberOfDecimals=1
        signedValue     (bool): Whether the data should be interpreted as unsigned or signed.
    Returns: single input register value: integer or float value
    '''
    def readInputRegValue(self,registerAddress,numberOfDecimals,signedValue):
        value = -9999
        try:
#            pydevd.settrace(host='192.168.1.102',port=5678)
            value = self.modbusInstrument.read_register(registerAddress,numberOfDecimals,FunctionCodes.READ_INPUTREG.value,signedValue)
        except IOError:
            print("SerialModbusComm IOError: Failed to read input register - address=", registerAddress) 
        except TypeError:
            print("SerialModbusComm TypeError: Failed to read input register - address=", registerAddress)             
                
        return value        
        
    '''
    Read one Slave Holding Register (16-bit)
    Arguments:  
        registerAddress  (int): The slave register address (use decimal numbers, not hex).
        numberOfDecimals (int): The number of decimals for content conversion.  Example 77.0 would be register value of 770, 
                                numberOfDecimals=1
        signedValue     (bool): Whether the data should be interpreted as unsigned or signed.
    Returns: single holding register value: integer or float value (divide by numberOfDecimals * 10)       
    '''
    def readHoldingRegValue(self,registerAddress,numberOfDecimals,signedValue):
        value = -9999
        try:
            value = self.modbusInstrument.read_register(registerAddress,numberOfDecimals,FunctionCodes.READ_HOLDINGREG.value,signedValue)
        except IOError:
            print("SerialModbusComm IOError: Failed to read holding register - address=",registerAddress)  
        except TypeError:
            print("SerialModbusComm TypeError: Failed to read holding register - address=",registerAddress)                                      

        return value
    
    '''
    Read multiple Slave Input Registers (16-bit per register)
    Arguments:  
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        numberOfRegs     (int): The number of registers to read
    Returns: register dataset: list of int       
    '''
    def readMultiInputRegValues(self,registerAddress,numberOfRegs):
        value = -9999
        try:
            value = self.modbusInstrument.read_registers(registerAddress,numberOfRegs,FunctionCodes.READ_INPUTREG.value)
        except IOError:
            print("SerialModbusComm IOError: Failed to read input registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        except TypeError:
            print("SerialModbusComm TypeError: Failed to read input registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      

        return value
 
    '''
    Read multiple Slave Holding Registers (16-bit per register)
    Arguments:  
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        numberOfRegs     (int): The number of registers to read
    Returns: register dataset: list of int       
    '''
    def readMultiHoldingRegValues(self,registerAddress,numberOfRegs):
        value = -9999
        try:
            value = self.modbusInstrument.read_registers(registerAddress,numberOfRegs,FunctionCodes.READ_HOLDINGREG.value)
        except IOError:
            print("SerialModbusComm IOError: Failed to read holding registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
        except TypeError:
            print("SerialModbusComm TypeError: Failed to read holding registers - address=" + str(registerAddress) + ", numberOfRegs=" + str(numberOfRegs))      
   
        return value
    
    '''
    Write one Slave holding register value (multiply value by numberOfDecimals * 10)
    Agruments:
        registerAddress  (int): The slave register address (use decimal numbers, not hex).
        value        (16 bits): The value to write
        numberOfDecimals (int): The number of decimals for content conversion.  
                                Example: numberOfDecimals=1, value=77.0 would write register value of 770, 
        signedValue     (bool): Whether the data should be interpreted as unsigned or signed.
    Returns: None
        
    Note: write_register can handle either FunctionCode.writeHoldingReg (6) or FunctionCode.writeHoldingRegs (16), this implementation
    uses FunctionCode.writeHoldingRegs (16) due to plans for codes used in the first implementation.
    '''  
    def writeHoldingRegister(self,registerAddress,value,numberOfDecimals,signedValue):
        try:
            self.modbusInstrument.write_register(registerAddress,value,numberOfDecimals,FunctionCodes.WRITE_HOLDINGREG.value,signedValue)
        except IOError:
            print("SerialModbusComm IOError: Failed to write holding register - address=" + str(registerAddress))      
        except TypeError:
            print("SerialModbusComm TypeError: Failed to write holding register - address=" + str(registerAddress))      
              
    '''  
    Write multiple Slave holding register values (16 bits per register)
    Agruments:
        registerAddress  (int): The starting slave register address (use decimal numbers, not hex).
        values   (list of int): The values to write - number of registers written is based on the length of the 'values' list
    Returns: None
    
    Note:  Command uses FunctionCode.writeHoldingRegs (16)
    '''  
    def writeHoldingRegisters(self,registerAddress,values):
        try:
            self.modbusInstrument.write_registers(registerAddress,values)
        except IOError:
            print("SerialModbusComm IOError: Failed to write holding registers - address=" + str(registerAddress))   #MM TODO:  add number of values   
        except TypeError:
            print("SerialModbusComm TypeError: Failed to write holding registers - address=" + str(registerAddress))   #MM TODO:  add number of values   
              
          
    
        
        
        