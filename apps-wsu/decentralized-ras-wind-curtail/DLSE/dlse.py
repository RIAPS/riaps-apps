import numpy
from read_excel import get_H_for_group

def dlse(V, I_ij, I_ji, group_no):
        Z = list()
        
        real_list = list()
        imag_list = list()
        for vector in V:
                real_list.append(vector.real)
                imag_list.append(vector.imag)
        Z += real_list + imag_list

        real_list = list()
        imag_list = list()
        for current_vector in I_ij:
                real_list.append(vector.real)
                imag_list.append(vector.imag)
        Z += real_list + imag_list

        real_list = list()
        imag_list = list()
        for current_vector in I_ji:
                real_list.append(vector.real)
                imag_list.append(vector.imag)
        Z += real_list + imag_list


        H = get_H_for_group(group_no)
