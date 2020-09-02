'''
Created on Apr 5, 2019

@author: riaps
'''

import sys
import os.path
import subprocess
import traceback
import time
import datetime
import signal
import yaml
import fncs
import re
from collections import namedtuple
from threading import RLock
import json
# import logging
 
from gla.server import ServiceThread
from gla.config import Config
from gla.dbase import Database
        
# namedtuple 
Subscribe = namedtuple("Subscriber", "client obj attr unit")
Publish   = namedtuple("Publish", "client obj attr value unit topic")
LogSpec   = namedtuple("LogSpec", "obj attr unit")

class Agent():
    TIME_FORMAT = "%Y-%m-%d %Y %H:%M:%S"
    def __init__(self,baseName):
        self.base = baseName
        self.model = baseName + '.glm'
        self.logs  = baseName + '.gll'
        self.fncs  = baseName + '.yaml'
        self.cfile = 'gla.yaml'
        
        assert os.path.isfile(self.model)
        assert os.path.isfile(self.logs)
        assert os.path.isfile(self.fncs)
        assert os.path.isfile(self.cfile)
        
        signal.signal(signal.SIGTERM,self.terminate)
        signal.signal(signal.SIGINT,self.terminate)
        
        try:
            Config.setup()
            with open(self.cfile,'r') as f:
                    self.conf = yaml.load(f,Loader=yaml.Loader)
        except:
                raise
            
        if self.conf.time_base == "now":
            self.time = datetime.datetime.utcnow()
        else:
            self.time =  datetime.datetime.strptime(self.conf.time_base,"%Y-%m-%d")
            
        self.logSpec = {}
        try:
            with open(self.logs,'r') as f:
                content = json.load(f)
                for item in content:
                    (obj,attr,unit) = item
                    key = '%s.%s' % (obj,attr)
                    drop =  re.compile(r' %s'% unit)
                    self.logSpec[key] = LogSpec(obj=obj,attr=attr,unit=drop)
        except:
            raise
        
        self.subs = {}  # obj.attr -> Subscribe
        self.pubs = []  # [Publish]*
        self.results = {}
        self.clients = {} 
        self.clientSubs = {} 
        self.lock = RLock()
#         logging.basicConfig(filename='agent.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO) 

    def launch(self,cmd,logfile,env):
        context = os.environ.copy()
        context.update(env)
        with open(logfile,"ab") if logfile else None as log:
            try:
                process = subprocess.Popen(cmd,env=context,stdout=log,stderr=subprocess.STDOUT)
            except:
                traceback.print_exc()
                print('launch error: %s' % sys.exc_info()[0])
                process = None
        return process
    
    def start(self):
        self.service = ServiceThread(self,self.conf.host,self.conf.port)
        self.service.start() 
        self.broker = self.launch(['fncs_broker',"2"],'broker.log',{"FNCS_TRACE" : "yes", "FNCS_LOG_STDOUT" : "yes"})
        self.engine = self.launch(['gridlabd',self.model],'gridlabd.log',{"FNCS_FATAL": "YES", "FNCS_LOG_STDOUT" : "yes"})
        os.environ['FNCS_CONFIG_FILE'] = self.fncs
        self.dbase = Database(self.conf,self.logSpec)
        
    def run(self):
        time_granted = 0
        fncs.initialize()
        time_stop = self.conf.time_stop
        time_pace = self.conf.time_pace
        while time_granted < time_stop:
            time1 = time.perf_counter()
            time_prev = time_granted
            time_granted = fncs.time_request(time_stop)
            time_advance = datetime.timedelta(seconds=(time_granted - time_prev))
            self.time = self.time + time_advance
            events = fncs.get_events()
            for topic in events:
                value = fncs.get_value(topic)
                print((time_granted, topic, value))
                key = topic
                resp = value
#                 key = topic.decode('utf-8')
#                 resp = value.decode('utf-8')
                result = None
                drop = None
                with self.lock:
                    if key in self.logSpec:
                        drop = self.logSpec[key].unit
                    elif key in self.subs:
                        drop = self.subs[key][0].unit
                    else:
                        pass
                    resp = drop.sub('',resp) if drop != None else resp
                    try: 
                        result = float(resp)
                    except:
                        try: 
                            result = complex(resp)
                        except: 
                            try: 
                                result = str(resp)
                            except: pass
                    # store results from the current simulation time step
                    obj, attr = key.split('.')
                    self.results[key]= (obj,attr,result,time_granted)
                    if key in self.subs:
                        for sub in self.subs[key]:
                            sub.client.sendClient(sub.obj,sub.attr,result,time_granted)
                if key in self.logSpec:
                    self.dbase.log(self.time,self.logSpec[key],resp)
            with self.lock:
                for pub in self.pubs:
#                     topic = pub.topic.encode('utf-8')
#                     value = pub.value.encode('utf-8')
                    topic = pub.topic
                    value = pub.value
                    print((time_granted,topic,value))
                    fncs.publish(topic, value)
                    if pub.topic in self.logSpec:
                        self.dbase.log(self.time,self.logSpec[pub.topic],pub.value)
                self.pubs = []
            self.dbase.flush()
            time2 = time.perf_counter()
            delta = time2-time1
            sleep = time_pace-delta
            if sleep > 0:
                time.sleep(sleep)

    def terminate(self,_ign1,_ign2):
        self.stop()
                        
    def stop(self):
        try: self.service.stop()
        except: pass
        try: fncs.finalize()
        except: pass
        try: self.broker.kill()
        except: pass
        try: self.engine.kill()
        except: pass
        
    def subscribe(self,client,sub):
        obj,attr,unit = sub
        key = '%s.%s' % (obj,attr)
        drop =  re.compile(r' %s'% unit)
        with self.lock:
            if key not in self.subs: self.subs[key] = []
            self.subs[key] += [Subscribe(client=client,obj=obj,attr=attr,unit=drop)]
            clientHash = hash(client)
            if clientHash not in self.clientSubs:
                self.clientSubs[clientHash] = set()
            self.clientSubs[clientHash].add(key)
            
    def query(self,client,query):
        obj,attr,unit = query
        key = '%s.%s' % (obj,attr)
        if key in self.results:
            return ('ans',self.results[key][0], self.results[key][1], self.results[key][2], self.results[key][3])
    
    def publish(self,client,pub):
        obj,attr,value,unit = pub
        topic = '%s.%s' % (obj,attr)
        with self.lock:
            self.pubs += [Publish(client=client,obj=obj,attr=attr,value=value,unit=unit,topic=topic)]
        
    def unsubscribe(self,client,sub=None):
        if sub != None:
            obj,attr,_unit = sub
            key = '%s.%s' % (obj,attr)
            with self.lock:
                assert key in self.subs
                self.subs[key] = filter(lambda sub: sub.client == client, self.subs[key])
        else:
            clientHash = hash(client)
            with self.lock:
                if clientHash in self.clientSubs:
                    for subKey in self.clientSubs[clientHash]:
                        self.subs[subKey] = list(filter(lambda sub: sub.client != client, self.subs[subKey]))
                    del self.clientSubs[clientHash]
                
    def isClient(self,name):
        return name in self.clients
    
    def addClient(self,name,client):
        with self.lock:
            self.clients[name] = client
    
    def delClient(self,name):
        with self.lock:
            del self.clients[name]
