from DUFLS_lib.GenAgent import GenAgent

# == For GenAgent
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

if __name__ == '__main__':
    # == Init
    ga_01 = GenAgent('GA01', gen_H, gen_S, freq_base, RTDS_IP, RTDS_PORT,
                 mname_str, mname_prefix,
                 pslider_name, pslider_full_value, qslider_name, qslider_full_value)
    ga_01.connect_rtds()

    # == Get f
    ga_01.update_freq_val()
    cur_freq = ga_01.get_freq_val()
    print('f = {:.5f} Hz/s'.format(cur_freq))

    # == Get dfdt
    ga_01.update_dfdt_val()
    cur_dfdt = ga_01.get_dfdt_val()
    print('dfdt = {:.5f} Hz/s'.format(cur_dfdt))

    # == Calc dp
    ga_01.estimate_dp()
    cur_dp = ga_01.dp
    print('Delta_P = {:.5f} MW'.format(cur_dp))

    # == Check triggers
    cur_trigger_freq = ga_01.check_trigger_freq()
    print('trigger_freq = {}'.format(cur_trigger_freq))

    cur_trigger_dfdt = ga_01.check_trigger_dfdt()
    print('trigger_dfdt = {}'.format(cur_trigger_dfdt))

    flag_uf = ga_01.check_triggers()
    print('Underfrequency issue = {}'.format(flag_uf))

    # == Estimate dp
    while True:
        ga_01.gen_monitoring()

        print('Freq = {} (Hz), dfdt = {} (Hz/s)'.format(ga_01.get_freq_val(), ga_01.get_dfdt_val()))

        cur_dp = ga_01.estimate_dp()
        print('Delta_P = {:.5f} MW'.format(cur_dp))
