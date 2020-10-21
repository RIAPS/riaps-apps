# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import capnp
import distributedvoltage_capnp
import time
# riaps:keep_import:end

class Gateway(Component):

    # riaps:keep_constr:begin
    def __init__(self, Ts, ip):
        super(Gateway, self).__init__()
        
        self.ip = ip
        self.Ts = Ts
        
        self.frequency = 0
        self.voltageMag = 0
        self.activePower = 0
        self.reactivePower = 0
        
        self.otherVoltage_delay10 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay9 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay8 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay7 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay6 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}   
        self.otherVoltage_delay5 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay4 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay3 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay2 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.otherVoltage_delay1 = {111:(0,0,0),112:(0,0,0),113:(0,0,0),114:(0,0,0),115:(0,0,0)}
        self.dataValues = { }
        
        
        self.start_stop     = 0 
        self.islanding_mode = 0      
        self.sec_en   = 0 
        self.angle_en = 0            
        self.delay_changed = 0
        self.ratio_reset = 0      

        self.OMEGASecondaryControlVariable = 0
        self.eSecondaryControlVariable = 0
        self.VoltInteLaplace = 0
        self.Volt_Estimated = 0
        self.RatioInteLaplace = 0
        self.Ratio_Estimated = 0
        self.RatioZInteLaplace = 0
        self.RatioZ_Estimated = 0   
        self.average_voltage = 0
        self.RatioZ_Estimated = 0
        self.RatioZ = 0
        
        self.display_counter_Q  = 0
        self.accurate_v = 0
        
        self.sync_onetwo_signal = 0
        self.sync_cnt = 0
        
    # riaps:keep_constr:end

    # riaps:keep_currentvoltage:begin
    def on_currentvoltage(self):
        bytes = self.currentvoltage.recv()
        msg = distributedvoltage_capnp.Voltage.from_bytes(bytes)

        timestamp = msg.time
        values    = msg.values

        s_time = f'{timestamp.tvSpec}'
        ns_time = f'{timestamp.tvNspec}'
        #for i in values:
        #    s = f'{s} {i} at {timestamp.tvSpec}.{timestamp.tvNspec}'
        #self.logger.info("values arrived: %s" % s)
        #pass
        
        frequency, voltageMag, activePower, reactivePower = values
        self.frequency = 365 + 25*frequency/65535
        self.voltageMag = 250 + 250*voltageMag/65535
        self.activePower = (activePower - 32768)*10
        self.reactivePower =(reactivePower - 32768)*10
         
        #print(f'values are {self.frequency}, {self.voltageMag}, {self.activePower}, {self.reactivePower}at {timestamp.tvSpec}.{timestamp.tvNspec}')
    
        if (len(self.dataValues) != 0):
            sum_ReactivePower = 0.0
            sum_negReactivePower = 0.0
            sum_OMEGASecondaryControlVariable = 0;
            sum_average_voltage = self.voltageMag
            sum_number_of_data = 1
            sum_VoltEstimated = 0
            sum_RatioEstimated = 0
            sum_RatioZ_Estimated = 0
        
            if self.display_counter_Q == 20:
                self.display_counter_Q = 0
                print("local voltage %f, average V %f, estimated V %f , estimate raio %f, estimate raio %f" %( self.voltageMag, self.average_voltage,self.Volt_Estimated, self.Ratio_Estimated, self.RatioZ_Estimated )) 
                print("data list %s" % str(self.dataValues))
            self.display_counter_Q = self.display_counter_Q + 1
            

            #for other_id, (otherValue_OMEAG, otherValue_ReactivePower) in self.dataValues.items():
            for other_id,(otherValue_OMEAG, otherValue_ReactivePower, otherValue_voltageMag, otherValue_RatioEstimated, otherValue_RatioZ) in self.dataValues.items():

                # average voltage
                sum_average_voltage += otherValue_voltageMag
                sum_number_of_data  += 1

              
                #power sharing 
                sum_OMEGASecondaryControlVariable += (self.activePower - otherValue_OMEAG)
                sum_ReactivePower += (self.reactivePower - otherValue_ReactivePower)

                
                # voltage estimation
                sum_VoltEstimated += (self.Volt_Estimated - otherValue_voltageMag)

                sum_RatioEstimated += (self.Ratio_Estimated - otherValue_RatioEstimated)   
                
                sum_RatioZ_Estimated += (self.RatioZ_Estimated - otherValue_RatioZ)  
                
            self.average_voltage = sum_average_voltage/sum_number_of_data
            
            self.dataValues.clear()
            
            der_OMEGASecondaryControlVariable = ( 5*(self.frequency-376.9911184) * self.sec_en + sum_OMEGASecondaryControlVariable*0.0003) * self.Ts
            
            der_ReactivePower = ( ((self.average_voltage-392))*10  + 0.001*sum_ReactivePower) * self.Ts * self.sec_en
            
            if self.ip == 111:
                nom = 0.25
            else :
                nom = 0.5
            der_VoltEstimated = 0.2*sum_VoltEstimated*nom    
            der_RatioEstimated = 0.2*sum_RatioEstimated*nom   
            der_RatioZEstimated = 0.2*sum_RatioZ_Estimated*nom 
            
            self.OMEGASecondaryControlVariable -= der_OMEGASecondaryControlVariable
            self.eSecondaryControlVariable -= der_ReactivePower
            
            self.VoltInteLaplace -= der_VoltEstimated

            
            self.RatioInteLaplace -= der_RatioEstimated
            self.RatioZInteLaplace -= der_RatioZEstimated
            
            if ( self.sec_en == 1):
                self.Ratio_Estimated = self.RatioInteLaplace + 1
                self.Volt_Estimated = self.voltageMag + self.VoltInteLaplace
                self.RatioZ_Estimated = self.RatioZ + self.RatioZInteLaplace
            
            
            if (self.sec_en == 0):
                self.OMEGASecondaryControlVariable = 0
                self.eSecondaryControlVariable = 0
                self.VoltInteLaplace = 0
                self.Volt_Estimated = 0
                self.RatioInteLaplace = 0
                self.Ratio_Estimated = 0
                self.RatioZInteLaplace = 0
                self.RatioZ_Estimated = 0
            
            if self.ratio_reset == 1:
                self.RatioInteLaplace = 0
                self.Ratio_Estimated = 0


            '''Write all holding registers'''       
            '''
            OMEGAToModbus = int( round ( ( (self.OMEGASecondaryControlVariable)*0+25  )*65535/50))
            if (OMEGAToModbus > 65535):
                OMEGAToModbus = 65535
            elif (OMEGAToModbus < 0):
                OMEGAToModbus = 0
                
            eToModbus = int( round ( ( (self.eSecondaryControlVariable)*0+250 )*65535/500 ) )
            if (eToModbus > 65535):
                eToModbus = 65535
            elif (eToModbus < 0):
                eToModbus = 0
            
            
            GToModbus = int( round ( self.G_integral*0 *65535/200 ) )
            if (GToModbus > 65535):
                GToModbus = 65535
            elif (GToModbus < 0):
                GToModbus = 0
                   
                
            status = self.start_stop
            
            if (self.islanding_mode == 1):
                status = status + 2
            
            if (self.sec_en == 1):
                status = status + 4

            if debugMode:
                self.logger.info("modbus command : %s" % str(status))
            
            self.values = [status, OMEGAToModbus, eToModbus, GToModbus]
            #self.values = [status, OMEGAToModbus, eToModbus, GToModbus]
            self.command = CommandFormat(ModbusCommands.WRITEMULTI_HOLDINGREGS,0,4,self.values,self.defaultNumOfDecimals,self.signedDefault)
            
            on_clock_modbus_command_start = time.time() 

            repMsg = self.sendModbusRequest(self.command)
        
            # Check if the Modbus Response is valid
            #if repMsg == -1 or repMsg == -9999:
            if repMsg == None:
                self.logger.info("Modbus either not ready")

            on_clock_modbus_command_end = time.time() 
        
            #self.debug_counter = self.debug_counter +1
            '''
            
        '''
            if (self.ip == 111):
                msg = (self.ip, now, self.activePower, self.reactivePower, self.eSecondaryControlVariable, self.estimateVoltage_delay4, self.negReactivePower)
                self.estimateVoltage_delay10 = self.estimateVoltage_delay9
                self.estimateVoltage_delay9 = self.estimateVoltage_delay8
                self.estimateVoltage_delay8 = self.estimateVoltage_delay7
                self.estimateVoltage_delay7 = self.estimateVoltage_delay6
                self.estimateVoltage_delay6 = self.estimateVoltage_delay5                
                self.estimateVoltage_delay5 = self.estimateVoltage_delay4
                self.estimateVoltage_delay4 = self.estimateVoltage_delay3
                self.estimateVoltage_delay3 = self.estimateVoltage_delay2
                self.estimateVoltage_delay2 = self.estimateVoltage_delay1
                self.estimateVoltage_delay1 = self.Volt_Estimated
            else:
        '''
        

        if self.sync_cnt >= 119 :
            self.sync_cnt = 0 
        
        if self.sync_cnt < 60 :
            self.sync_onetwo_signal = 1
        else:
            self.sync_onetwo_signal = 2

        self.sync_cnt = self.sync_cnt + 1
        
        now = time.time()

        msg = (self.ip, now, self.activePower, self.reactivePower, self.eSecondaryControlVariable, self.Volt_Estimated, self.Ratio_Estimated, self.RatioZ_Estimated, self.sync_cnt)
        self.thisReady.send_pyobj(msg)
            
        #self.logger.info("secondary controller update: fre %f and ang_diff %f", self.frequency, self.VoltageAngleDiff)
           


           
        try:  

            #time_modbus_mea = on_clock_modbus_measurement_end_and_algorithm_start - on_clock_modbus_measurement_start
            #time_modbus_com = on_clock_modbus_command_end - on_clock_modbus_command_start
            #time_all  = on_clock_end - on_clock_start
            #time_algorithm  = time_all - time_modbus_mea - time_modbus_com
            
            filename = "t_cal_%s" % str(self.ip)
            file = open(filename, "a")
            file.write(s_time +'     ' + ns_time+'     '+str(self.Volt_Estimated) +'     '+ str(self.Ratio_Estimated) +'     ' + str(self.accurate_v) +'     '+str(self.delay_changed)+'     '+str(self.RatioZ_Estimated)+'     '+str(self.RatioZ)+'     '+str(self.sync_onetwo_signal)+'     '+str(self.voltageMag) +'\n')
            file.close()
            #self.logger.info("t cal: total %f, m_m %f, m_c %f, al %f", time_all, time_modbus_mea, time_modbus_com, time_algorithm)
        except UnboundLocalError:
            pass
        


    def on_nodeReady(self):
        msg = self.nodeReady.recv_pyobj()  # Receive (actorID,timestamp,value)
        #self.logger.info("on_otherReady():%s",str(msg))
        otherId,otherTimestamp,otherValue_OMEAG,otherValue_ReactivePower,otherValue_e, otherValue_voltageMag, otherValue_Ratio, otherValue_RatioZ, otherSync_cnt= msg #otherValue_ReactivePower
        now = time.time()
        '''
        if (otherId == 112 and self.ip == 111):                           
                    try:  
                                time_all = now - otherTimestamp
                                filename= "comm_time%s_112" % str(self.ip)
                                file = open(filename, "a")
                                file.write(str(time_all)+'\n')
                                file.close()
                    except UnboundLocalError:
                                pass
        elif (otherId == 113 and self.ip == 111):                           
                    try:  
                                time_all = now - otherTimestamp
                                filename= "comm_time%s_113" % str(self.ip)
                                file = open(filename, "a")
                                file.write(str(time_all)+'\n')
                                file.close()
                    except UnboundLocalError:
                                pass
        elif (otherId == 114 and self.ip == 111):                           
                    try:  
                                time_all = now - otherTimestamp
                                filename= "comm_time%s_114" % str(self.ip)
                                file = open(filename, "a")
                                file.write(str(time_all)+'\n')
                                file.close()
                    except UnboundLocalError:
                                pass     
        elif (otherId == 115 and self.ip == 111):                           
                    try:  
                                time_all = now - otherTimestamp
                                filename= "comm_time%s_115" % str(self.ip)
                                file = open(filename, "a")
                                file.write(str(time_all)+'\n')
                                file.close()
                    except UnboundLocalError:
                                pass    
        '''
                        
        if (otherId != self.ip): #self.uuid was used for general operation
            
            

            
            self.otherVoltage_delay10[otherId] = self.otherVoltage_delay9[otherId]
            self.otherVoltage_delay9[otherId] = self.otherVoltage_delay8[otherId]
            self.otherVoltage_delay8[otherId] = self.otherVoltage_delay7[otherId]
            self.otherVoltage_delay7[otherId] = self.otherVoltage_delay6[otherId]
            self.otherVoltage_delay6[otherId] = self.otherVoltage_delay5[otherId]
            self.otherVoltage_delay5[otherId] = self.otherVoltage_delay4[otherId]
            self.otherVoltage_delay4[otherId] = self.otherVoltage_delay3[otherId]
            self.otherVoltage_delay3[otherId] = self.otherVoltage_delay2[otherId]
            self.otherVoltage_delay2[otherId] = self.otherVoltage_delay1[otherId]
            self.otherVoltage_delay1[otherId] = (otherValue_voltageMag, otherValue_Ratio, otherValue_RatioZ)
        
            if otherId == 111:
                self.sync_cnt = otherSync_cnt
                
                
            if self.ip == 111:
                if otherId == 112 or otherId == 113:
                
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    else:
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])
                elif otherId == 114: 
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    elif (self.delay_changed == 1):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])                           
                elif otherId == 115:                                  
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])   
                    else:
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])
                        
            elif self.ip == 112:
                if otherId == 111 :
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    else :
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])
                
                elif otherId == 113:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                '''
                elif otherId == 114:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1])
                '''    
            elif self.ip == 113:
                if otherId == 111 :
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    else:
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])
                
                elif otherId == 112:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                '''
                elif otherId == 115:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay6[otherId][0], self.otherVoltage_delay6[otherId][1])    
                '''    
            elif self.ip == 114:
                if otherId == 111:
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    elif (self.delay_changed == 1):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])

                elif otherId == 115 :
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                
                '''
                elif  otherId == 112:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1])
                '''

            elif self.ip == 115:
                if otherId == 111 :
                    if (self.delay_changed == 0):
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                    else:
                        self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay4[otherId][0], self.otherVoltage_delay4[otherId][1], self.otherVoltage_delay4[otherId][2])
                        
                elif otherId == 114 :
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay2[otherId][0], self.otherVoltage_delay2[otherId][1], self.otherVoltage_delay2[otherId][2])
                
                '''
                elif otherId == 114 or otherId == 113:
                    self.dataValues[otherId] = (otherValue_OMEAG, otherValue_ReactivePower, self.otherVoltage_delay6[otherId][0], self.otherVoltage_delay6[otherId][1])    
                '''
            
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
        '''
        if ( data['DIGITALS2'] == 1 ):
            self.RatioZ  = 1             
        elif ( data['DIGITALS2'] == 2 ):
            self.RatioZ  = 2 
        else:
            self.breaker2_open   = 0 
            self.breaker3_close = 0
        '''        
        
        self.RatioZ  = data['DIGITALS2']
        '''
        if ( data['DIGITALS3'] == 7 ):
            self.breaker1_is_closed = 1 
            self.breaker2_is_closed = 1       
            self.breaker3_is_closed = 1      
        elif ( data['DIGITALS3'] == 3 ):
            self.breaker1_is_closed = 1 
            self.breaker2_is_closed = 1       
            self.breaker3_is_closed = 0         
        elif ( data['DIGITALS3'] == 5 ):
            self.breaker1_is_closed = 1 
            self.breaker2_is_closed = 0       
            self.breaker3_is_closed = 1            
        elif ( data['DIGITALS3'] == 2 ):
            self.breaker1_is_closed = 0 
            self.breaker2_is_closed = 1       
            self.breaker3_is_closed = 0
        elif ( data['DIGITALS3'] == 4 ):
            self.breaker1_is_closed = 0 
            self.breaker2_is_closed = 0       
            self.breaker3_is_closed = 1             
        elif ( data['DIGITALS3'] == 6 ):
            self.breaker1_is_closed = 0 
            self.breaker2_is_closed = 1       
            self.breaker3_is_closed = 1             
        elif ( data['DIGITALS3'] == 1 ):
            self.breaker1_is_closed = 1 
            self.breaker2_is_closed = 0       
            self.breaker3_is_closed = 0             
        else:
            self.breaker1_is_closed = 0 
            self.breaker2_is_closed = 0       
            self.breaker3_is_closed = 0      
        
        
        #self.logger.info("Receive digi1 command from 110: %s and sec_en %f",str(data['DIGITALS1']), self.sec_en)
        '''
        self.accurate_v = data['vuf1']
        
        if ( data['DIGITALS3'] == 1 ):
            self.delay_changed = 1 
            self.ratio_reset = 0 
        elif( data['DIGITALS3'] == 2 ):
            self.delay_changed = 0
            self.ratio_reset = 1             
        elif ( data['DIGITALS3'] == 3 ):
            self.delay_changed = 1 
            self.ratio_reset = 1 
        else:
            self.delay_changed = 0
            self.ratio_reset = 0    
# riaps:keep_currentvoltage:end

# riaps:keep_impl:begin

# riaps:keep_impl:end