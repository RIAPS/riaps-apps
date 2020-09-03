
#CompReq.py
from riaps.run.comp import Component
import os
import random
import spdlog as spd
import subprocess
import time
import logging

class NicDevice(Component):
    def __init__(self, logfile):
        super(NicDevice, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

#         self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
#         self.logger.set_level(spd.LogLevel.DEBUG)
#         self.logger.set_pattern('%v')

        self.logger.info("Starting NicDevice %d" % self.id)

        self.actorName = logfile
        self.uuid = False
        self.activeComps = []
        self.activeComponentCount = 0

    def on_repPort(self):
        msg = self.repPort.recv_pyobj()
        self.logger.info("Received %s" % msg)
        try:
            res = subprocess.call("ifconfig eth0 %s" % msg,shell=True)
            self.logger.info("%s RESULT: %s" % (msg,str(res)))
            response = 'done'
        except Exception as e:
            response = str(e)
        self.repPort.send_pyobj(response)

    def on_intHbClock(self):
        msg = self.intHbClock.recv_pyobj()
        self.intHbPub.send_pyobj("KILL")

    def on_intHbSub(self):
        msg = self.intHbSub.recv_pyobj()
        if msg not in self.activeComps:
            self.activeComps.append(msg)
            self.activeComponentCount += 1
            if self.activeComponentCount > 1:
                self.intHbClock.halt()
                self.logger.info("INTERNAL RUNNING")


    def __destroy__(self):
        self.logger.info("Stopping NicDevice %d" % self.id)
        self.logger.flush()
