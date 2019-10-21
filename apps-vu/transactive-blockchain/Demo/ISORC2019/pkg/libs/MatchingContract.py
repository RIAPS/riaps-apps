import logging

from libs.Contract import Contract
#from Contract import Contract

class MatchingContract(Contract):
  def __init__(self, client, address):
    super(MatchingContract, self).__init__(client, address, [
      "ProsumerRegistered(uint64 prosumer, uint64 feeder)",
      "BuyingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy)",
      "SellingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy)",
      "SolutionCreated(uint64 solutionID, uint64 solverID)",
      "TradeAdded(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power, uint64 objective)",
      "Finalized(uint64 interval, int64 bestSolution)",
      "TradeFinalized(uint64 sellerID, uint64 buyerID, uint64 time, uint64 power)"
    ])
    
  def setup(self, from_account, _Cint, _Cext, _nextInterval):
    self.call_func(from_account, "setup",
      "uint64", _Cint,
      "uint64", _Cext,
      "uint64", _nextInterval)      
    
  def registerProsumer(self, from_account, prosumer_id, feeder_id):
    self.call_func(from_account, "registerProsumer",
      "uint64", prosumer_id,
      "uint64", feeder_id)

  def postBuyingOffer(self, from_account, prosumer_id, start_time, end_time, energy):
    self.call_func(from_account, "postBuyingOffer", 
      "uint64", prosumer_id, 
      "uint64", start_time, 
      "uint64", end_time, 
      "uint64", energy)

  def postSellingOffer(self, from_account, prosumer_id, start_time, end_time, energy):
    self.call_func(from_account, "postSellingOffer", 
      "uint64", prosumer_id, 
      "uint64", start_time, 
      "uint64", end_time, 
      "uint64", energy)
            
  def createSolution(self, from_account, solverID):
    self.call_func(from_account, "createSolution",
      "uint64", solverID)
    
  def addTrade(self, from_account, solutionID, sellerID, buyerID, time, power):
    self.call_func(from_account, "addTrade",
      "uint64", solutionID,
      "uint64", sellerID,
      "uint64", buyerID,
      "uint64", time,
      "uint64", power)
      
  def finalize(self, from_account, time_interval):
    self.call_func(from_account, "finalize",
      "uint64", time_interval)

