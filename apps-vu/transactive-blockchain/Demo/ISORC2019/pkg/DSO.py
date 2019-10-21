#DSO.py
from riaps.run.comp import Component
import os
import logging
from time import time, sleep


from libs.config import *
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime
import zmq

#from asyncio.log import logger

class DSO(Component):
    def __init__(self, logfile):
        super(DSO, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting DSO",str(self.pid))
        self.client = EthereumClient(ip=MINER, port=PORT)
        self.account = self.client.accounts()[0] # use the first owned address
        self.deploy_contract()
        self.next_interval = START_INTERVAL
        t = time()
        self.epoch = t - START_INTERVAL * INTERVAL_LENGTH

        self.dbase = Database()

        self.grid = zmq.Context().socket(zmq.REQ)
        self.grid.connect('tcp://%s:5555' %(GRID))

        logpath = '/tmp/' + logfile + '.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.warning("(PID %s) - starting DSO",str(self.pid))


    def on_contractAddr(self):
        msg = self.contractAddr.recv_pyobj()
        if msg['request'] == "query_contract_address":
            self.logger.info("PID (%s) - on_query():%s",str(self.pid),str(msg))
            self.logger.info("query_contract_address()")
            self.logger.info("time elapsed since epoch %s" %(time()-self.epoch))
            self.contractAddr.send_pyobj({'contract': self.contract_address, 'time': time() - self.epoch})
        elif msg['request']== "waste":
            self.logger.info("on_consume()[%d]:%d", self.pid,len(msg['payload']))
            self.contractAddr.send_pyobj("waste message received")
        else:
            self.logger.error("Unknown request: " + msg['request'])
            self.contractAddr.send_pyobj("Unknown request!")

    def on_finalizer(self):
        now = self.finalizer.recv_pyobj()
        self.logger.info('PID(%s) - on_finalizer(): %s',str(self.pid),str(now))
        self.logger.warning("Finalizing interval {}".format(self.next_interval))
        self.contract.finalize(self.account, self.next_interval)
        self.stepSim()
        self.next_interval += 1


    def stepSim(self):
        msg = {"request" : "step"}
        self.grid.send_pyobj(msg)
        response = self.grid.recv_pyobj()

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping DSO",str(self.pid))

    def deploy_contract(self):
        self.logger.info("Deploying contract...")
        # use command function because we need to get the contract address later
        receiptID = self.client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': self.account, 'gas': TRANSACTION_GAS}])
        self.logger.info("Transaction receipt: " + receiptID)
        while True:
            sleep(5)
            self.logger.info("Waiting for contract to be mined... (block number: {})".format(self.client.command("eth_blockNumber", params=[])))
            receipt = self.client.command("eth_getTransactionReceipt", params=[receiptID])
            if receipt is not None:
                self.contract_address = receipt['contractAddress']
                break
        self.contract = MatchingContract(self.client, self.contract_address)
        self.contract.setup(self.account, MICROGRID.C_ext, MICROGRID.C_int, START_INTERVAL)
        self.logger.info("Contract address: " + self.contract_address)
