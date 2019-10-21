import logging

class Contract:
  def encode_address(address):
    return "000000000000000000000000" + address[2:]

  def encode_uint(value):
    return format(value, "064x")

  def encode_int(value):
    return format(value & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, "064x")
 
  def decode_address(data, pos):
    return "0x" + data[pos * 64 + 24 : (pos + 1) * 64]

  def decode_uint(data, pos):
    return int(data[pos * 64 : (pos + 1) * 64], 16)

  def decode_int(data, pos):
    uint = Contract.decode_uint(data, pos)
    if uint > 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff:
      uint -= 0x10000000000000000000000000000000000000000000000000000000000000000
    return uint
    
  def generate_topics(self, events):
    self.topics = {}
    for event in events:
      name = event.split("(")[0].strip()
      topic = {'name': name}
      params = []
      for param in [s.strip() for s in event.split("(")[1].replace(")", "").split(",")]:
        ptype = param.split(" ")[0]
        pname = param.split(" ")[-1]
        params.append((ptype, pname))
      topic['params'] = params
      signature = "{}({})".format(name, ",".join([ptype for (ptype, pname) in params]))
      keccak256 = self.client.keccak256(signature)
      if not (keccak256.startswith("0x") and len(keccak256) == 66):
        raise Exception("Incorrect hash {} computed for signature {}!".format(keccak256, signature))
      self.topics[keccak256] = topic 
   
  def __init__(self, client, address, events):
    self.client = client # instance of EthereumClient
    self.address = address # Ethereum contract address
    self.filter_id = client.new_filter()
    self.func_hash = {}
    self.generate_topics(events)
    
  def call_func(self, from_account, name, *args):
    # generate signature
    arg_types = []
    arg_values = []
    for i in range(len(args) >> 1):
      arg_types.append(args[i * 2])
      arg_values.append(args[i * 2 + 1])
    signature = "{}({})".format(name, ",".join(arg_types))
    if signature not in self.func_hash:
      keccak256 = self.client.keccak256(signature)
      if not (keccak256.startswith("0x") and len(keccak256) == 66):
        raise Exception("Incorrect hash {} computed for signature {}!".format(keccak256, signature))
      self.func_hash[signature] = keccak256[:10]
    data = self.func_hash[signature]
    # encode arguments
    for i in range(len(arg_types)):
      if arg_types[i] == "uint64":
        data += Contract.encode_uint(arg_values[i])
      elif arg_types[i] == "int64":
        data += Contract.encode_int(arg_values[i])
      elif arg_types[i] == "address":
        data += Contract.encode_address(arg_values[i])
      else:
        raise Exception("Unknown type {}!".format(arg_types[i]))
    # send transaction
    self.client.transaction(from_account, data, self.address)
    
  def poll_events(self):
    log = self.client.get_filter_changes(self.filter_id)
    events = [] 
    for item in log:
      if self.address == item['address']:
        if item['topics'][0] in self.topics:
          topic = self.topics[item['topics'][0]]
          event = {'name': topic['name']}
          params = {}
          data = item['data'][2:]
          data_pos = 0
          for (ptype, pname) in topic['params']:
            if ptype == "uint64":
              params[pname] = Contract.decode_uint(data, data_pos)
            elif ptype == "int64":
              params[pname] = Contract.decode_int(data, data_pos)
            elif ptype == "address":
              params[pname] = Contract.decode_address(data, data_pos)
            data_pos += 1
          event['params'] = params 
          events.append(event)        
    return events

