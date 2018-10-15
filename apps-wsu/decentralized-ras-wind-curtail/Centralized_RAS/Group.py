from riaps.run.comp import Component
from xlrd import open_workbook
import logging
import numpy

EXCEL_FILE = 'Variable.xlsx'
NUM_GROUPS = 4
WIND_FARM_NO = 3
TEMP_MID = {1:[], 2:[1,0,0], 3:[0,1,0], 4:[0,0,1]}

class Group(Component):
        def __init__(self, group_no):
                super(Group, self).__init__()
                self.group_no = group_no
                self.V = None
                self.I = None
                book = open_workbook(EXCEL_FILE)
                temp1 = get_sheet_array(book, "Temp")
                bb = get_sheet_array(book, "bb")
                self.H = get_sheet_array(book, "H")
                self.Temp = temp1[int((group_no - 1) * (len(temp1)/NUM_GROUPS)) : int(group_no * (len(temp1)/NUM_GROUPS))]
                self.b = bb[int((group_no - 1) * (len(temp1)/NUM_GROUPS)) : int(group_no * (len(temp1)/NUM_GROUPS))]
                self.minDict = dict()
                self.iteration = 0
                self.readyList = [0 for i in range(NUM_GROUPS)]
                self.A_dict = dict()
                
                self.logger.info("Group " + str(self.group_no) + " initialized")

        def on_phasorPort(self):
                msg = self.phasorPort.recv_pyobj()
                self.logger.info(str(msg))
                if msg is not None:
                    self.V, self.I = msg
                
        def calculatePG(self, v_index, i_index):
                v_vect = self.V[v_index]
                i_vect = self.I[i_index]
    
                res = v_vect * i_vect * 3
                return res.real

        def on_clock(self):
                msg = self.clock.recv_pyobj()
                self.ras()
                #self.logger.info(self.H)
                
        def ras(self):
                                
                PG_list.append(self.calculatePG(1, 1))
                PG_list.append(self.calculatePG(2, 4))
                PG_list.append(self.calculatePG(9, 21))
                PG_list.append(self.calculatePG(11, 16))
                
                self.H[1][0] = PG_list[1]
                self.H[8][1] = PG_list[2]
                self.H[10][2] = PG_list[3]
                self.H[0][3] = PG_list[0] - 1
                
                f = [j * -1 for j in PG_list[1:]] + [0]

                a1 = numpy.dot(self.Temp, self.H)
                a2 = numpy.asarray([j[:WIND_FARM_NO] for j in a1])
                if self.group_no == 1:
                    Temp_1 = numpy.concatenate((a2, (a2 * -1), [f[:WIND_FARM_NO]]))
                else:
                    Temp_1 = numpy.concatenate((a2, (a2 * -1), [TEMP_MID[self.group_no]], [f[:WIND_FARM_NO]]))
                
                a3 = numpy.asarray([[j[WIND_FARM_NO]] for j in a1])

                b1 = self.b - a3
                b2 = self.b + a3
                
                B = numpy.concatenate((b1, b2))

                if self.group_no == 1:
                    B = numpy.concatenate((B, [[0]]))
                else:
                    B = numpy.concatenate((B, [[1], [0]]))

                temp_size = [0, 10, 11, 11, 11]

                num_cons = 44

                if self.group_no == 1:
                        Temp_2_1 = numpy.concatenate((numpy.eye(temp_size[1]), numpy.zeros((temp_size[1], num_cons - temp_size[1]))), axis = 1) 


                if self.group_no == 2:
                        Temp_2_1 = numpy.concatenate((numpy.zeros((temp_size[2], temp_size[1])), numpy.eye(temp_size[2]), numpy.zeros((temp_size[2], num_cons - temp_size[2] - temp_size[1]))), axis = 1)

                if self.group_no == 3:
                        Temp_2_1 = numpy.concatenate((numpy.zeros((temp_size[3], temp_size[1] + temp_size[2])), numpy.eye(temp_size[3]), numpy.zeros((temp_size[3], num_cons - temp_size[3] - temp_size[2] - temp_size[1]))), axis = 1)

                if self.group_no == 4:
                        Temp_2_1 = numpy.concatenate((numpy.zeros((temp_size[4], temp_size[1] + temp_size[2] + temp_size[3])), numpy.eye(temp_size[4]), numpy.zeros((temp_size[4], 1))), axis = 1)


                Temp_2_2 = numpy.concatenate((numpy.zeros((1, num_cons - 1)), [[1.0]]), axis = 1)
                Temp_2 = numpy.concatenate((Temp_2_1, Temp_2_2))

                self.A = numpy.concatenate((Temp_1, Temp_2, B), axis = 1)
                self.x = min(self.A[-1])
                self.logger.info("A CALCULATED " + str(self.group_no))
                self.logger.info(self.A)

                self.A_dict = dict()

                self.readyPub.send_pyobj(self.group_no)


        def on_readySub(self):
                gr_index = self.readySub.recv_pyobj()
                self.readyList[gr_index - 1] = 1
                if (sum(self.readyList) == NUM_GROUPS):
                    self.readyList = [0 for i in range(NUM_GROUPS)]
                    self.logger.info("All groups are ready")
                    if (self.group_no == 1):
                        self.check_x(self.x)
                        


        def check_x(self, x):
                '''If x is less than 0, alert all the other groups to find pivot row and run gaussian elimination'''
                if x < 0:
                        self.n = find_element(self.A[-1], x)
                        self.logger.info("GROUP 1 INITIATING DISTRIBUTED CALCULATION")
                        self.indexPub.send_pyobj(self.n)
                else:
                        self.logger.info("DONE!! " + str(self.A))
                        self.indexPub.send_pyobj(-1)
                        

        def on_indexSub(self):
                self.n = self.indexSub.recv_pyobj()
                self.logger.info("RECEIVED N " + str(self.group_no) + " " + str(self.n))
                if self.n >= 0:
                    self.do_fpr()
                else:
                    self.completePub.send_pyobj([self.group_no, self.A])
                
        def do_fpr(self):
                self.logger.info(self.A)
                self.G, self.N, mini, self.pivot_row = find_pivot_row(self.A, self.n)
                minmsg = [self.group_no, mini, self.iteration]
                
                self.iteration += 1
                self.logger.info("ITERATION " + str(self.iteration))
                self.logger.info(minmsg)
                self.minPub.send_pyobj(minmsg)
                
        def on_minSub(self):
                min_group, min_val, i = self.minSub.recv_pyobj()
                self.logger.info("RECEIVED MIN " + str(min_group) + " " + str(min_val) + " " + str(i) )
                
                if i not in self.minDict.keys():
                    self.minDict[i] = [[min_group, min_val]]
                else:
                    self.minDict[i].append([min_group, min_val])
                    if len(self.minDict[i]) == NUM_GROUPS:
                        #Find the index of the group with the minimum value
                        self.logger.info(self.minDict)
                        minList = self.minDict[i]
                        minList.sort(key = lambda x: x[0]) #Sort the list to break ties in case of consensus
                        
                        min_index = minList[0][0]
                        min_value = minList[0][1]
                        for i in range(1, len(minList)):
                            if minList[i][1] < min_value:
                                min_value = minList[i][1]
                                min_index = i
                                    
                        self.logger.info("CONSENSUS REACHED " + str(min_index) + str(self.group_no))
                        if min_index == self.group_no:
                            self.pivotPub.send_pyobj([min_index, self.pivot_row])

        def on_pivotSub(self):
                k, received_pivot_row = self.pivotSub.recv_pyobj()
                self.do_ge(k, received_pivot_row)

        def do_ge(self, k, received_pivot_row):
                if k == self.group_no:
                        self.A = gaussian_elimination(self.A, self.G, self.N, self.n, received_pivot_row)
                else:
                        self.A = gaussian_elimination(self.A, self.G, -1, self.n, received_pivot_row)

                if self.group_no == 1:
                        self.check_x(min(self.A[-1]))

        def on_completeSub(self):
                recv_group, recv_A = self.completeSub.recv_pyobj()
                self.logger.info("GOT A FROM " + str(recv_group))
                if self.group_no >= 1:
                    self.A_dict[recv_group] = recv_A
                    if len(self.A_dict.keys()) == NUM_GROUPS:
                        maxA3 = numpy.concatenate((self.A_dict[1][3], self.A_dict[2][3], self.A_dict[3][3], self.A_dict[4][3]))
                        result = max(maxA3)
                        self.logger.info("SENDING " + str(result))
                        self.resultPort.send_pyobj(result)


                        
def find_element(array, element):
        if element in array:
                return list(array).index(element)
        return -1        

def find_non_zero(array):
        non_zero_indices = list()
        for i in range(len(array)):
                if array[i] != 0:
                        non_zero_indices.append(i)
        return non_zero_indices

def find_pivot_row(array, n):
        min_value = 10000
        result_index = -1
        for i in range(len(array)):
                min_element = array[i][n]
                last_element = array[i][len(array[i]) - 1]
                if min_element > 0 and (last_element/min_element) < min_value:
                        min_value = last_element / min_element
                        result_index = i

        column_array = [x[n] for x in array]
        non_zero_array = find_non_zero(column_array)
        pivot_row = array[result_index][:]
        return non_zero_array, result_index, min_value, pivot_row

def gaussian_elimination(A, non_zero_indices, pivot_index, n, pivot_row):
        for i in range(len(non_zero_indices)):
                index = non_zero_indices[i]
                if index != pivot_index:
                        A[index] = A[index] - pivot_row * A[index][n] / pivot_row[n]

        return A


def get_sheet_array(book, sheetname):
        sheet = book.sheet_by_name(sheetname)
        sheet_array = list()
        for row in sheet.get_rows():
                row_list = list()
                for x in row:
                        if x.ctype == 2:
                                row_list.append(x.value)
                        else:
                                row_list.append(None)
                sheet_array.append(row_list)

        return sheet_array

