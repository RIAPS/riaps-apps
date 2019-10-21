'''
Created on Feb 20, 2017

@author: riaps
'''
import logging

import pprint
from time import time
import requests

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

import datetime
import random
import time
from libs.Grafana.config import Config

class Database(object):
    def __init__(self):
        super(Database, self).__init__()
        self.logger = logging.getLogger(__name__)
        #thing to get values I need
        #---------------------------------------------------------------------------------
        #self.client = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
        #                             Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
        #                             Config.INFLUX_DBASE_NAME)
        self.client = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
                                     Config.INFLUX_DBASE_NAME)
        self.client.switch_database(Config.INFLUX_DBASE_NAME)
        self.create()
        #---------------------------------------------------------------------------------
        self.yesterday = yesterday = datetime.date.today() - datetime.timedelta(days=1)
        #Yesterday at midnight
        self.yesterday0 = datetime.datetime.combine(self.yesterday, datetime.time.min)

    def create(self):
        try :
            self.client.create_database(Config.INFLUX_DBASE_NAME)
        except requests.exceptions.ConnectionError as e:
            self.logger.warning("CONNECTION ERROR %s" %e)
            self.logger.warning("try again")


    def log(self,interval, obj,seriesName,value):
        records = []

        print(interval)

        now = self.yesterday0 + datetime.timedelta(minutes=15*interval)
        print(now)

        if value != None:
            try:
                floatValue = float(value)
            except:
                floatValue = None
        if floatValue != None:
            #---------------------------------------------------------------------------------
            record = {  "time": now,
                        "measurement":seriesName,
                        "tags" : { "object" : obj },
                        "fields" : { "value" : floatValue },
                        }
            records.append(record)
        self.logger.info("writing: %s" % str(records))
        try:
            res= self.client.write_points(records) # , retention_policy=self.retention_policy)
        except requests.exceptions.ConnectionError as e:
            self.logger.warning("CONNECTION ERROR %s" %e)
            self.logger.warning("try again")
            self.create()
        #---------------------------------------------------------------------------------

        # print (res)
        # assert res

    def post(self, now, tag_dict, seriesName, value):
        records = []

        if value != None:
            try:
                floatValue = float(value)
            except:
                floatValue = None
        if floatValue != None:
            #---------------------------------------------------------------------------------
            record = {  "time": now - datetime.timedelta(days=1),
                        "measurement":seriesName,
                        "tags" : tag_dict,
                        "fields" : { "value" : floatValue },
                        }
            records.append(record)
        self.logger.info("writing: %s" % str(records))
        try:
            res= self.client.write_points(records) # , retention_policy=self.retention_policy)
        except requests.exceptions.ConnectionError as e:
            self.logger.warning("CONNECTION ERROR %s" %e)
            self.logger.warning("try again")
            self.create()


    def __destroy__(self):
        self.client.drop_database(Config.INFLUX_DBASE_NAME)
