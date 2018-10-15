import logging

from riaps.run.comp import Component
from CUFLS_lib.cufls_relay import *

RTDS_IP = "192.168.1.102"
RTDS_PORT = 7571 # Node 01

mname_str = 'F2'
mname_prefix = 'F'
pslider_name = 'L2-P'
pslider_full_value = 20
qslider_name = 'L2-Q'
qslider_full_value = 12

freq_thres_list = [i/10 for i in range(594,584,-1)]
ls_perc_list = [0.04]*len(freq_thres_list)

class CuflsRelayNode01(Component):
    def __init__(self):
        super(CuflsRelayNode01, self).__init__()

        self.cufls_relay = CuflsRelay(RTDS_IP, RTDS_PORT,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value,
                 freq_thres_list, ls_perc_list)

        # == Connect RTDS
        self.cufls_relay.connect_rtds()
        self.logger.info("CUFLS Relay Initialization Completed!")
        
    def on_clock(self):
        time = self.clock.recv_pyobj()

        freq_value = self.check_freq()
        self.logger.info("Freq = %f Hz", freq_value)

        self.load_shedding_check(freq_value)

    def on_commandmsg(self):
        pass

    def check_freq(self):
        meter_value = self.cufls_relay.read_meter()
        return meter_value

    def load_shedding_check(self, freq_value):
        self.cufls_relay.load_shedding_check(freq_value)
