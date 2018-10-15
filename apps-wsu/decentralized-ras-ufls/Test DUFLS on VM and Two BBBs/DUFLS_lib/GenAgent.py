from datetime import datetime

from DUFLS_lib.Agent import Agent


class GenAgent(Agent):
    
    DP_K = 1.05

    def __init__(self, agent_name, gen_H, gen_S, freq_base,
                 rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value):
        super(GenAgent, self).__init__(freq_base,
                    rtds_ip, rtds_port,
                    mname_str, mname_prefix,
                    pslider_name, pslider_full_value, qslider_name, qslider_full_value)

        self.name = agent_name

        self.H = gen_H
        self.S = gen_S

        self.dp = 0

    def estimate_dp(self):
        self.dp = GenAgent.DP_K * (2*self.H*self.S/self.f_base)*self.dfdt_val*(self.freq_val/self.f_base)
        
        self.dp = (-1)*self.dp
        return self.dp

    # == For testing only
    def gen_monitoring(self):
        flag_uf = self.test_monitoring()

        if flag_uf:
            cur_ls_time = datetime.now()
            print('[{}] UF Issue Detected!'.format(cur_ls_time))
            print('Freq = {} (Hz), dfdt = {} (Hz/s)'.format(self.get_freq_val(), self.get_dfdt_val()))

            self.estimate_dp()
