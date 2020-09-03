#CompReq.py
from riaps.run.comp import Component
import os
# import spdlog as spd
import random
import threading
import logging

class CompReq(Component):
    def __init__(self, logfile):
        super(CompReq, self).__init__()
        self.id = random.randint(0,10000)


        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

#         self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
#         self.logger.set_level(spd.LogLevel.DEBUG)
#         self.logger.set_pattern('%v')

        self.logger.info("Starting CompReq %d" % self.id)

        self.actorName = logfile
        self.uuid = False

        self.activeComponentCount = 0
        self.lockNIC = threading.Lock()

        self.activeComps = []

        self.NICCommand = 'down'
        self.NICCycled = False

    def handleNICStateChange(self,state):
        self.logger.info("NIC State Change: %s" % state)

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s %s" % (now,self.actorName))
        msg = random.randint(0,100)
        self.logger.info("sending value %d" % msg)
        self.sendval.send_pyobj(msg)
        if self.activeComponentCount <= 1:
            return
        if self.sporadic.running():
            pass
        else:
            self.sporadic.setDelay(8.0)
            self.sporadic.launch()

    def on_sporadic(self):
        now = self.sporadic.recv_pyobj()
        self.logger.info("on_sporadic: %s" % str(now))

        if self.NICCycled:
            return

        if self.lockNIC.acquire(blocking = False):
            try:
                self.logger.info("Requesting NIC %s" % self.NICCommand)
                self.reqNicKill.send_pyobj(self.NICCommand)
                if self.NICCommand == 'down':
                    self.NICCommand = 'up'
                else:
                    self.NICCycled = True

            except PortError:
                self.logger.info("REQ port error")
                self.lockNIC.release()
                self.reqNicKill.reset()
        else:
            self.logger.info("Could not acquire NIC req port")

    def on_reqNicKill(self):
        msg = self.reqNicKill.recv_pyobj()
        self.logger.info("on_reqNicKill: %s" % msg)
        self.lockNIC.release()

    def on_intHbClock(self):
        msg = self.intHbClock.recv_pyobj()
        self.intHbPub.send_pyobj("REQ")

    def on_intHbSub(self):
        msg = self.intHbSub.recv_pyobj()
        if msg not in self.activeComps:
            self.activeComps.append(msg)
            self.activeComponentCount += 1
            if self.activeComponentCount > 1:
                self.intHbClock.halt()
                self.logger.info("INTERNAL RUNNING")


    def __destroy__(self):
        self.logger.info("Stopping CompReq %d" % self.id)
        self.logger.flush()
