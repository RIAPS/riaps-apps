import logging

from riaps.run.comp import Component
from DUFLS_lib.GenAgent import GenAgent

# == GLOBAL
NUM_NODES = 3

# == For GenAgent
GA_NAME = 'GA01_Node01'
gen_H = 10 #Unit: s (MWs/MVA)
gen_S = 45 #Unit: MW (Base Turbine MW Rating)

# == For Agent
freq_base = 60 #Unit: Hz

# == For DuflsRlay
RTDS_IP = "192.168.1.102"
RTDS_PORT = 7571 # Node 01

mname_str = 'F2'
mname_prefix = 'F'
pslider_name = 'L2-P'
pslider_full_value = 20
qslider_name = 'L2-Q'
qslider_full_value = 12

class Node01_GA01(Component):
    def __init__(self):
        super(Node01_GA01, self).__init__()

        self.ga_01 = GenAgent(GA_NAME, gen_H, gen_S, freq_base, RTDS_IP, RTDS_PORT,
                         mname_str, mname_prefix,
                         pslider_name, pslider_full_value, qslider_name, qslider_full_value)

        # == Connect RTDS
        self.ga_01.connect_rtds()
        self.logger.info("%s Initialization Completed!", self.ga_01.name)
        
    def on_clock(self):
        time = self.clock.recv_pyobj()

        freq_value, dfdt_value = self.monitoring()
        self.logger.info("Freq = %f (Hz); Dfdt = %f (Hz/s)", freq_value, dfdt_value)

        # self.logger.info('~~~~~~~~~send sth~~~~~~~')
        # self.share_dp_pub.send_pyobj(str(2.0))
 
        self.load_shedding_check()

    def monitoring(self):
        freq_meter_value, dfdt_meter_value = self.ga_01.agent_monitoring()
        return freq_meter_value, dfdt_meter_value

    def ls_action(self, ls_val):
        self.ga_01.load_shedding_action(ls_val)

    def flag_ls_true(self):
        cur_dp = self.ga_01.estimate_dp()
        self.share_dp_pub.send_pyobj(str(cur_dp))

        self.logger.info("Delta_P = %f (MW)", cur_dp)

        my_dp = cur_dp / NUM_NODES
        self.ls_action(my_dp)

    def load_shedding_check(self):
        flag_ls = self.ga_01.load_shedding_check()
        if flag_ls:
            self.flag_ls_true()

    def on_notice_ls_sub(self):
        msg = self.notice_ls_sub.recv_pyobj()
        self.flag_ls_true()
