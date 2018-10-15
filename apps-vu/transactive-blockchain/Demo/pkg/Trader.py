#Trader.py
from riaps.run.comp import Component
from riaps.run.exc import PortError
import os
import logging

from time import time, sleep
import signal

from libs.config import *
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime

class Trader(Component):
    def __init__(self,ID,logfile):
        super(Trader, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Trader",str(self.pid))

        self.prosumer_id = ID
        self.net_production = self.read_data(self.prosumer_id)
        self.selling_offers = set()
        self.buying_offers = set()
        self.connected =0

        self.dbase = Database()

        self.role = None
        self.roleID = 0
        #self.grid = zmq.Context().socket(zmq.PUB)
        #self.grid.bind('tcp://127.0.0.1:2000')
        self.interval_asks = {}
        self.interval_bids = {}
        self.interval_trades ={}
        self.finalized = -1

        #RESOURCE MANAGEMENT PARAMETERS
        #NETWORK
        self.blk = 512
        self.min = 1*self.blk
        self.max = 4*self.blk
        self.msg_size = self.min


        logpath = '/tmp/' + logfile + '.log'
        self.killLog = 'killLog.log'
        try: os.remove(logpath)
        except OSError: pass
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.WARNING)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.warning("(PID %s) - starting Trader",str(self.pid))

    def on_contractAddr(self):
        try :
            req = self.contractAddr.recv_pyobj()
            if 'contract' in req:
                self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
                self.epoch = time() - req['time']
                self.time_interval = int(time() - self.epoch) // INTERVAL_LENGTH
                self.contract_address = req['contract']
                self.logger.info("Contract address: " + self.contract_address)
                self.logger.info("Setting up connection to Ethereum client...")
                client = EthereumClient(ip=MINER, port=PORT)
                self.account = client.accounts()[0] # use the first owned address
                self.logger.info("Creating contract object...")
                self.contract = MatchingContract(client, self.contract_address)
                self.contract.registerProsumer(self.account, prosumer_id, PROSUMER_FEEDER[prosumer_id])
                self.connected = 1
                self.logger.warning("Connected: %s" %self.connected)
            else :
                self.logger.info("reply is:%s " %req)
        except PortError as e:
            self.logger.info("on_contractAddr:port exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_contractAdd: port error received")


    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))

        if self.connected == 0 :
            self.query_contract_address()
        elif self.connected == 1 :
            self.logger.debug("Polling events...")


            # if self.time_interval == 28 and self.prosumer_id == 106:
            #     with open(self.killLog, 'a') as f:
            #         f.write("KILL PROCESS: %s" %time())
            #     self.logger.warning("KILL PROCESS: %s" %time())
            #     os.kill(self.pid,signal.SIGKILL)


            events = self.contract.poll_events()
#             try:# added this because laptop lost connection, and would need to reconnect to miner and grafana
#                 events = self.contract.poll_events()
#             except Exception as e:
#                 self.logger.warning("LOST CONNECTION TO HOST: %s" %e)
#                 self.connected =0


            for event in events: #self.contract.poll_events():
                params = event['params']
                name = event['name']
                if (name == "BuyingOfferPosted") and (params['prosumer'] == self.prosumer_id):
                    self.buying_offers.add(params['ID'])
                    self.logger.info("{}({}).".format(name, params))
                elif (name == "SellingOfferPosted") and (params['prosumer'] == self.prosumer_id):
                    self.selling_offers.add(params['ID'])
                    self.logger.info("{}({}).".format(name, params))
                elif (name == "TradeAdded") and ((params['sellerID'] in self.selling_offers) or (params['buyerID'] in self.buying_offers)):
                    self.logger.info("{}({}).".format(name, params))
                elif name == "Finalized":
                    self.finalized = params['interval']
                    self.logger.info("interval finalized : {}".format(self.finalized))
                    self.interval_trades[self.finalized] = [] #List of trades finalized for a given interval
                    self.time_interval = self.finalized + 1
                    self.logger.info("time_interval: %s = finalized: %s + 1" %(self.time_interval, self.finalized))
                    self.dbase.log(self.finalized-2, "interval_now", self.prosumer_id, self.finalized-2)
                    self.dbase.log(self.time_interval, self.prosumer_id, self.role, 0)



                elif (name == "TradeFinalized") and ((params['sellerID'] in self.selling_offers) or (params['buyerID'] in self.buying_offers)):
                    self.logger.warning("{}({}).".format(name, params))
                    time_interval = params['time']
                    power = params['power']
                    self.interval_trades[time_interval].append(power)
                    #self.grid.send_pyobj({"interval" : self.finalized, "power": self.roleID*sum(self.interval_trades[self.finalized]), "INTERVAL_LENGTH" : INTERVAL_LENGTH, "time_stamp" : next_actuation})
                    self.dbase.log(time_interval, self.prosumer_id, self.role, sum(self.interval_trades[time_interval]))

                    self.ack.send_pyobj("%s" %(self.prosumer_id)) #Time Sensitive Messaging
            # self.waste_network()


    def on_post(self):
        now = self.post.recv_pyobj()
        self.logger.info('PID(%s) - on_post(): %s',str(self.pid),str(now))
        if self.connected :
            self.post_offers(self.time_interval)

    def handleActivate(self):
        with open(self.killLog, 'a') as f:
            f.write("Live: %s" %time())
        self.logger.warning("handleActivate: %s" %time())
        self.logger.warning("UUID: %s" %self.getUUID())
#         self.cltReqPort.set_recv_timeout(1.0)
#         self.cltReqPort.set_send_timeout(1.0)
#         rto = self.cltReqPort.get_recv_timeout()
#         sto = self.cltReqPort.get_send_timeout()
#         self.logger.info("handleActivate: (rto,sto) = (%s,%s)" % (str(rto),str(sto)))

    def handlePeerStateChange(self,state,uuid):
        self.logger.warning("UUID: %s, STATE: %s" %(uuid, state))

    def handleNICStateChange(self, state):
        if state=="down":
            self.logger.warning("UUID: %s" %self.getUUID())
            self.logger.warning("NIC is %s" % state)
            self.connected = 0
            self.logger.warning("Connected: %s" %self.connected)
        elif state =="up":
            self.logger.warning("NIC is %s" % state)
#             self.connectGrafana()#This appears to be unnecessary...
#

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping Trader",str(self.pid))


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


    def post_offers(self, time_interval):
        remaining_offers = []
        self.logger.info("Posting offers for interval {}...".format(time_interval))
        for offer in self.net_production:
            self.logger.info("energy: %s" %(offer['energy']))
            if offer['end'] < time_interval: # offer in the past, discard it
                pass
            elif offer['start'] <= time_interval + PREDICTION_WINDOW: # offer in near future, post it
                if offer['energy'] < 0:
                    self.role = "consumer"
                    self.roleID = -1
                    self.logger.info("postBuyingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'], -offer['energy']))
                    self.contract.postBuyingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], -offer['energy'])
                    try:
                        self.interval_bids[offer['start']].append(offer['energy'])
                    except KeyError:
                        self.interval_bids[offer['start']] = [offer['energy']]
                    self.dbase.log(offer['start'], self.prosumer_id, "buying", sum(self.interval_bids[offer['start']]))
                else:
                    self.role = "producer"
                    self.roleID = 1
                    self.logger.info("postSellingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'], offer['energy']))
                    self.contract.postSellingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], offer['energy'])
                    try:
                        self.interval_asks[offer['start']].append(offer['energy'])
                    except KeyError:
                        self.interval_asks[offer['start']] = [offer['energy']]
                    self.dbase.log(offer['start'], self.prosumer_id, "selling", sum(self.interval_asks[offer['start']]))
            else: # offer in far future, post it later
                remaining_offers.append(offer)
            self.net_production = remaining_offers
            self.logger.info("Offers posted.")

    def read_data(self, prosumer_id):
        self.logger.info("Reading net production values...")
        feeder = int(prosumer_id / 100)
        prosumer = prosumer_id % 100
        print(os.getcwd())
        with open(DATA_PATH + "prosumer_{}.csv".format(prosumer_id), "rt") as fin:
            line = next(fin)
            data = []
            for line in fin:
                try:
                    fields = line.split(',')
                    data.append({
                        'start': int(fields[0]),
                        'end': int(fields[1]),
                        'energy': int(1000 * float(fields[2]))
                        })
                except Exception:
                    pass
            if not len(data):
                raise Exception("No values found in data file!")
            self.logger.info("Read {} values.".format(len(data)))
            return data

    def handleCPULimit(self):
        self.logger.info('handleCPULimit()')

    def handleMemLimit(self):
        self.logger.info('handleMemLimit()' )

    def handleNetLimit(self):
        self.logger.info('handleNetLimit %s' %self.msg_size)
        self.msg_size = self.min
        self.logger.info('handled NetLimit %s' %self.msg_size)
        now = datetime.datetime.now()
        self.dbase.post(now=now, tag_dict={"resource":"Network", "ID":self.prosumer_id}, seriesName="Waste", value=self.msg_size)

    def waste_network(self):
        msg = {
            'request': "waste",
            'payload': bytearray(self.msg_size)
        }
        self.logger.info("WASTE NETWORK")
        try:
            self.contractAddr.send_pyobj(msg)
            self.msg_size = self.msg_size + self.blk
#             if self.msg_size == self.max: self.msg_size = self.min
            now = datetime.datetime.now()
            self.dbase.post(now=now, tag_dict={"resource":"Network", "ID":self.prosumer_id}, seriesName="Waste", value=self.msg_size)
        except PortError as e:
            self.logger.info("waste_network:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("waste_network: try again")
