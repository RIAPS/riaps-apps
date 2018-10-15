from cufls_relay import *

RTDS_IP = "192.168.1.102"
RTDS_PORT = 7572 # Node 02

mname_str = 'F3'
mname_prefix = 'F'
pslider_name = 'L3-P'
pslider_full_value = 20
qslider_name = 'L3-Q'
qslider_full_value = 12
freq_thres_list = [i/10 for i in range(594,584,-1)]
ls_perc_list = [0.04]*len(freq_thres_list)

if __name__ == '__main__':
    # == Init
    cufls_relay_01 = Cufls_Relay(RTDS_IP, RTDS_PORT,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value,
                 freq_thres_list, ls_perc_list)

    # == Connect RTDS
    cufls_relay_01.connect_rtds()

    # == Start Monitoring
    cufls_relay_01.monitor()
