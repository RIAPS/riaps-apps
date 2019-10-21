#Recorder.py
from riaps.run.comp import Component
from riaps.run.exc import PortError

import os
import logging

from libs.config import *
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import collections
from time import time, sleep

class Recorder(Component):
    def __init__(self, logfile):
        super(Recorder, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Recorder",str(self.pid))

        self.connected =0
        self.interval_trades = {}
        self.finalized = -1
        self.solutions = collections.defaultdict(dict)
        self.solution2solver ={}
        self.dbase = Database()


        logpath = '/tmp/' + logfile + '.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.warning("(PID %s) - starting Recorder",str(self.pid))

    def on_contractAddr(self):
        req = self.contractAddr.recv_pyobj()
        self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))

        self.epoch = time() - req['time']
        self.contract_address = req['contract']
        self.logger.info("Contract address: " + self.contract_address)
        self.logger.info("Setting up connection to Ethereum client...")
        client = EthereumClient(ip=MINER, port=PORT)
        self.account = client.accounts()[0] # use the first owned address
        self.logger.info("Creating contract object...")
        self.contract = MatchingContract(client, self.contract_address)
        self.connected = 1

    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))

        if self.connected == 0 :
            self.query_contract_address()

        elif self.connected == 1 :
            self.logger.debug("Polling events...")
            for event in self.contract.poll_events():
                params = event['params']
                name = event['name']
                self.logger.info("{}({}).".format(name, params))

                if name == "Finalized":
                    self.finalized = params['interval']
                    stopWatch = {"interval":self.finalized, "start":time(), "running" : 1}
                    self.logger.info("interval finalized : {}".format(self.finalized))
                    self.interval_trades[self.finalized] = []
                elif name == "TradeFinalized":
                    if (stopWatch["running"]):
                        stopWatch["running"] = 0
                        stopWatch["split"] = time() - stopWatch["start"]
                        self.dbase.log(self.finalized, "Solver", "FinalizeTime", stopWatch["split"])
                    interval = params['time']
                    power = params['power']
                    self.interval_trades[self.finalized].append(power)
                    self.logger.info(self.finalized)
                    self.logger.info(self.interval_trades[self.finalized])
                    self.dbase.log(self.finalized,"Solver", "TotalPowerTraded", sum(self.interval_trades[self.finalized]))

                elif name == "TradeAdded":
                    interval = params['time']
                    ID = params['solutionID']
                    pwr =  params['power']
                    solverID = self.solution2solver[ID]
                    if int(ID) < 10 :
                        ID = "0"+str(ID)
                    if int(ID) < 100 :
                        ID = "0"+str(ID)
                    try:
                        self.solutions[ID][interval] += pwr
                    except KeyError:
                        self.solutions[ID][interval] = pwr
                    #TradeAdded({'solutionID': 63, 'power': 400, 'time': 93, 'objective': 400, 'buyerID': 65, 'sellerID': 27}).
                    self.logger.info("TradeAdded : interval:{}, Solver:{}, SolutionID:{}, pwr:{}".format(interval,solverID,ID,self.solutions[ID][interval]))
                    self.dbase.log(interval, "solution"+str(ID), "Solver"+str(solverID),  self.solutions[ID][interval])
                    self.logger.info("{}({}).".format(name, params))
                elif (name == "SolutionCreated"):
                    solverID = params['solverID']
                    solutionID = params['solutionID']
                    self.solution2solver[solutionID] = solverID
                    self.logger.info("SolutionCreated Solver:{} Solution:{}".format(solverID, solutionID))

    def handlePeerStateChange(self,state,uuid):
        self.logger.warning("peer %s is %s at: %s" % (uuid,state, time()))

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping Recorder",str(self.pid))


    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)

        try:
            #self.cltReqPort.send_pyobj(msg)
            self.contractAddr.send_pyobj(msg)
        except PortError as e:
            self.logger.info("query_contract_address:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("query_contract_address: try again")
