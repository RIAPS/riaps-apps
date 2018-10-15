from datetime import datetime

from CUFLS_lib.rtds_talker import *

info_print_num_ites = 5e1

class CuflsRelay(object):

    def __init__(self, rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value,
                 freq_thres_list, ls_perc_list):
        self.rtds_talker = RtdsTalker(rtds_ip, rtds_port)

        self.mname_str = mname_str
        self.mname_prefix = mname_prefix

        self.freq_thres_list = freq_thres_list
        self.ls_perc_list = ls_perc_list
        self.freq_thres_flag = [False]*len(self.freq_thres_list)

        # @TODO: check whether the freq_thres_list is sorted or not

        self.pslider_name = pslider_name
        self.pslider_full_value = pslider_full_value
        self.qslider_name = qslider_name
        self.qslider_full_value = qslider_full_value

    def connect_rtds(self):
        self.rtds_talker.connect_rtds()

    def disconnect_rtds(self):
        self.rtds_talker.disconnect_rtds()

    def monitor(self):
        print('Start monitoring')
        counter = 0
        while True:
            meter_value = self.read_meter()
            self.load_shedding_check(meter_value)
            counter += 1
            if counter >= info_print_num_ites:
                print('Monitoring...')
                counter = 0

    def read_meter(self):
        meter_value = self.rtds_talker.read_meter(self.mname_str, self.mname_prefix)
        return meter_value

    def load_shedding_check(self, meter_value):
        flag_take_ls_action = False
        for idx, val in enumerate(self.freq_thres_list):
            if (val > meter_value) and \
                    (not self.freq_thres_flag[idx]):
                flag_take_ls_action = True
                self.freq_thres_flag[idx] = True
        
        if flag_take_ls_action:
            self.load_shedding_action()

    def load_shedding_action(self):
        total_ls_perc = 0
        for idx, val in enumerate(self.freq_thres_flag):
            if val:
                total_ls_perc += self.ls_perc_list[idx]

        total_ld_left = 1 - total_ls_perc

        pslider_val = self.pslider_full_value * total_ld_left #TODO: check if 1-total_ls_perc is nonnegative
        qslider_val = self.qslider_full_value * total_ld_left

        self.rtds_talker.set_slider(self.pslider_name, pslider_val)
        self.rtds_talker.set_slider(self.qslider_name, qslider_val)
        
        cur_ls_time = datetime.now()
        print('[{}] After load shedding, {:.2%}% load left.'.format(cur_ls_time, total_ld_left))
        # @TODO Display the amount & percent of load shedding in this step
        
