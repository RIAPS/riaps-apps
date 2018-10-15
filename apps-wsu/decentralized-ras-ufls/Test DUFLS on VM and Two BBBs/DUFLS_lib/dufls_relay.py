from datetime import datetime

from DUFLS_lib.rtds_talker import *

info_print_num_ites = 5e1

class DuflsRelay(object):

    DFDT_PREFIX_STR = 'dfdt_'

    def __init__(self, rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value):
        self.rtds_talker = RtdsTalker(rtds_ip, rtds_port)

        self.mname_str = mname_str
        self.mname_prefix = mname_prefix

        self.dfdt_mname_str = DuflsRelay.DFDT_PREFIX_STR + mname_str
        self.dfdt_mname_prefix = DuflsRelay.DFDT_PREFIX_STR + mname_prefix

        self.pslider_name = pslider_name
        self.pslider_full_value = pslider_full_value
        self.qslider_name = qslider_name
        self.qslider_full_value = qslider_full_value

    def connect_rtds(self):
        self.rtds_talker.connect_rtds()

    def disconnect_rtds(self):
        self.rtds_talker.disconnect_rtds()

    def read_freq_meter(self):
        freq_meter_value = self.rtds_talker.read_meter(self.mname_str, self.mname_prefix)
        return freq_meter_value

    def read_dfdt_meter(self):
        dfdt_meter_value = self.rtds_talker.read_meter(self.dfdt_mname_str, self.dfdt_mname_prefix)
        return dfdt_meter_value

    def load_shedding_action(self, p_ls_val):
        # TODO: check if the amount of load to be shed is larger than ls_val

        # TODO: deal with multiple ls actions
        pslider_val = self.pslider_full_value - p_ls_val
        total_ld_shed = p_ls_val / self.pslider_full_value
        total_ld_left = 1 - total_ld_shed

        q_ls_val = total_ld_shed * self.qslider_full_value
        qslider_val = self.qslider_full_value - q_ls_val

        self.rtds_talker.set_slider(self.pslider_name, pslider_val)
        self.rtds_talker.set_slider(self.qslider_name, qslider_val)

        cur_ls_time = datetime.now()
        print('[{}] After load shedding, {:.2%} load left, i.e., {:.2%} load shed'.format(cur_ls_time, total_ld_left, total_ld_shed))

