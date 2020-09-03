# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
# import capnp
# import memfail_capnp
import ctypes
import time

# riaps:keep_import:end

class MemDevice(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(MemDevice, self).__init__()
        
    def handleActivate(self):
        self.logger.info("starting seg fault timer")
        self.clock.setDelay(10.0)
        self.clock.launch()
# riaps:keep_constr:end

# riaps:keep_clock:begin
    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s" % now)
        try:
            f = open("check_seg.txt", "x")
            f.close()
            self.clock.halt()
            self.logger.info("causing segmentation fault")
            time.sleep(2)
            ctypes.string_at(0)
        except FileExistsError as e:
            self.logger.info("file exists, actor restarted")
        except:
            self.logger.info("could not create file")
        
# riaps:keep_clock:end

# riaps:keep_impl:begin

# riaps:keep_impl:end 