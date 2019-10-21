#
from riaps.run.comp import Component
import logging
import os
import ctypes  #import ctypes c/c++ extension for python

class DW(ctypes.Structure):  #class created to access struct defined in simulink c code
    _fields_ = [('PrevAggrEng_DSTATE', ctypes.c_double)] #element of the struct of type double. See RIAPS_Sim_Int.c

class SubSim(Component):
    def __init__(self, logfile):
        super(SubSim, self).__init__()
        self.pid = os.getpid()

        logpath = '/tmp/' + logfile + '.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        # create dynamic linked library. Need a way to deploy the .so file with component
        self.simlib = ctypes.CDLL('libs/TestSimulink/RIAPS_Sim_Int.so')        # define argument types for the function RIAPS_Sim_Int_step
        self.simlib.RIAPS_Sim_Int_step.argtypes = [ctypes.c_double]
        #define return type for the function RIAPS_Sim_Int_step
        self.simlib.RIAPS_Sim_Int_step.restype = ctypes.c_double

    def on_connect(self):
        now = self.connect.recv_pyobj()
        msg = 'sub_up'  #notify the publisher to start sending

        try:
            self.ready.send_pyobj(msg)
        except PortError as e:
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_connect error: try again")

    def on_subSimPort(self):
        msg = self.subSimPort.recv_pyobj() #receive value from publisher
        msg = float(msg)
        self.logger.warning("[%d] on_subSimPort():%f" %(self.pid, msg))
        self.logger.warning('calling simulink function')
        #use ctypes "in_dll()" function to get the struct variable
        rtDW = DW.in_dll(self.simlib,'rtDW')
        #print the previous sum stored in simulink
        self.logger.warning('PrevAggrEng_DSTATE = %f' %rtDW.PrevAggrEng_DSTATE)
        # get simulink return value
        result = self.simlib.RIAPS_Sim_Int_step(ctypes.c_double(msg))
        self.logger.warning('simulink output = %f' %result)
        rep = "ready"
        self.logger.warning("[%d] send req: %s" % (self.pid,rep)) #send request to signal next value
        self.ready.send_pyobj(rep)

    def on_ready(self):
        msg = self.ready.recv_pyobj()
        self.logger.warning('[%d] recv rep: %s' % (self.pid,msg))
        if msg == 'pub_up':
            self.connect.halt()

    def __destroy__(self):
        self.logger.warning("[%d] destroyed" % self.pid)
