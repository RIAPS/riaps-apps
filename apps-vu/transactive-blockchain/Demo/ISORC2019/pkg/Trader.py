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
import zmq

class Trader(Component):
    def __init__(self,ID,logfile):
        super(Trader, self).__init__()
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Trader",str(self.pid))

        self.prosumer_id = ID
        self.net_production = self.read_data(self.prosumer_id)
        self.selling_offers = set()
        self.buying_offers = set()
        self.connected = 0
        self.logger.warning("Disconnected: %s %s" %(self.connected, str(self.pid)))

        self.dbase = Database()

        self.role = None
        self.roleID = 0

        print("GRID: %s" %GRID)
        self.grid = zmq.Context().socket(zmq.REQ)
        self.grid.connect('tcp://%s:5555' %(GRID))
        self.currentInterval = 0
        self.charge = self.getCharge()


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
                self.working_interval = int(time() - self.epoch) // INTERVAL_LENGTH
                self.currentInterval = self.working_interval - 1
                self.contract_address = req['contract']
                self.logger.info("Contract address: " + self.contract_address)
                self.logger.info("Setting up connection to Ethereum client...")
                client = EthereumClient(ip=MINER, port=PORT)
                self.account = client.accounts()[0] # use the first owned address
                self.logger.info("Creating contract object...")
                self.contract = MatchingContract(client, self.contract_address)
                self.contract.registerProsumer(self.account, prosumer_id, PROSUMER_FEEDER[prosumer_id])
                self.connected = 1
                self.logger.warning("Connected: %s %s" %(self.connected, str(self.pid)))
            else :
                self.logger.info("reply is:%s " %req)
        except PortError as e:
            self.logger.info("on_contractAddr:port exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_contractAdd: port error received")


    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.debug('PID(%s) - on_poller(): %s',str(self.pid),str(now))

        if self.connected == 0 :
            self.logger.info('Connected?: %s %s' %(self.connected==1, str(self.pid)))
            self.query_contract_address()
        elif self.connected == 1 :
            self.logger.debug("Polling events...")


            # if self.working_interval == 28 and self.prosumer_id == 106:
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
                    self.currentInterval = self.finalized - 1
                    self.logger.info("interval finalized : {}".format(self.finalized))
                    self.interval_trades[self.finalized] = [0] #List of trades finalized for a given interval
                    self.working_interval = self.finalized + 1
                    # self.now =
                    self.logger.info("working_interval: %s = finalized: %s + 1" %(self.working_interval, self.finalized))
                    self.dbase.log(self.currentInterval, "interval_now", self.prosumer_id, self.currentInterval)
                    self.dbase.log(self.working_interval, self.prosumer_id, self.role, 0)

                    if self.finalized <= END_INTERVAL:
                        self.charge = self.getCharge()
                        self.postTrade()


                elif (name == "TradeFinalized") and ((params['sellerID'] in self.selling_offers) or (params['buyerID'] in self.buying_offers)):
                    self.logger.warning("{}({}).".format(name, params))
                    finalized_interval = params['time']
                    power = params['power']
                    self.interval_trades[finalized_interval].append(power)

                    if self.finalized <= END_INTERVAL:
                        self.postTrade()

                    self.dbase.log(finalized_interval, self.prosumer_id, self.role, sum(self.interval_trades[finalized_interval]))

                    self.ack.send_pyobj("%s" %(self.prosumer_id)) #Time Sensitive Messaging
            # self.waste_network()

    def getCharge(self):
        # response = {"perUnitCharge":value,
        #          "solarActual": value,
        #          "battActual" : value,
        #          "battCMD" : value,
        #          "OHLcurrent" : value, #overhead line current
        #          }

        msg = {"request":"charge",
               "ID" : str(self.prosumer_id)}

        self.grid.send_pyobj(msg)
        response = self.grid.recv_pyobj()
        # perUnitCharge = response['perUnitCharge'].split(" ")[0][1:]
        perUnitCharge = response['perUnitCharge']
        charge = CAPACITY * perUnitCharge
        self.logger.info("\nCHARGE: %s\n" %charge)

        if self.role == "producer":

            self.dbase.log(interval=self.currentInterval, obj=self.prosumer_id, seriesName="charge", value=charge)

            battCMD = response['battCMD']
            self.logger.info("battCMD: %s" %battCMD)
            self.dbase.log(interval=self.currentInterval, obj=self.prosumer_id, seriesName="battCMD", value=battCMD)

            solarActual = response['solarActual']
            self.logger.info("solarActual: %s" %solarActual)
            self.dbase.log(interval=self.currentInterval, obj=self.prosumer_id, seriesName="solarActual", value=solarActual)

            battActual = response['battActual']
            self.logger.info("battActual: %s" %battActual)
            self.dbase.log(interval=self.currentInterval, obj=self.prosumer_id, seriesName="battActual", value=battActual)

            totalActual = solarActual+battActual
            self.logger.info("totalActual: %s" %totalActual)
            self.dbase.log(interval=self.currentInterval, obj=self.prosumer_id, seriesName="totalActual", value=totalActual)

        return int(charge)

    def postTrade(self):
        power = self.roleID*sum(self.interval_trades[self.finalized])
        msg = {"request": "postTrade",
               "interval": self.finalized,
               "power" : power,
               "ID" : str(self.prosumer_id)
               }
        self.grid.send_pyobj(msg)
        response = self.grid.recv_pyobj()
        self.dbase.log(self.finalized, self.prosumer_id, seriesName="PowerFinalized", value=power)



    def on_post(self):
        now = self.post.recv_pyobj()
        if self.connected and self.finalized <= END_INTERVAL:
            self.logger.debug('PID(%s) - on_post(): %s',str(self.pid),str(now))
            self.post_offers(self.working_interval)

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
            self.logger.warning("Disconnected: %s %s" %(self.connected, str(self.pid)))
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


    def post_offers(self, working_interval):
        remaining_offers = []
        self.logger.debug("Posting offers for interval {}...".format(working_interval))
        for offer in self.net_production:
            self.logger.debug("energy: %s" %(offer['energy']))
            if offer['end'] < working_interval: # offer in the past, discard it
                pass
            elif offer['start'] <= working_interval + PREDICTION_WINDOW: # offer in near future, post it
                if offer['energy'] < 0:
                    self.role = "consumer"
                    self.roleID = -1
                    powerRequested = -offer['energy']*4 # Wh*15min/60min to W
                    self.logger.info("postBuyingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'],powerRequested))
                    self.dbase.log(offer['start'], self.prosumer_id, "expectedLoad", powerRequested)
                    self.contract.postBuyingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], powerRequested)
                    try:
                        self.interval_bids[offer['start']].append(-powerRequested)
                    except KeyError:
                        self.interval_bids[offer['start']] = [-powerRequested]
                    self.dbase.log(offer['start'], self.prosumer_id, "buying", sum(self.interval_bids[offer['start']]))
                else:
                    self.role = "producer"
                    self.roleID = 1

                    solarPower = offer['energy']*4 # convert Wh*15min/1hr = W
                    self.logger.info("solarPower: %s" %solarPower)
                    self.dbase.log(offer['start'], self.prosumer_id, "solarExpected", solarPower)



                    batteryPower = min(self.charge,int(RATED_POWER*LOGICAL_INTERVAL))*4 # Wh*15min/1hr = W
                    self.logger.info("self.charge: %s" %self.charge)
                    self.dbase.log(offer['start'], self.prosumer_id, "battExpected", batteryPower)
                    self.logger.info("RATED_POWER*LOGICAL_INTERVAL: %s" %(RATED_POWER*LOGICAL_INTERVAL))
                    self.logger.info("batteryPower: %s" %batteryPower)

                    powerOffered = solarPower+batteryPower

                    self.logger.info("postSellingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'], powerOffered))
                    # self.logger.info("EnergyOffered: %s" %energyOffered)
                    self.contract.postSellingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], powerOffered)
                    try:
                        self.interval_asks[offer['start']].append(powerOffered)
                    except KeyError:
                        self.interval_asks[offer['start']] = [powerOffered]
                    self.dbase.log(offer['start'], self.prosumer_id, "selling", sum(self.interval_asks[offer['start']]))
                self.logger.info("Offers posted.")
            else: # offer in far future, post it later
                remaining_offers.append(offer)
            self.net_production = remaining_offers


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
                        'energy': int(250 * float(fields[2])) #csv in kW, convert to Wh
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
