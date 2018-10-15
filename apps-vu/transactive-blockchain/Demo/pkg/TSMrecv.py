#DSO.py
from riaps.run.comp import Component
import os
import logging
from time import time, sleep

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime

#from asyncio.log import logger

class TSMrecv(Component):
    def __init__(self, logfile):
        super(TSMrecv, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting TSM receiver",str(self.pid))

        self.dbase = Database()  

        logpath = '/tmp/' + logfile + '.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.warning("(PID %s) - starting TSM receiver",str(self.pid))

    def on_ack(self):
        '''Time Sensitive Messaging '''
        msg = self.ack.recv_pyobj()
        self.logger.info("PID (%s) - on_ack():%s",str(self.pid),str(msg))
        sendTime = self.ack.get_sendTime()
        recvTime = self.ack.get_recvTime()
        self.logger.warning("sendTime: %s, recvTime: %s" %(sendTime, recvTime))
        self.logger.warning("%s FlightTime: %s" %(msg, recvTime-sendTime))
        self.dbase.post(now=datetime.datetime.now(), tag_dict={"ID":msg}, seriesName="TSM", value=recvTime-sendTime)

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping TSM reciever",str(self.pid))
