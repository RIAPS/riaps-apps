class Microgrid:
  def __init__(self, interval_length, C_ext, C_int, feeders, prosumer_feeder):
    self.interval_length = interval_length
    self.C_ext = C_ext
    self.C_int = C_int
    self.feeders = feeders
    self.prosumer_feeder = prosumer_feeder

