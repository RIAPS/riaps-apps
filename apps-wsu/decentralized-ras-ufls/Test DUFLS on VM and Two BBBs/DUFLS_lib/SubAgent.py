from datetime import datetime

from DUFLS_lib.Agent import Agent


class SubAgent(Agent):
    
    DP_K = 1

    def __init__(self, agent_name, freq_base,
                 rtds_ip, rtds_port,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value):
        super(SubAgent, self).__init__(freq_base,
                    rtds_ip, rtds_port,
                    mname_str, mname_prefix,
                    pslider_name, pslider_full_value, qslider_name, qslider_full_value)

        self.name = agent_name

