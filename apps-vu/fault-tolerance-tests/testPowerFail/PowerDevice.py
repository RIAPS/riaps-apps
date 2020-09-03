# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import subprocess
import os
# import capnp
# import powerfail_capnp

# riaps:keep_import:end

class PowerDevice(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(PowerDevice, self).__init__()
        self.logger.info("started")
# riaps:keep_constr:end

# riaps:keep_repport:begin
    def on_RepPort(self):
        msg = self.RepPort.recv_pyobj()
        self.logger.info("received message : %s" % msg)
        try:
            f = open("check.txt", "x")
            f.close()
            try:
                cmd = subprocess.run("reboot", shell=True)
                self.logger.info("%s RESULT: %s" % (msg,str(cmd)))
                resp = "done"
            except:
                resp = "error"
        except FileExistsError as e:
            self.logger.info("file exists, reboot successful")
            resp = "success"
            
        except:
            self.logger.info("could not create file")
            resp = "error"
           
        self.RepPort.send_pyobj(resp)
# riaps:keep_repport:end

# riaps:keep_impl:begin

# riaps:keep_impl:end