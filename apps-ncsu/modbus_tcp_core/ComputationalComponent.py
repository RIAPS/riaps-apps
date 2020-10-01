'''

Created on Nov 25, 2019

@author: riaps
    
'''

from riaps.run.comp import Component
from riaps.run.exc import PortError
import uuid
import os
from collections import namedtuple
from ModbusTcpReqRepDevice import CommandFormat,ModbusCommands

''' Enable debugging to gather timing information on the code execution'''
debugMode = False

'''Register number / value'''
RegSet = namedtuple('RegSet', ['RegNum', 'value'])
'''For Inverter Control'''
InputHoldingRegs = namedtuple('InputHoldingRegs', ['Grid_Guard_Code','Language','Operating_mode_relay','Active_Power_Limit','On_Off'])

'''For Inverter READ'''
HoldingRegs = namedtuple('HoldingRegs',['Plant_mains_connection','DC_Power','DC_Voltage', 'DC_Current','AC_Grid_Frequency','AC_Active_Power','AC_Active_Power_phase_L1','AC_Active_Power_phase_L2','AC_Active_Power_phase_L3','AC_Reactive_Power','AC_Reactive_Power_phase_L1','AC_Reactive_Power_phase_L2','AC_Reactive_Power_phase_L3','AC_Apparent_Power','AC_Apparent_Power_phase_L1','AC_Apparent_Power_phase_L2','AC_Apparent_Power_phase_L3','AC_Voltage_phase_L1','AC_Voltage_phase_L2','AC_Voltage_phase_L3','AC_Grid_Current','AC_Grid_Current_phase_L1','AC_Grid_Current_phase_L2','AC_Grid_Current_phase_L3','Operating_Time','Feed_in_time','Daily_yeld','Total_yeld','Grid_Guard_Code','Language','Operating_mode_relay','Active_Power_Limit','On_Off'])
 
class ComputationalComponent(Component):
    def __init__(self, Ts, ip):
        super().__init__()
        #pydevd.settrace(host='192.168.1.103',port=5678)
        self.uuid = uuid.uuid4().int
        self.pid = os.getpid()
        self.ip = ip   
        self.inputHoldingRegs = InputHoldingRegs(RegSet(43090,[11830, 62961]),RegSet(40013,0),RegSet(40575,0),RegSet(40915,0),RegSet(41253,0))
        self.holdingRegs = HoldingRegs(RegSet(30881,0),RegSet(30773,0),RegSet(30771,0),RegSet(30769,0),RegSet(30803,0),RegSet(30775,0),RegSet(30777,0),RegSet(30779,0),RegSet(30781,0),RegSet(30805,0),RegSet(30807,0),RegSet(30809,0),RegSet(30811,0),RegSet(30813,0),RegSet(30815,0),RegSet(30817,0),RegSet(30819,0),RegSet(30783,0),RegSet(30785,0),RegSet(30787,0),RegSet(30795,0),RegSet(30977,0),RegSet(30979,0),RegSet(30981,0),RegSet(30541,0),RegSet(30543,0),RegSet(30535,0),RegSet(30529,0),RegSet(43090,0),RegSet(40013,0),RegSet(40575,0),RegSet(40915,0),RegSet(41253,0))   

        '''Setup Commands for modbusTCP'''          #Initialization values
        self.readOrWrite = 1                        # 1 to will enable also write 
        self.defaultInitalReg = 0
        self.defaultNumOfRegs = 0
        self.dummyValue = [0]
        self.defaultNumOfDecimals = 0
        self.signedDefault = False
        self.count=1
        self.logger.info("ComputationalComponent: %s - starting" % str(self.pid))   

    def on_clock(self):
        now = self.clock.recv_pyobj() 
        self.logger.info("On_clock()[%s]: %s ::::::::::::::::::::::::::::::::::::: UPDATING OPERATIONS :::::::::::::::::::::::::::::::::::::::::::::::" % (str(self.pid), str(now)))

        '''Read multiple holding registers'''
        RegtypeR=['Connection type','DC','AC1','AC2','Time','Energy']
            
        for i in range (len(RegtypeR)):                                   #Cycle for how many starting registers to read
            if(RegtypeR[i]=='Energy'):                                     
                    self.defaultInitalReg = self.holdingRegs.Total_yeld.RegNum                        #Energy yeld values
                    self.defaultNumOfRegs = 8
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)

            elif(RegtypeR[i]=='DC'):                                      #DC input values
                    self.defaultInitalReg = self.holdingRegs.DC_Current.RegNum
                    self.defaultNumOfRegs = 6
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)  
                
            elif(RegtypeR[i]=='Time'):                                     #Time values
                    self.defaultInitalReg = self.holdingRegs.Operating_Time.RegNum
                    self.defaultNumOfRegs = 4
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)                             

                
            elif(RegtypeR[i]=='AC1'):                                       #AC1 output values
                    self.defaultInitalReg = self.holdingRegs.AC_Active_Power.RegNum
                    self.defaultNumOfRegs = 46
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
             
            elif(RegtypeR[i]=='AC2'):                                       #AC2 output values
                    self.defaultInitalReg = self.holdingRegs.AC_Grid_Current_phase_L1.RegNum
                    self.defaultNumOfRegs = 6
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)        
                    
            elif(RegtypeR[i]=='Connection type'):                           #Connection types values
                    self.defaultInitalReg = self.holdingRegs.Plant_mains_connection.RegNum
                    self.defaultNumOfRegs = 2
                    self.logger.info("Request to Read type <%s>" %str(RegtypeR[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)                    
                                                    
        '''Write multiple holding registers'''                       
        if (self.readOrWrite == 1):                                                
            RegtypeW=['GridGuardCode','Language','Operating mode of multi-function relay','Active power Limit','On/Off']
            for i in range (len(RegtypeW)):                                                #Cycle for how many starting registers to read
                if(RegtypeW[i]=='GridGuardCode'):
                    self.defaultInitalReg = self.inputHoldingRegs.Grid_Guard_Code.RegNum   #Register for Grid Guard Code             
                    self.defaultNumOfRegs = 2
                    'Read before Write' 
                    self.logger.info("Request to Read type <%s>" %str(RegtypeW[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
                    'Write'
                    self.values = self.inputHoldingRegs.Grid_Guard_Code.value               #Grid Guard Code (fixed)
                    if (self.holdingRegs.Grid_Guard_Code.value==0 and self.count==1):       #Write only if it is not already written 
                        self.count=0
                        self.logger.info("Request to Write type <%s>" %str(RegtypeW[i]))                                                        #Remove self.count if running for long time or when SMA updates the firmware
                        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.defaultInitalReg, self.defaultNumOfRegs,self.values, self.signedDefault)
                        repMsg = self.sendModbusRequest(self.command)
                        self.exitandcheckvalue(repMsg)
                    else:
                        self.logger.info("Requested to Write type <%s> -Value already written-" %str(RegtypeW[i]))
                    
                elif(RegtypeW[i]=='Language'):                                              #Register for Changing Language
                    self.defaultInitalReg = self.inputHoldingRegs.Language.RegNum          
                    self.defaultNumOfRegs = 2
                    'Read before Write' 
                    self.logger.info("Request to Read type <%s>" %str(RegtypeW[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
                    'Write'
                    msgval = [0, 778]                                 #Language: 777=German 778=English 779=Italian 780=Spanish
                    msg0=(msgval[0]*65536+msgval[1])                  #Converted to 1 value for comparison reason
                    'Storing writing values for later usage'
                    self.inputHoldingRegs = self.inputHoldingRegs._replace(Language=RegSet(RegNum=40013,value=msg0))
                    if (self.inputHoldingRegs.Language.value != self.holdingRegs.Language.value):   #Write only if is not yet written
                        self.values = msgval                          
                        self.logger.info("Request to Write type <%s>" %str(RegtypeW[i]))
                        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.defaultInitalReg, self.defaultNumOfRegs,self.values, self.signedDefault)
                        repMsg = self.sendModbusRequest(self.command)
                        self.exitandcheckvalue(repMsg)
                    else:
                        self.logger.info("Requested to Write type <%s> -Value already written-" %str(RegtypeW[i]))    
                                                       
                elif(RegtypeW[i]=='Operating mode of multi-function relay'):                  
                    self.defaultInitalReg = self.inputHoldingRegs.Operating_mode_relay.RegNum       #Register for Operating mode of multi-function relay
                    self.defaultNumOfRegs = 2
                    'Read before Write' 
                    self.logger.info("Request to Read type <%s>" %str(RegtypeW[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
                    'Write'
                    msgval = [0, 1349]                        #Operationg_mode : Switching status grid relay= 258 Fault indication=1341 Fan control=1342 Self-consumption=1343 Control via communication=1349 Battery bank=1359
                    msg0=(msgval[0]*65536+msgval[1])          #Converted to 1 value for comparison reason
                    'Storing writing values for later usage'
                    self.inputHoldingRegs = self.inputHoldingRegs._replace(Operating_mode_relay=RegSet(RegNum=40575,value=msg0))
                    if (self.inputHoldingRegs.Operating_mode_relay.value != self.holdingRegs.Operating_mode_relay.value) :
                        self.logger.info("Request to Write type <%s>" %str(RegtypeW[i]))
                        self.values=msgval 
                        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.defaultInitalReg, self.defaultNumOfRegs,self.values, self.signedDefault)
                        repMsg = self.sendModbusRequest(self.command)
                        self.exitandcheckvalue(repMsg)
                    else:
                        self.logger.info("Requested to Write type <%s> -Value already written-" %str(RegtypeW[i]))
                    
                elif(RegtypeW[i]=='Active power Limit'):       #Register for Active power Limit
                    self.defaultInitalReg = self.inputHoldingRegs.Active_Power_Limit.RegNum     
                    self.defaultNumOfRegs = 2
                    'Read before Write'  
                    self.logger.info("Request to Read type <%s>" %str(RegtypeW[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
                    'Write' 
                    msgval = [0,20000]                          #Active power limit in [W]         
                    msg0=(msgval[0]*65536+msgval[1])            #Converted to 1 value for comparison reason
                    'Storing writing values for later usage'
                    self.inputHoldingRegs = self.inputHoldingRegs._replace(Active_Power_Limit=RegSet(RegNum=40915,value=msg0))
                    if (self.inputHoldingRegs.Active_Power_Limit.value != self.holdingRegs.Active_Power_Limit.value) : 
                        self.logger.info("Request to Write type <%s>" %str(RegtypeW[i]))
                        self.values=msgval
                        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.defaultInitalReg, self.defaultNumOfRegs,self.values, self.signedDefault)
                        repMsg = self.sendModbusRequest(self.command)
                        self.exitandcheckvalue(repMsg)
                    else:
                        self.logger.info("Requested to Write type <%s> -Value already written-" %str(RegtypeW[i]))
                        
                    
                elif(RegtypeW[i]=='On/Off'):                               
                    self.defaultInitalReg = self.inputHoldingRegs.On_Off.RegNum      #Register for On/Off Fast shut-down
                    self.defaultNumOfRegs = 2 
                    'Read before Write' 
                    self.logger.info("Request to Read type <%s>" %str(RegtypeW[i]))
                    self.command = CommandFormat(ModbusCommands.READMULTI_HOLDINGREGS, self.defaultInitalReg , self.defaultNumOfRegs ,self.dummyValue, self.signedDefault)    
                    repMsg = self.sendModbusRequest(self.command)
                    self.exitandcheckvalue(repMsg)
                    'Write'
                    #if(==):                         Reason why start or stop the inverter (to be implemented)
                    msgval = [0, 1467]               #Start AC+DC side=1467   Stop DC side=381 Full Stop AC+DC side=1749                              
                    msg0=(msgval[0]*65536+msgval[1])
                    'Storing writing values for later usage'
                    self.inputHoldingRegs = self.inputHoldingRegs._replace(On_Off=RegSet(RegNum=41253,value=msg0))
                    if (self.inputHoldingRegs.On_Off.value != self.holdingRegs.On_Off.value) : 
                        self.logger.info("Request to Write type <%s>" %str(RegtypeW[i]))
                        self.values=msgval
                        self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS, self.defaultInitalReg, self.defaultNumOfRegs,self.values, self.signedDefault)
                        repMsg = self.sendModbusRequest(self.command)
                        self.exitandcheckvalue(repMsg)
                    else:
                        self.logger.info("Requested to Write type <%s> -Value already written-" %str(RegtypeW[i]))
                    
              
    def sendModbusRequest(self, requestMsg):         
        rep = None                                            #Init to invalid response value
        try:
            self.modbusReqPort.send_pyobj(requestMsg)
            rep = self.modbusReqPort.recv_pyobj()
        except PortError as e:
            self.logger.info("on_clock:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_clock: port error received")
        return rep
    
    def exitandcheckvalue(self,repmsg):   
        if (repmsg != None):                                 #Check in  both READ/WRITE case  
            Cmsg=self.registertable(repmsg)                  #Take input repMsg and receive d in Cmsg or return MsgVal again
            self.logger.info("Converted values :::::LOADING::::: to the logger" )
            self.tx_modbusTCPData.send_pyobj(Cmsg)           #Send Log data values to the logger
            if (repmsg ==-1):
                    self.logger.info("Modbus not ready error level at on_RepPort(Device)" )
            if (repmsg ==999):
                    self.logger.info("Modbus not ready to Read/Write error level at Function SendModbusCommand(Device)" )
            elif (repmsg ==-9999):
                    self.logger.info("Modbus not ready error level at Function ReadMultiHoldingRegisters(Library)" )     
            elif (repmsg ==-9990):
                    self.logger.info("Modbus not ready error level at Function WritingHoldingRegisters(Library)" )    
        else:
            self.logger.info("Modbus either not ready or no value read")   
            
    def registertable(self, Msgval):                                           #Function recognize the register and correct the values
        
        if (self.defaultInitalReg==self.holdingRegs.Plant_mains_connection.RegNum and self.defaultNumOfRegs==2):   #READ part Connection type
            msg0=(Msgval[0]*65535+Msgval[1])                                   #30881 and 30882 Connection type 
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(Plant_mains_connection=RegSet(RegNum=30881,value=msg0))
            if (msg0==1779):
                text='Separated'
            elif (msg0==1780):
                text='Public electricity mains'  
            elif (msg0==1781):
                text='Island mains'
            else:
                text='UNKNOWN'
            d = {"Plant mains connection ":text} 
        
        elif (self.defaultInitalReg==self.holdingRegs.DC_Current.RegNum and self.defaultNumOfRegs==6):   #READ part DC values
            msg0=round((Msgval[0]*65536+Msgval[1])*0.001,2)                    #30769 and 30770 DC input Current 
            msg1=round((Msgval[2]*65536+Msgval[3])*0.01,2)                     #30771 and 30772 DC input Voltage
            msg2=Msgval[4]*65536+Msgval[5]                                     #30773 and 30774 DC input Power   
            'Correction values when inverter is turned off'
            if (msg2==2147483648):                                             #Correction values when inverter is turned off   
                msg1=msg2=msg3=0
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(DC_Current=RegSet(RegNum=30769,value=msg0))
            self.holdingRegs = self.holdingRegs._replace(DC_Voltage=RegSet(RegNum=30771,value=msg1))
            self.holdingRegs = self.holdingRegs._replace(DC_Power=RegSet(RegNum=30773,value=msg2))
            d = {"DC Power [W]":msg2,
                 "DC Voltage [V]":msg1,
                 "DC Current [A]":msg0}                 
        
        elif (self.defaultInitalReg==self.holdingRegs.AC_Active_Power.RegNum and self.defaultNumOfRegs==46):  #READ part AC1 values
            msg0=(Msgval[0]*65535+Msgval[1])                                    #30775 and 30776 AC Active Power
            msg1=(Msgval[2]*65535+Msgval[3])                                    #30777 and 30778 Active Power L1
            msg2=(Msgval[4]*65535+Msgval[5])                                    #30779 and 30780 Active Power L2
            msg3=(Msgval[6]*65535+Msgval[7])                                    #30781 and 30782 Active Power L3
            msg4=round((Msgval[8]*65535+Msgval[9])*0.01,2)                      #30783 and 30784 Grid Voltage L1
            msg5=round((Msgval[10]*65535+Msgval[11])*0.01,2)                    #30785 and 30786 Grid Voltage L2
            msg6=round((Msgval[12]*65535+Msgval[13])*0.01,2)                    #30787 and 30788 Grid Voltage L3
            msg7=round((Msgval[20]*65535+Msgval[21])*0.001,2)                   #30795 and 30796 Tot Grid Current        
            msg8=round((Msgval[28]*65535+Msgval[29])*0.01,2)                    #30803 and 30804 Grid Frequency
            msg9=(Msgval[30]-65535)*65535-(65535-Msgval[31])                    #30805 and 30806 Tot Reactive pow 
            msg10=(Msgval[32]-65535)*65535-(65535-Msgval[33])                   #30807 and 30808 Reactive Power L1
            msg11=(Msgval[34]-65535)*65535-(65535-Msgval[35])                   #30809 and 30810 Reactive Power L2
            msg12=(Msgval[36]-65535)*65535-(65535-Msgval[37])                   #30811 and 30812 Reactive Power L3                           
            msg13=(Msgval[38]*65536+Msgval[39])                                 #30813 and 30814 Tot Apparent Power
            msg14=(Msgval[40]*65536+Msgval[41])                                 #30815 and 30816 Apparent Power L1 
            msg15=(Msgval[42]*65536+Msgval[43])                                 #30817 and 30818 Apparent Power L2 
            msg16=(Msgval[44]*65536+Msgval[45])                                 #30819 and 30820 Apparent Power L3    
            'Correction values when inverter is turned off'
            if (msg0==0 or msg0==2147483648 or msg0==2147450880 and msg1==2147450880 or msg10==-4294901760):        
                msg0=msg1=msg2=msg3=msg4=msg5=msg6=msg7=msg8=msg9=msg10=msg11=msg12=msg13=msg14=msg15=msg16=0
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(AC_Active_Power=RegSet(RegNum=30775,value=msg0))
            self.holdingRegs = self.holdingRegs._replace(AC_Active_Power_phase_L1=RegSet(RegNum=30777,value=msg1))
            self.holdingRegs = self.holdingRegs._replace(AC_Active_Power_phase_L2=RegSet(RegNum=30779,value=msg2))   
            self.holdingRegs = self.holdingRegs._replace(AC_Active_Power_phase_L3=RegSet(RegNum=30781,value=msg3))
            self.holdingRegs = self.holdingRegs._replace(AC_Voltage_phase_L1=RegSet(RegNum=30783,value=msg4))
            self.holdingRegs = self.holdingRegs._replace(AC_Voltage_phase_L2=RegSet(RegNum=30785,value=msg5))
            self.holdingRegs = self.holdingRegs._replace(AC_Voltage_phase_L3=RegSet(RegNum=30787,value=msg6))
            self.holdingRegs = self.holdingRegs._replace(AC_Grid_Current=RegSet(RegNum=30795,value=msg7))
            self.holdingRegs = self.holdingRegs._replace(AC_Grid_Frequency=RegSet(RegNum=30803,value=msg8))
            self.holdingRegs = self.holdingRegs._replace(AC_Reactive_Power=RegSet(RegNum=30805,value=msg9))
            self.holdingRegs = self.holdingRegs._replace(AC_Reactive_Power_phase_L1=RegSet(RegNum=30807,value=msg10))
            self.holdingRegs = self.holdingRegs._replace(AC_Reactive_Power_phase_L2=RegSet(RegNum=30809,value=msg11))
            self.holdingRegs = self.holdingRegs._replace(AC_Reactive_Power_phase_L3=RegSet(RegNum=30811,value=msg12))
            self.holdingRegs = self.holdingRegs._replace(AC_Apparent_Power=RegSet(RegNum=30813,value=msg13))
            self.holdingRegs = self.holdingRegs._replace(AC_Apparent_Power_phase_L1=RegSet(RegNum=30815,value=msg14))
            self.holdingRegs = self.holdingRegs._replace(AC_Apparent_Power_phase_L2=RegSet(RegNum=30817,value=msg15))
            self.holdingRegs = self.holdingRegs._replace(AC_Apparent_Power_phase_L3=RegSet(RegNum=30819 ,value=msg16))
            d = {"AC Grid Frequency [Hz]":msg8,
                 "AC Active Power [W]":msg0,
                 "AC Active Power phase L1 [W]":msg1,
                 "AC Active Power phase L2 [W]":msg2,
                 "AC Active Power phase L3 [W]":msg3,
                 "AC Reactive Power [VAr]":msg9,
                 "AC Reactive Power phase L1 [VAr]":msg10,
                 "AC Reactive Power phase L2 [VAr]":msg11,
                 "AC Reactive Power phase L3 [VAr]":msg12,
                 "AC Apparent Power [VA]":msg13,
                 "AC Apparent Power phase L1 [VA]":msg14,
                 "AC Apparent Power phase L2 [VA]":msg15,
                 "AC Apparent Power phase L3 [VA]":msg16,
                 "AC Voltage phase L1 [V]":msg4,
                 "AC Voltage phase L2 [V]":msg5,
                 "AC Voltage phase L3 [V]":msg6,
                 "AC Grid Current [A]":msg7}

        elif (self.defaultInitalReg==self.holdingRegs.AC_Grid_Current_phase_L1.RegNum and self.defaultNumOfRegs==6):   #READ part AC2 values
            msg0=round((Msgval[0]*65535+Msgval[1])*0.001,2)                     #30977 and 30978 Grid Current phase L1
            msg1=round((Msgval[2]*65535+Msgval[3])*0.001,2)                     #30979 and 30980 Grid Current phase L2
            msg2=round((Msgval[4]*65535+Msgval[5])*0.001,2)                     #30981 and 30982 Grid Current phase L3    
            'Correction values when inverter is turned off'
            if (msg0==2147450,880):                                             #Correction values when inverter is turned off
                msg0=msg1=msg2=0 
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(AC_Grid_Current_phase_L1=RegSet(RegNum=30977,value=msg0))
            self.holdingRegs = self.holdingRegs._replace(AC_Grid_Current_phase_L2=RegSet(RegNum=30979,value=msg1))
            self.holdingRegs = self.holdingRegs._replace(AC_Grid_Current_phase_L3=RegSet(RegNum=30981,value=msg2))                                                              
            d = {"AC Current phase L1 [A]":msg0,
                 "AC Current phase L2 [A]":msg1,
                 "AC Current phase L3 [A]":msg2}

        elif (self.defaultInitalReg==self.holdingRegs.Operating_Time.RegNum and self.defaultNumOfRegs==4):      #READ part Time values
            msg0=round((Msgval[0]*65536+Msgval[1])/3600,2)                      #30541 and 30542 Operating Time
            msg1=round((Msgval[2]*65536+Msgval[3])/3600,2)                      #30543 and 30544 Feed in time
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(Operating_Time=RegSet(RegNum=30541,value=msg0))
            self.holdingRegs = self.holdingRegs._replace(Feed_in_time=RegSet(RegNum=30543,value=msg1))
            d = {"Operating Time [h]":msg0,
                 "Feed in time [h]":msg1}
        
        elif (self.defaultInitalReg==self.holdingRegs.Total_yeld.RegNum and self.defaultNumOfRegs==8):      #READ part Energy values
            msg0=round((Msgval[0]*65536+Msgval[1])*0.000001,6)                  #30529 and 30530 Total Yeld
            msg1=round((Msgval[6]*65536+Msgval[7]),2)                           #30535 and 30536 Daily Yeld 
            'Storing values for later usage'
            self.holdingRegs = self.holdingRegs._replace(Total_yeld=RegSet(RegNum=30529,value=msg0))
            self.holdingRegs = self.holdingRegs._replace(Daily_yeld=RegSet(RegNum=30535,value=msg1))
            d = {"Daily yeld [Wh]":msg1,
                "Total yeld [MWh]":msg0}
                
        elif (self.defaultInitalReg==self.holdingRegs.Grid_Guard_Code.RegNum and self.defaultNumOfRegs==2):   #WRITE/READ part GridGuardCode 
            try:                                                                #For Read format values
                msg0=(Msgval[0]+Msgval[1])            
                'Storing values for later usage'
                self.holdingRegs = self.holdingRegs._replace(Grid_Guard_Code=RegSet(RegNum=43090,value=msg0))                 
                if (msg0==0):
                    text='Valid'                                                #To be changed to 'INVALID' when the Firmware by SMA is updated  
                else:
                    text='Valid' 
                d = {"Grid Guard Code ":text}
            except :                                                            #For Write format values
                msg0=Msgval
                if (msg0==2):
                    text='Successfully'
                else:
                    text='Failed'    
                d = {"Grid Guard Code just sent :::: ":text}             
            
        elif (self.defaultInitalReg==self.holdingRegs.Language.RegNum and self.defaultNumOfRegs==2):    #WRITE/READ part Language                                
            try:                                                                #For Read format values
                msg0=(Msgval[0]*65536+Msgval[1])                                #40013 and 40014 Language (777=German), (778=English), (779=Italian)
                'Storing values for later usage'
                self.holdingRegs = self.holdingRegs._replace(Language=RegSet(RegNum=40013,value=msg0))
                if (msg0==777): 
                    text='Deutsch'
                elif (msg0==778): 
                    text='English'                               
                elif (msg0==779): 
                    text='Italiano'                
                else:
                    text='UNKNOWN'
                d = {"Language ":text}
            except :                                                              #For Write format values                                 
                msg0=Msgval
                if (msg0==2):
                    text='Successfully'
                else:
                    text='Failed'
                d = {"Change Language Command just sent ":text}                                                                        
        elif (self.defaultInitalReg==self.holdingRegs.Operating_mode_relay.RegNum and self.defaultNumOfRegs==2):   #WRITE/READ part Operating mode for multi-function relay 
            try:                                                                  #For Read format values                                                             
                msg0=(Msgval[0]*65536+Msgval[1])                                
                'Storing values for later usage'
                self.holdingRegs = self.holdingRegs._replace(Operating_mode_relay=RegSet(RegNum=40575,value=msg0))
                if (msg0==258): 
                    text='Switching status grid relay'
                elif (msg0==1341): 
                    text='Fault indication'                               
                elif (msg0==1342): 
                    text='Fan control'
                elif (msg0==1343): 
                    text='Self-consumption'
                elif (msg0==1349): 
                    text='Control via communication'                               
                elif (msg0==1359): 
                    text='Battery bank'                                  
                else:
                    text='UNKNOWN'
                d = {"Multi-function relay mode ":text}
            except :                                                              #For Write format values
                msg0=Msgval
                if (msg0==2):
                    text='Successfully'
                else:
                    text='Failed'
                d = {"Change mode for relay Command just sent ":text}
        
        elif (self.defaultInitalReg==self.holdingRegs.Active_Power_Limit.RegNum and self.defaultNumOfRegs==2):   #WRITE/READ part Active power Limit 
             
            try:                                                           #For Read format values
                msg0=(Msgval[0]*65536+Msgval[1])                           #Converted to 1 value for comparison reason                                             #41255 Active power limitation in %
                'Storing values for later usage'
                self.holdingRegs = self.holdingRegs._replace(Active_Power_Limit=RegSet(RegNum=40915,value=msg0))                               
                d = {"Active power limitation in [W] ":msg0}
            except:                                                         #For Write format values
                msg0=Msgval
                if (msg0==2):
                    text='Successfully'
                else:
                    text='Failed'    
                d = {"Change Active Power Limit Command just sent":text} 
            
        
        elif (self.defaultInitalReg==self.holdingRegs.On_Off.RegNum and self.defaultNumOfRegs==2):   #WRITE/READ part On/Off 
                                                
            try:                                                            #For Read format values
                msg0=(Msgval[0]*65536+Msgval[1])                            #41253 (381=Stop), (1749=Full-stop) (1467=Start)
                'Storing values for later usage'
                self.holdingRegs = self.holdingRegs._replace(On_Off=RegSet(RegNum=41253,value=msg0))
                if (msg0==381): 
                    text='Stop DC side'
                elif (msg0==1749): 
                    text='Full-stop AC+DC side'                               
                elif (msg0==1467): 
                    text='Start'              
                else:
                    text='UNKNOWN'
                d = {"Fast Start/Shut-down set to ":text}
            except :                                                         #For Write format values
                msg0=Msgval
                if (msg0==2):
                    text='Successfully'
                else:
                    text='Failed'    
                d = {"Change Start/Shut-down Command just sent ":text}                                                                                         
          
        else: 
            text=self.defaultInitalReg
            d= {"...UNKNOWN REGISTER SELECTED...":text}
        #print(self.holdingRegs)
        #print (self.inputHoldingRegs)
        return d
    
    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)