# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
from _curses import OK
from sys import stdout
import subprocess
import psutil
# import capnp
# import deplofail_capnp

# riaps:keep_import:end

class SvcDevice(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(SvcDevice, self).__init__()
        self.service = ""
# riaps:keep_constr:end

# riaps:keep_repport:begin
    def on_repport(self):
        msg = self.repport.recv_pyobj()
        self.service = msg
        self.logger.info("received message : %s" % msg)
        try:
            f = open("check_svc.txt", "x")
            f.close()
            try:
                cmd = subprocess.run(["pgrep %s" %msg], shell=True, stdout = subprocess.PIPE)
                proc_id = cmd.stdout.decode()
                proc_id = proc_id[:-1]
                self.logger.info("%s RESULT: %s" % (msg,str(proc_id)))
            except e:
                self.logger.info("error : %s" % e)
                resp = "error"
                
            try:
                self.logger.info("killing process")
                cmd = subprocess.run(["kill %s" %str(proc_id), "-SIGKILL"], shell=True)
                self.logger.info("%s RESULT: %s" % (msg,str(cmd)))
                resp = "ok"
            except:
                resp = "error"
                
        except FileExistsError as e:
            self.logger.info("file exists, service restarted successfully")
            resp = "success"
        except:
            self.logger.info("could not create file")
            resp = "error"
           
        self.repport.send_pyobj(resp)
# riaps:keep_repport:end

# riaps:keep_check:begin
    def on_check(self):
        found = False
        if not self.service == "":
            for proc in psutil.process_iter():
                if proc.name() == self.service:
                    self.logger.info("process name = %s, id = %s, status = %s" % (proc.name(), str(proc.pid), proc.status()))
                    found = True
            if not found:
                self.logger.info("%s service not running!" % self.service)
# riaps:keep_check:end

# riaps:keep_impl:begin

# riaps:keep_impl:end