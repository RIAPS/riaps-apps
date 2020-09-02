'''
Created on Oct 29, 2018

@author: riaps
'''

import yaml

class Config(yaml.YAMLObject):
    '''
    gla configuration object
    '''
    yaml_tag = u'!GLAConfig'
    def __init__(self,
                 host='',port=0,
                 time_stop=21600, time_pace=1,time_base="2000-01-01",
                 dbhost='localhost', dbport=8086, dbuser='riapsdev', dbpassword='riaps', dbname='gridlabd', dbdrop=True):
        self.host = host
        self.port = port
        self.time_stop = time_stop
        self.time_pace = time_pace
        self.time_base = time_base
        self.dbhost = dbhost
        self.dbport = dbport
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbname = dbname
        self.dbdrop = dbdrop
        
    def __repr__(self):
        return "%s(host=%r,port=%r,time_stop=%r,time_pace=%r,dbhost=%r,dbport=%r,dbuser=%r,dbpassword=%r,dbname=%r,dbdrop=%r)" % \
            (self.__class__.__name__,
             self.host,self.port, 
             self.time_stop,self.time_pace,
             self.dbhost,self.dbport,self.dbuser,self.dbpassword,self.dbname,self.dbdrop
             )
    
    @classmethod
    def setup(cls):
        def constructor(loader, node) :
            fields = loader.construct_mapping(node)
            return Config(**fields)
        yaml.add_constructor('!GLAConfig', constructor)
        

