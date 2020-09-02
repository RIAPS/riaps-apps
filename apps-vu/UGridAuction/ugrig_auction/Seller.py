'''
Created on Oct 12, 2018

@author: purboday
'''
from riaps.run.comp import Component
import logging
import time
import os


class Seller(Component):
    def __init__(self, sellernum):
        super(Seller, self).__init__()
        self.pid = os.getpid()
        now = time.ctime(int(time.time()))
        self.logger.info("(PID %s)-starting Seller, %s" %(str(self.pid),str(now)))
        self.sellernum = str(sellernum)
        self.bidamt = 0
        self.assigned = ''
        self.winner = ''
        self.price = 0
        self.active = False
        self.pulse = 0
        self.buyers = 3
        self.assignedbuyers = {}
        self.biddingbuyers = 0
        
    def on_assignport(self):
        # Receive bid
        msg = self.assignport.recv_pyobj()
        self.logger.info(str(msg))
        if self.active == True:   
            msg = msg.split(',')
            if not msg[0] == 'assigned':
                self.biddingbuyers+= 1
                obj = str(msg[0])
                bidamt = float(msg[1])
                buyernum = msg[2]
                if obj == self.sellernum:
                    self.logger.info("Seller %s received bid %f from Buyer %s" % (self.sellernum, bidamt, buyernum))
                    if bidamt >= self.bidamt:
                        self.bidamt = float(msg[1])
                        self.winner = buyernum
            else:
                self.assignedbuyers[msg[1]] = msg[0]
            self.logger.info('assigned = %d, bidding = %d' % (len(self.assignedbuyers), self.biddingbuyers))
            if self.biddingbuyers + len(self.assignedbuyers) == self.buyers:
                if len(self.assignedbuyers) < self.buyers:
                    self.assignment()
    
#     def on_timeout(self):
#         now = self.timeout.recv_pyobj()
#         if self.active:
#             self.pulse += 1
#             if self.pulse == 4:   
#                 self.active = False
#                 self.logger.info('finalizing bids for seller [PID: %s]' %(self.pid))
#                 if not self.assigned == '':
#                     freed = self.assigned
#                 else:
#                     freed = ''
#                 self.assigned = self.winner
#                 self.logger.info("seller %s temporarily assigned to buyer %s" % (self.sellernum, self.assigned))
#                 self.freebuyer.send_pyobj('assigned_'+self.assigned+'_'+self.sellernum)
#                 if not freed == '':
#                     self.freebuyer.send_pyobj('freed_'+freed)
#                 self.price += self.bidamt
#                 msg = self.sellernum+'_'+str(self.price)
#                 self.logger.info('seller %s sending new price' % self.sellernum)
#                 self.sendprice.send_pyobj(msg)
#                 self.active = True
#                 self.pulse = 0
                
    def assignment(self):
#     now = self.timeout.recv_pyobj()
        self.logger.info('finalizing bids for seller [PID: %s]' %(self.pid))
        self.price += self.bidamt
        if not self.winner == '':
            if not self.assigned == '':
                freed = self.assigned
            else:
                freed = ''
            self.assigned = self.winner
            self.logger.info("seller %s temporarily assigned to buyer %s" % (self.sellernum, self.assigned))
            self.freebuyer.send_pyobj('assigned_'+self.assigned+'_'+self.sellernum)
            if not freed == '':
                self.freebuyer.send_pyobj('freed_'+freed)
        else:
            msg = self.sellernum+'_'+str(self.price)
            self.logger.info('seller %s sending new price' % self.sellernum)
            self.assignedbuyers.clear()
            self.biddingbuyers = 0
            self.winner = ''
            self.bidamt = 0
            time.sleep(5)
            self.sendprice.send_pyobj(msg)
        
    def on_recvack(self):
        resp = self.recvack.recv_pyobj()
        if not self.winner == '':
            msg = self.sellernum+'_'+str(self.price)
            self.logger.info('seller %s sending new price' % self.sellernum)
            self.assignedbuyers.clear()
            self.biddingbuyers = 0
            self.winner = ''
            self.bidamt = 0
            time.sleep(5)
            self.sendprice.send_pyobj(msg)
        
            
    def on_notify(self):
        msg = self.notify.recv_pyobj()
        if msg == 'start':
            self.active = True
            self.logger.info('starting negotiation round')
            self.assignedbuyers.clear()
            self.biddingbuyers = 0
            self.winner = ''
            self.bidamt = 0
            msg = self.sellernum+'_'+str(self.price)
            self.sendprice.send_pyobj(msg)
        elif msg == 'stop':
            self.active = False
            self.logger.info('seller %s assigned to buyer %s' % (self.sellernum, self.assigned))

        
    def __destroy__(self):
        now = time.time()
        self.logger.info("%s - stopping Seller, %s" %(str(self.pid),now))