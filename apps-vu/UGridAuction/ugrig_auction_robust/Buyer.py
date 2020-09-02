'''
Created on Oct 12, 2018

@author: purboday
'''
from riaps.run.comp import Component
import logging
import time
import os


class Buyer(Component):
    def __init__(self, buyernum):
        super(Buyer, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting buyer, %s" %(str(self.pid),str(now)))
        self.benefit = [2,2,0]
        self.increment = 0.4
        self.buyernum = buyernum
        self.assigned = ''
        self.price = [0,0,0]
        self.pulse = 0
#         self.started = False
        self.sellers = 3
        self.seller_resp = 0
        self.bid = False
        self.uuid = ""
        self.sellerinfo = {}
        
    def handleActivate(self):
        self.uuid = self.getUUID()
#         self.timeout.setDelay(60.0)
#         self.timeout.launch()
    
    def on_collect(self):
        msg = self.collect.recv_pyobj()
        msg= msg.split('_')
        self.logger.info('received from seller %s price %s' %(msg[0], msg[1]))
        self.sellerinfo[msg[2]] = (msg[0], 'on')
        if not self.bid:
            self.price[int(msg[0])-1]= float(msg[1])
            self.seller_resp += 1
            if not self.assigned == '':
                if self.seller_resp == self.sellers:
                    self.seller_resp = 0
                    msg = 'assigned,'+self.buyernum+','+self.assigned+','+self.uuid
#                     self.bid = True
                    self.bidport.send_pyobj(msg)
            else:
                if self.seller_resp == self.sellers:
                    self.bid = True
#                     self.timeout.halt()
                    self.waitbid()
        else:
            self.logger.info("bid not reset")
#         if not self.started:
#             self.started = True

#     def on_timeout(self):
#         now = self.timeout.recv_pyobj()
#         self.logger.info("timeout")
#         self.timeout.halt()
#         if not self.bid:
#             if not self.assigned == '':
#                 self.seller_resp = 0
#                 msg = 'assigned,'+self.buyernum+','+self.assigned+','+self.uuid
#                 self.bidport.send_pyobj(msg)
#             else:
#                 self.bid = True
#                 self.waitbid()
        
#     def on_waitbid(self):
#         now = self.waitbid.recv_pyobj()
#         if self.started:
#             self.pulse += 1
#             if self.pulse == 4:
#                 self.logger.info('calculating bids')
#                 cost = []
#                 for i in range(len(self.price)):
#                     cost.append(self.benefit[i] - self.price[i])
#                 max_value = max(cost)
#                 max_index = cost.index(max_value) + 1
#                 cost.pop(max_index)
#                 second_max = max(cost)
#                 bidamt = max_value - second_max + self.increment
#                 msg = str(max_index)+','+str(bidamt)+','+self.buyernum
#                 self.logger.info('buyer (PID %s) bid %f for object %d' %(self.pid,bidamt,max_index))
#                 self.bidport.send_pyobj(msg)
#                 self.started = False
                
    def waitbid(self):
#     now = self.waitbid.recv_pyobj()
        self.logger.info('calculating bids')
        self.seller_resp = 0
        cost = []
        self.logger.info(str(len(self.price)))
        for i in range(len(self.price)):
            cost.append(self.benefit[i] - self.price[i])
        max_value = max(cost)
        max_index = cost.index(max_value)
        cost.pop(max_index)
        second_max = max(cost)
        bidamt = max_value - second_max + self.increment
        msg = str(max_index + 1)+','+str(bidamt)+','+self.buyernum+','+self.uuid
        self.logger.info('buyer %s bid %f to Seller %d' %(self.buyernum,bidamt,(max_index+1)))
        self.bidport.send_pyobj(msg)
        self.bid = False
#         self.started = False
            
        
    def on_freebuyer(self):
        msg = self.freebuyer.recv_pyobj()
        msg = msg.split('_')
        if msg[1] == self.buyernum:
            if msg[0] == 'assigned':
                self.assigned = msg[2]
                self.logger.info('buyer %s assigned Seller %s' %(self.buyernum, self.assigned))
                pair = self.buyernum+'_'+self.assigned
            elif msg[0] == 'freed':
                self.assigned = ''
                self.logger.info('buyer %s freed' % self.buyernum)
                pair = self.buyernum+'_free'
            self.bid = False
            self.statusport.send_pyobj(pair)
            self.sendack.send_pyobj(pair)
            
    def on_prepare(self):
        msg = self.prepare.recv_pyobj()
        if msg == 'start':
            self.assigned = ''
            self.seller_resp = 0
            self.bid = False
            
    def handlePeerStateChange(self, state, uuid):
        if state == off:
            self.logger.info("peer %s went offline" % uuid)
            if uuid in self.sellerinfo:
                self.sellerinfo[uuid][1] = 'off'
                self.sellers -= 1
                self.logger.info("%s is off, number of sellers = %d" % (self.sellerinfo[uuid][0], self.sellers))
                if self.assigned == self.sellerinfo[uuid][0]:
                    self.assigned = ''
                if not self.bid:
                    if not self.assigned == '':
                        if self.seller_resp == self.sellers:
                            self.seller_resp = 0
                            msg = 'assigned,'+self.buyernum+','+self.assigned+','+self.uuid
                            self.bidport.send_pyobj(msg)
                    else:
                        if self.seller_resp == self.sellers:
                            self.bid = True
                            self.waitbid()
                    
                       
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping Buyer, %s" %(str(self.pid),now))         
