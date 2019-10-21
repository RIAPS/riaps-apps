#Solver.py
from riaps.run.comp import Component
from riaps.run.exc import PortError
import os
import subprocess
import pwd
import signal
import psutil
import logging
import requests

from time import time, sleep

import libs.config as cfg
# from libs.config import *
from libs.MatchingSolver import MatchingSolver, Offer
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime



import random, string
from cgi import logfile
from pexpect.replwrap import bash




def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Solver(Component):
    def __init__(self,logfile):
        super(Solver, self).__init__()
        self.pid = os.getpid()

        self.logger.info("(PID %s) - starting Solver",str(self.pid))

        #Waste Space parameters
        self.delta = 1 # 1 MB #
        self.size = self.delta
        self.name = '/tmp/tmp%s' % randomword(8)
        self.logger.info(os.getcwd())

        #App Specific parameters
        self.solverID = 1
        print("solverID %s" %self.solverID)
        self.solution = None
        self.objective = 0
        self.connected =0
        self.new_offers = False
        self.solver = MatchingSolver(cfg.MICROGRID)
        self.buying_offers = []
        self.selling_offers = []
        self.finalized = -1
        self.waiting_solutionID = False
        self.PREDICTION = False
        self.PREDICTION_WINDOW = cfg.PREDICTION_WINDOW
        self.recordTime = False
        self.interval_trades ={}
        self.solutions ={}
        self.ISID = 0
        self.DeadLine = 0.5 #seconds ideally this would be gotten from the framework API
        self.Pgain = 25#50
        self.PWMax = 50
        self.priorPW = self.PREDICTION_WINDOW


        self.logpath = '/tmp/' + logfile + '.log'
        self.killLog = 'killLog.log'
        try: os.remove(self.logpath)
        except OSError: pass
        self.fh = logging.FileHandler(self.logpath)
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)
        self.logger.info("(PID %s) - starting Solver",str(self.pid))
        self.s = open('/dev/zero').read(1024*100-1)

        self.dbase = Database()
        self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

        self.uid = os.geteuid()
#         self.logger.info("UID: %s" %self.uid)
        self.username = pwd.getpwuid(self.uid)[0]
#         self.logger.info("USERNAME: %s" %self.username)

        self.thisProcess = psutil.Process(self.pid)
        self.cpuUtil = self.thisProcess.cpu_percent()




    # def connectGrafana(self):
    #     try :
    #         # self.db = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
    #         #                          Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
    #         #                          "solverDbase")
    #         # self.db.create_database(Config.INFLUX_DBASE_NAME)
    #         # self.db.switch_database(Config.INFLUX_DBASE_NAME)
    #         self.dbase = Database()
    #         self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)
    #
    #     except requests.exceptions.ConnectionError as e:
    #         self.logger.warning("CONNECTION ERROR %s" %e)
    #         self.logger.warning("try again")
    #         self.connectGrafana()





#     def on_contractAddr(self):
#         self.logger.info("on_contractAddr()")
#
#         req = self.contractAddr.recv_pyobj()
#         self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
#
#         self.epoch = time() - req['time']
#         self.contract_address = req['contract']
#         self.logger.info("Contract address: " + self.contract_address)
#         self.logger.info("Setting up connection to Ethereum client...")
#         client = EthereumClient(ip=MINER, port=PORT)
#         self.account = client.accounts()[0] # use the first owned address
#         self.logger.info("Creating contract object...")
#         self.contract = MatchingContract(client, self.contract_address)
#         self.connected = 1

    def on_contractAddr(self):
        try :
            req = self.contractAddr.recv_pyobj()
            if 'contract' in req:
                self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
                self.epoch = time() - req['time']
                self.time_interval = int(time() - self.epoch) // cfg.INTERVAL_LENGTH

                self.solutions[self.time_interval]={}

                self.contract_address = req['contract']
                self.logger.info("Contract address: " + self.contract_address)
                self.logger.info("Setting up connection to Ethereum client...")
                client = EthereumClient(ip=cfg.MINER, port=cfg.PORT)
                self.account = client.accounts()[0] # use the first owned address
                self.logger.info("Creating contract object...")
                self.contract = MatchingContract(client, self.contract_address)
                # self.contract.registerProsumer(self.account, prosumer_id, cfg.PROSUMER_FEEDER[prosumer_id])
                self.connected = 1

            else :
                self.logger.info("reply is:%s " %req)
        except PortError as e:
            self.logger.info("on_contractAddr:port exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_contractAdd: port error received")



    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        self.logger.info('update')

        if self.connected == 0 :
            self.query_contract_address()

        elif self.connected == 1 :
            self.logger.debug("Polling events...")
            #
            # if self.time_interval == 28:
            #     with open(self.killLog, 'w') as f:
            #         f.write("KILL PROCESS: %s" %time())
            #     self.logger.warning("KILL PROCESS: %s" %time())
            #     os.kill(self.pid,signal.SIGKILL)

            for event in self.contract.poll_events():
                params = event['params']
                name = event['name']
                self.logger.info("{}({}).".format(name, params))

                if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
                    self.new_offers = True
                    offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'])
                    if name == "BuyingOfferPosted":
                        self.buying_offers.append(offer)
                    else:
                        self.selling_offers.append(offer)
                elif (name == "SolutionCreated") and (params['solverID'] == self.solverID):

                    self.waiting_solutionID = False
                    solutionID = params['solutionID']

                    self.solutions[self.time_interval][self.ISID]=solutionID

                    if self.solution is not None:
                        self.logger.info("Solution {} created by contract, adding trades...".format(solutionID))
                        trades = [trade for trade in self.solution if int(trade['p']) > 0]
                        for trade in trades:
                            self.contract.addTrade(self.account, solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
                        self.logger.info("{} trades have been submitted to the contract.".format(len(trades)))

#                         if self.PREDICTION_WINDOW < 60:
#                             self.PREDICTION_WINDOW +=5
#                         self.logger.info("PREDICTION_WINDOW: %s" %self.PREDICTION_WINDOW)
#                         self.dbase.post(now=datetime.datetime.now(), tag_dict={"resource":"Memory", "ID":'Solver'+str(self.solverID)}, seriesName="Waste", value=self.PREDICTION_WINDOW)

                    else:
                        self.logger.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
                elif name == "Finalized":

                    self.logger.info("INTERVAL:%s SOLUTIONS: %s" %(self.time_interval, self.solutions[self.time_interval]))

                    self.finalized = params['interval']
                    self.time_interval = self.finalized + 1
                    self.objective = float("-inf")
                    self.solution = None

                    self.solutions[self.time_interval]={}

                    if self.waiting_solutionID:
                        self.logger.error("INTERVAL FINALIZED BEFORE SOLUTION WAS CREATED, AND TRADES ADDED")
                        self.waiting_solutionID = False
                    # new_offers = False # TODO: offers for next interval might be added in the same block as the finalization for the previous!
                    self.logger.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(self.finalized))
                    self.logger.info("New interval is : {}".format(self.time_interval))

                elif name == "TradeFinalized":
                    self.logger.info("{}({}).".format(name, params))
                    for offer in self.selling_offers:
                        if offer.ID == params['sellerID']:
                            offer.energy -= params['power']
                            break
                    for offer in self.buying_offers:
                        if offer.ID == params['buyerID']:
                            offer.energy -= params['power']
                            break

                elif name == "TradeAdded":
                    self.logger.info("{}({}).".format(name, params))


#         bashCommand = 'quota -w %s | awk "NR==3"' %self.uid # returns row
# #             self.logger.info("bashCommand: %s" %bashCommand)
#         p1 = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
#         output, error = p1.communicate()
#         quota = " ".join(output.decode().split()).split(' ')
# #         self.logger.info("QUOTA: %s" %quota)
#         space = quota[1].strip('*') # I think the asterisk shows because the value is changing.
# #         self.logger.info("SPACE: %s" %space)
#         limit = quota[3]
        now=datetime.datetime.now()

        self.cpuUtil = self.thisProcess.cpu_percent()
        self.memUsage = self.thisProcess.memory_info()
#         self.logger.info("rss: %s" %self.memUsage[0])
        # self.dbase.post(now=now , tag_dict={"disk":"space"}, seriesName="Disk", value=space)
        # self.dbase.post(now=now , tag_dict={"disk":"limit"}, seriesName="Disk", value=limit)
        self.dbase.post(now=now , tag_dict={"cpu":"use"}, seriesName="CPU", value=self.cpuUtil)
        self.dbase.post(now=now , tag_dict={"mem":"rss"}, seriesName="Mem", value=self.memUsage[0])
        self.dbase.post(now=now , tag_dict={"mem":"vms"}, seriesName="Mem", value=self.memUsage[1])




    def on_solve(self):

        timer={}
        timer['start']=time()
        now = self.solve.recv_pyobj()
        self.logger.info('PID(%s) - on_solve(): %s',str(self.pid),str(now))


        if self.connected:
            if (self.new_offers or self.solutions[self.time_interval]=={}) :
                if self.new_offers:
                    self.logger.info("NEW OFFERS")
                if self.solutions[self.time_interval]=={}:
                    self.logger.info("NEW INTERVAL")
                self.ISID+=1
                self.solutions[self.time_interval][self.ISID]=None

                self.recordTime = True
                self.new_offers = False
                self.logger.info("Solving...")
                stopWatch = {"interval":self.time_interval, "start":time(), "running" : 1}

    #             self.logger.info("buying offers")
    #             for offer in self.buying_offers:
    #                 self.logger.info("%s, %s, %s, %s, %s" %(str(offer.ID), str(offer.prosumer), str(offer.startTime), str(offer.endTime), str(offer.energy)))
    #
    #             self.logger.info("selling offers")
    #             for offer in self.selling_offers:
    #                 self.logger.info("%s, %s, %s, %s, %s" %(str(offer.ID), str(offer.prosumer), str(offer.startTime), str(offer.endTime), str(offer.energy)))

                boffers=[]
                for offer in self.buying_offers:
                    if offer.endTime < self.time_interval:
                        pass
                    elif offer.startTime <= self.time_interval + self.PREDICTION_WINDOW:
                        # print(offer.__dict__)
                        boffers.append(offer)

                soffers=[]
                for offer in self.selling_offers:
                    if offer.endTime < self.time_interval:
                        pass
                    elif offer.startTime <= self.time_interval + self.PREDICTION_WINDOW:
                        # print(offer.__dict__)
                        soffers.append(offer)

                (solution, objective) = self.solver.solve(boffers, soffers, finalized=self.finalized)
                stopWatch["split"] = time()-stopWatch["start"]
                now=datetime.datetime.now()

                self.logger.info("Solve Time: %s, buy offers: %s, sell offers: %s, total: %s"
                                 %(stopWatch["split"], len(self.buying_offers), len(self.selling_offers),
                                   len(self.buying_offers)+len(self.selling_offers) ))

                if objective > self.objective:
                    self.solution = solution
                    self.objective = objective
                    self.logger.info("interval: {}, New solution: (objective = {}).".format(self.time_interval,objective))

                    self.interval_trades[self.time_interval]=0
                    for offer in self.solution:
                        self.logger.info("interval: %s; trade interval: %s" %(self.time_interval, offer['t']))
                        if offer['t'] == self.time_interval:
                            self.interval_trades[self.time_interval] += offer['p']
                    energy = self.interval_trades[self.time_interval]
                    self.logger.info("Interval: {}, Proposed Energy: {}".format(self.time_interval, energy))


                    if not self.waiting_solutionID:
                        self.contract.createSolution(self.account, self.solverID)
                        self.waiting_solutionID = True
                        self.logger.info("Trades will be submitted once a solution is created in the contract.")
                else:
                    self.logger.info("No better solution found (objective = {}).".format(objective))

            try:
                self.dbase.post(now=datetime.datetime.now(), tag_dict={"resource":"storage"}, seriesName="Waste", value=os.stat(self.logpath).st_size)
            except FileNotFoundError as e:
                self.logger.info("file does not exist")

    #         self.waste()
            timer['stop']=time()
            timer['split'] = timer['stop'] - timer['start']
            if self.recordTime:

                self.recordTime = False
                self.logger.info("SOLVE TIME: %s PREDICTION WINDOW: %s" %(timer['split'], self.PREDICTION_WINDOW))
                error = timer['split'] - self.DeadLine
                self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="error", value=error)


                if not self.PREDICTION:
                    self.priorPW = self.PREDICTION_WINDOW
                    self.PREDICTION_WINDOW = self.PREDICTION_WINDOW +5 #- self.Pgain*error
                    if self.PREDICTION_WINDOW < 0:
                        self.PREDICTION_WINDOW =0
                    if self.PREDICTION_WINDOW > self.PWMax:
                        self.PREDICTION_WINDOW = self.PWMax
                    self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PW", value=self.PREDICTION_WINDOW)

                self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="on_solve_time", value=timer["split"])
                self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="solveTime", value=stopWatch["split"])



    def handleSpcLimit(self):
        '''This is a function called by the riaps platform and should be generated if we are doing disk limits'''
        self.logger.warning('handleSpcLimit() ')
        try:
            with open(self.logpath, 'w'): #opening the log file like this truncates it.
                pass
#             os.remove(self.logpath)
#             os.remove(self.name)
#             self.size = self.delta
#             now = datetime.datetime.now()
#             self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)

        except FileNotFoundError as e:
            self.logger.info("handleSpcLimit: Remove Error = %s" % e)
            self.logger.info("file does not exist")

    def handleMemLimit(self):
        now = datetime.datetime.now()
        memNow = self.thisProcess.memory_info()
        self.logger.warning('handleMEMLimit(): %s' %str(memNow))
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="RSSNow", value=memNow[0])
            self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleDeadline(self,funcName):
        self.logger.warning("handleDeadline(): %s" % funcName)
        #if self.self.Pgain += 1
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleCPULimit(self):
        self.logger.warning('handleCPULimit()')
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleNICStateChange(self, state):
        if state=="down":
            self.logger.warning("NIC is %s" % state)
            # lost connection to contract
            self.connected = 0
            # self.connectGrafana()
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)
        else:
            self.logger.warning("NIC is %s" % state)



    def __destroy__(self):
        self.logger.info("(PID %s) - stopping Solver",str(self.pid))


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

    def waste(self):
        self.logger.info("WASTE %s" %self.s)
#         try:
# #             cmd = 'dd if=/dev/zero of=%s bs=1M count=%d' % (self.name,self.size)
# #             res = os.system(cmd)
#             self.logger.info(self.s)
#         except:
#             self.logger.info("waste: op failed at %d" % (self.size))
#         if res == 0:
#             self.size += self.delta
#         now = datetime.datetime.now()
#         self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)
