from DUFLS_lib.dufls_relay import *

RTDS_IP = "192.168.1.102"
RTDS_PORT = 7571 # Node 01

mname_str = 'F2'
mname_prefix = 'F'
pslider_name = 'L2-P'
pslider_full_value = 20
qslider_name = 'L2-Q'
qslider_full_value = 12

if __name__ == '__main__':
    # == Init
    dufls_relay_01 = DuflsRelay(RTDS_IP, RTDS_PORT,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value)

    # == Connect RTDS
    dufls_relay_01.connect_rtds()

    # == Start Monitoring
    freq_meter_value = dufls_relay_01.read_freq_meter()
    print('Freq meter value = {} Hz'.format(freq_meter_value))

    dfdt_meter_value = dufls_relay_01.read_dfdt_meter()
    print('Dfdt meter value = {} Hz/s'.format(dfdt_meter_value))
