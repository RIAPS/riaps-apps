#!/usr/bin/env python3
"""
tinyPMU will listen on ip:port for incoming connections.
When tinyPMU receives command to start sending
measurements - fixed (sample) measurement will
be sent.
"""
from pypmu.pmu import Pmu
from pypmu.frame import ConfigFrame2, DataFrame

PMU_ID = 1974
PMU_CONFIG = ConfigFrame2(pmu_id_code=PMU_ID, time_base=1000000, num_pmu=1,
    station_name="opal_io.py", id_code=PMU_ID,
    data_format=(True, True, True, True),
    phasor_num=6, analog_num=5, digital_num=1,
    channel_names=["VAGPM", "VBYPM", "VCYPM", "VASPM", "VBZPM", "VCZPM",
                   "VAGM", "VAGA", "VASM", "VASA", "SLIP1",
                   "BRKPCCTR", "RMB1", "RMB2", "",
                   "", "", "", "",
                   "", "", "", "",
                   "", "", "", ""],
    ph_units=[(1, 'v'), (1, 'v'), (1, 'v'), (1, 'v'), (1, 'v'), (1, 'v')],
    an_units=[(1, 'pow'), (1, 'pow'), (1, 'pow'), (1, 'pow'), (1, 'pow')],
    dig_units=[(0x0000, 0x0007)],
    f_nom=60,
    cfg_count=1,
    data_rate=120)

PMU_DATA = DataFrame(pmu_id_code=PMU_ID,
    stat=('ok', True, 'timestamp', False, False, False, 0, '<10', 0),
    phasors=[(115000.0, 0.0), (115000.0, 2.0944), (115000.0, -2.0944), (114989.0, 0.0873), (114989.0, 2.1817), (114989.0, -2.0071)],
    freq=0, dfreq=0,
    analog=[115000.0, 0.0, 114989.0, 5.0, 7.7],
    digital=[0x0000],
    data_format=(True, True, True, True))


pmu = Pmu(ip="127.0.0.1", port=9876)

pmu.set_configuration(PMU_CONFIG)  # This will load default PMU configuration specified in IEEE C37.118.2 - Annex D (Table D.2)
pmu.set_header('dummy_relay')  # This will load default header message "Hello I'm tinyPMU!"

pmu.run()  # PMU starts listening for incoming connections

while True:
    if pmu.clients:  # Check if there is any connected PDCs
        pmu.send(PMU_DATA)  # Sending sample data frame specified in IEEE C37.118.2 - Annex D (Table D.1)

pmu.join()
