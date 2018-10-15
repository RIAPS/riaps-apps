import logging

from riaps.run.comp import Component
from DUFLS_lib.SubAgent import SubAgent

# == GLOBAL
NUM_NODES = 3

# == For GenAgent
SA_NAME = 'SA02_Node03'

# == For Agent
freq_base = 60 #Unit: Hz

# == For DuflsRlay
RTDS_IP = "192.168.1.102"
RTDS_PORT = 7573 # Node 03

mname_str = 'F4'
mname_prefix = 'F'
pslider_name = 'L4-P'
pslider_full_value = 20
qslider_name = 'L4-Q'
qslider_full_value = 10

class Node03_SA02(Component):
    def __init__(self):
        super(Node03_SA02, self).__init__()

        self.sa_02 = SubAgent(SA_NAME, freq_base, RTDS_IP, RTDS_PORT,
                         mname_str, mname_prefix,
                         pslider_name, pslider_full_value, qslider_name, qslider_full_value)

        # == Connect RTDS
        self.sa_02.connect_rtds()
        self.logger.info("%s Initialization Completed!", self.sa_02.name)
        
    def on_clock(self):
        time = self.clock.recv_pyobj()

        freq_value, dfdt_value = self.monitoring()
        self.logger.info("Freq = %f (Hz); Dfdt = %f (Hz/s)", freq_value, dfdt_value)

        self.load_shedding_check()

    def monitoring(self):
        freq_meter_value = self.sa_02.agent_monitoring()
        return freq_meter_value

    def ls_action(self, ls_val):
        self.sa_02.load_shedding_action(ls_val)

    def load_shedding_check(self):
        flag_ls = self.sa_02.load_shedding_check()
        if flag_ls:
            pass
            # self.notice_ls_pub.send_pyobj('LS is needed!')

    def on_share_dp_sub(self):
        msg_dp_str = self.share_dp_sub.recv_pyobj()
        self.logger.info("%s received %s", self.sa_02.name, msg_dp_str)
        dp_val = float(msg_dp_str)

        my_dp = dp_val / NUM_NODES
        self.ls_action(my_dp)
