from riaps.run.comp import Component
import logging
import numpy
import math
import time
from xlrd import open_workbook
    
EXCEL_FILE = "H_matrix_RTDS.xlsx"

GROUP_MAP = dict()

#Group 1
V_mea = [1,2,3,4,5,6]
I_ij = [None, 2, 5, None, None, 6, None, None]
I_ji = [3, None, 25, 9, 7, None, 8, 11]

GROUP_MAP[1] = [V_mea, I_ij, I_ji]

#Group 2
V_mea = [4,7,8,9,10,2,3,5,14,11]
I_ij = [None, 6, None, 10, None, None, 23, None, None, 19]
I_ji = [9, None, 8, None, 22, 24, None, 20, 18, None]

GROUP_MAP[2] = [V_mea, I_ij, I_ji]

#Group 3
V_mea = [6,11,12,13,14,5,9,10]
I_ij = [None, None, 12, None, None, 19, 13, 15]
I_ji = [11, 17, None, 14, 18, None, None, None]

GROUP_MAP[3] = [V_mea, I_ij, I_ji]
    
#Decentralized
V_mea = range(1,15)
I_ij = [None, 2, 3, None, None, 6, None, 8, None, None, None, 12, None, None, 15, None, None, 18, 19, 20]
I_ji = [1, None, 3, 4, 5, None, 7, None, 9, 10, 11, None, 13, 14, None, 16, 17, None, None, None]

GROUP_MAP[0] = [V_mea, I_ij, I_ji]
    
class Group(Component):
    def __init__(self, group_no):
        super(Group, self).__init__()
        self.group_no = group_no
        self.V = None
        self.I = None
        self.H = self.get_H_for_group()
        self.V_mea, self.I_ij, self.I_ji = GROUP_MAP[group_no]
        self.inbus_received = True
        self.outbus_received = True

        self.logger.info("Initialized Component")
        
    def get_H_for_group(self):
        book = open_workbook(EXCEL_FILE)
        group_name = "Group" + str(self.group_no)
        if self.group_no == 0:
            group_name = "Whole Group"
        sheet = book.sheet_by_name(group_name)
        sheet_array = list()
        for row in sheet.get_rows():
                row_list = list()
                for x in row:
                        if x.ctype == 2:
                                row_list.append(x.value)
                        else:
                                row_list.append(0)
                sheet_array.append(row_list)
        return sheet_array
    
    def on_clock(self):
        msg = self.clock.recv_pyobj()
        self.logger.info("Clock event")
        start_time = time.time()
        self.calculate()
        time_taken = time.time() - start_time
        self.logger.info("Time taken: " + str(time_taken))
        
    def on_phasorPort(self):
        msg = self.phasorPort.recv_pyobj()
        self.logger.info(str(msg))
        if msg is not None:
            self.V, self.I = msg
            
    def calculate(self):
        if self.V is None or self.I is None:
            return None
        #create the Z matrix
        Z = list()
        for v in self.V_mea:
            if v is None:
                Z.append(None)
            else:
                v_phasor = self.V[v]
                Z.append(v_phasor.real)
        for v in self.V_mea:
            if v is None:
                Z.append(None)
            else:
                v_phasor = self.V[v]
                Z.append(v_phasor.imag)
        
        for i in self.I_ij:
            if i is None:
                Z.append(None)
            else:
                i_phasor = self.I[i]
                Z.append(i_phasor.real)
        for i in self.I_ij:
            if i is None:
                Z.append(None)
            else:
                i_phasor = self.I[i]
                Z.append(i_phasor.imag)
            
        for i in self.I_ji:
            if i is None:
                Z.append(None)
            else:
                i_phasor = self.I[i]
                Z.append(i_phasor.real)
        for i in self.I_ji:
            if i is None:
                Z.append(None)
            else:
                i_phasor = self.I[i]
                Z.append(i_phasor.imag)
            
        #the Z matrix is created, now we need to get the actual H matrix
        H = list()
        for i in range(len(Z)):
            if Z[i] is None:
                Z[i] = 0
                H.append([0 for j in range(len(self.H[i]))])
            else:
                H.append(self.H[i])
                
        self.logger.info("H: " + str(numpy.asarray(H).T))
        
                
        Z = numpy.reshape(Z, (len(Z), -1))
        H = numpy.asarray(H)
        prod1 = numpy.dot(H.T, H)
        prod1 = numpy.linalg.inv(prod1)
        prod2 = numpy.dot(prod1, H.T)
        X = numpy.dot(prod2, Z)
        self.logger.info(str(Z))
        self.logger.info(str(numpy.dot(H, X)))
        
        result = Z - numpy.dot(H, X)
        final_error = math.sqrt(sum([x ** 2 for x in result]))
        self.logger.info("FINAL RESULT " + str(final_error))
        
        
        