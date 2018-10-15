# import riaps
from riaps.run.comp import Component
import logging
import random
import os
import threading
import zmq
import time
import struct
from pypmu.pdc import Pdc
from pypmu.frame import CommonFrame


class C37ReceiverThread(threading.Thread):
    def __init__(self, component):
        threading.Thread.__init__(self)
        self.active = threading.Event()
        self.active.clear()
        self.waiting = threading.Event()
        self.terminated = threading.Event()
        self.terminated.clear()
        self.component = component
        self.pdc = Pdc(pmu_ip=self.component.pmu_ip,
                             pmu_port=self.component.pmu_port)

    def run(self):
        self.data_plug = self.component.data_queue.setupPlug(self)
        self.config_plug = self.component.config_queue.setupPlug(self)
        self.header_plug = self.component.header_queue.setupPlug(self)

        while True:
            if self.terminated.is_set():
                break

            if not self.active.is_set():
                if self.pdc.is_connected():
                    self.pdc.stop()
                    self.active.wait()
                    self.pdc.start()
                else:
                    self.active.wait()

            if self.pdc.is_connected():
                data = self.pdc.get()
                self.data_plug.send_pyobj(data)

            else:
                self.pdc.run()
                if self.pdc.is_connected():
                    header = self.pdc.get_header()
                    self.header_plug.send_pyobj(header)
                    config = self.pdc.get_config()
                    self.config_plug.send_pyobj(config)
                    self.pdc.start()
                else:
                    # TODO: wait some?
                    pass


        self.pdc.quit()

    def activate(self):
        self.active.set()

    def deactivate(self):
        self.active.clear()

    def terminate(self):
        self.terminated.set()

class C37Receiver1P13A2D(Component):
    def __init__(self, pmu_ip, pmu_port):
        super().__init__()
        self.logger.setLevel(logging.DEBUG)
        self.pmu_ip = pmu_ip
        self.pmu_port = pmu_port
        self.angle_diff = 0
        self.logger.info("PMU @%s:%d", pmu_ip, pmu_port)
        self.readerThread = None                    # Cannot manipulate ports in constructor or start threads

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.logger.info('on_clock():%s  and the angle_diff is %f ', now, self.angle_diff)
        if self.readerThread == None:
            self.readerThread = C37ReceiverThread(self)
            self.readerThread.start()
            self.data_queue.activate()
            self.config_queue.activate()
            self.header_queue.activate()

    def __destroy__(self):
        self.logger.info("__destroy__")
        if self.readerThread:
            self.readerThread.terminate()

    def on_data_queue(self):
        """Processing incoming data frames (application specific).

        Note: This is not a generic implementation.

        The current (hard coded) packet format:
        Value format: (P;F;F;F) = 15
            Polar Float phasors, Float analog and Float frequency values

        [PHASOR0]  VAGPM: not used
        
        [f]        f:   C37frequency
        [df]       df:  C37frequency deviation
        
        [ANALOG0]  f1: frequency at DG1 output
        [ANALOG1]  f2: frequency at DG2 output
        [ANALOG2]  f3: frequency at DG3 output
        [ANALOG3]  f4: frequency at DG4 output
        [ANALOG4]  P1: active power at DG1 output
        [ANALOG5]  P2: active power at DG2 output
        [ANALOG6]  P3: active power at DG3 output
        [ANALOG7]  P4: active power at DG4 output
        [ANALOG8]  Q1: reactive power at DG1 output
        [ANALOG9]  Q2: reactive power at DG2 output
        [ANALOG10]  Q3: reactive power at DG3 output
        [ANALOG11]  Q4: reactive power at DG4 output
        [ANALOG12]  V2: Voltage at DG2 output
        
        [DIGITAL0] BRKPCCTR: BReaKer at PCC TRipping
        [DIGITAL1] RMB1: Remote Bit 1
        [DIGITAL2] RMB2: Remote Bit 2
        """
        OFFSET_SOC = 6
        OFFSET_VALUES = 16
        FMT_VALUES = '!ff ff ffff ffff ffff f H H'  #'!ff(phase angle and mag) ff(f and df) ffff ffff ffff f(13 analogs) H H(2 dig)' 
        #self.logger.info('on_data_queue()')
        frame = self.data_queue.recv_pyobj()
        _, framesize = struct.unpack_from('!HH', frame, 0)
        assert CommonFrame.extract_frame_type(frame) == 'data'

        soc, fracsec = struct.unpack_from('!II', frame, OFFSET_SOC)
        timestamp = soc + float(fracsec & 0xffffff) / 0xffffff # assuming time_base

        (vagpm_m, vagpm_a, freq, rocof, f1, f2, f3, f4, P1, P2, P3, P4, Q1, Q2, Q3, Q4, V2,
         digits, digits1) = \
                struct.unpack_from(FMT_VALUES, frame, OFFSET_VALUES)

        #data = {'VAGPM': (vagpm_m, vagpm_a), 
        #        'f1': f1, 'f2': f2, 'f3': f3, 'f4': f4, 'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4, 
        #        'Q1':Q1, 'Q2':Q2, 'Q3':Q3, 'Q4':Q4, 'V2':V2, 'DIGITALS': digits, 'DIGITALS1': digits1,
        #        'FREQ': freq, 'ROCOF': rocof,
        #        'timestamp': timestamp}
        data = {'mag_diff':P1, 'angle_diff': P2, 'DIGITALS': digits, 'DIGITALS1': digits1}
        self.angle_diff = P2
        self.c37data.send_pyobj(data)

    def on_config_queue(self):
        OFFSET_NUM_PMU = 18
        OFFSET_CHNAMES = 46

        #self.logger.info('on_config_queue()')
        frame = self.config_queue.recv_pyobj()

        assert CommonFrame.extract_frame_type(frame) == 'cfg2'

        num_pmu, stn, idcode, fmt, phnmr, annmr, dgnmr = \
            struct.unpack_from('!H16sHHHHH', frame, OFFSET_NUM_PMU)
        assert num_pmu == 1 # cannot process multistream configs

        def str_clean(bstr):
            return bstr.decode('ascii').strip()

        n_channels = (phnmr + annmr + dgnmr * 16)
        ch_names_b = struct.unpack_from('16s' * n_channels, frame, OFFSET_CHNAMES)
        ch_names = [str_clean(ch_name) for ch_name in ch_names_b]

        config = {'station': str_clean(stn), 'phasors': ch_names[0:phnmr],
                  'analogs': ch_names[phnmr:phnmr+annmr], 'digitals': ch_names[phnmr+annmr:]}

        self.c37config.send_pyobj((frame, config))

    def on_header_queue(self):
        #self.logger.info('on_header_queue()')
        frame = self.header_queue.recv_pyobj()
        self.c37header.send_pyobj((frame.convert2bytes(), frame.header))