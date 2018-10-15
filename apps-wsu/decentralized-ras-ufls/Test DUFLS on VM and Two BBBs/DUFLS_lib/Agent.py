import random # @For offline debug

from DUFLS_lib.dufls_relay import *

class Agent(object):

    FREQ_LV = 59.8 #Unit: Hz
    DFDT_LV = -1.35 #Unit: Hz/s
    DFDT_HV = -0.3 #Unit: Hz/s

    LS_APPLIED_COUNTER = 200;

    def __init__(self, freq_base,
                 rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value):
        self.f_base = freq_base

        self.dufls_relay = DuflsRelay(rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value)

        self.freq_val = 0.0
        self.dfdt_val = 0.0

        self.ls_applied = False
        self.ls_applied_counter = Agent.LS_APPLIED_COUNTER

    def connect_rtds(self):
        self.dufls_relay.connect_rtds()

    # == For load shedding
    def load_shedding_action(self, ls_val):
        self.dufls_relay.load_shedding_action(ls_val)
        self.ls_applied = True

    # == For monitoring
    def agent_monitoring(self):
        self.update_readings()
        freq_meter_value = self.get_freq_val()
        dfdt_meter_value = self.get_dfdt_val()
        return freq_meter_value, dfdt_meter_value

    def update_readings(self):
        self.update_freq_val()
        self.update_dfdt_val()

    def update_freq_val(self):
        # self.freq_val = random.random()*self.f_base # @For offline debug

        self.freq_val = self.dufls_relay.read_freq_meter()

    def update_dfdt_val(self):
        # self.dfdt_val = (-1)*random.random() # @For offline debug

        self.dfdt_val = self.dufls_relay.read_dfdt_meter()

    def get_freq_val(self):
        return self.freq_val

    def get_dfdt_val(self):
        return self.dfdt_val

    # == Check
    def load_shedding_check(self):
        if self.ls_applied and self.ls_applied_counter > 0:
            self.ls_applied_counter -= 1
        else:
            self.ls_applied = False
            self.ls_applied_counter = Agent.LS_APPLIED_COUNTER

        if self.ls_applied:
            flag_ls = False
        else:
            flag_ls = self.check_triggers()

        return flag_ls

    def check_triggers(self):
        triggers_flags_list = [self.check_trigger_freq(), self.check_trigger_dfdt()]
        flags_all = all(triggers_flags_list)
        return flags_all

    def check_trigger_freq(self):
        return self.freq_val < Agent.FREQ_LV

    def check_trigger_dfdt(self):
        return Agent.DFDT_LV <= self.dfdt_val <= Agent.DFDT_HV

    # == For testing
    def test_monitoring(self):
        self.update_readings()
        flag_uf = self.check_triggers()
        return flag_uf
