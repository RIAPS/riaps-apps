"""MQTT Device Component.

RIAPS Project

Copyright 2018, Vanderbilt University

Author: Peter Volgyesi <peter.volgyesi@vanderbilt.edu> 
"""
from riaps.run.comp import Component
import os
import logging
import json
import threading

import paho.mqtt.client as mqtt

class MQTT(Component):
    def __init__(self, host, port, qos, topic):
        super(MQTT, self).__init__()	        
        self.client_id = "%s-%s" % (self.getAppName(), str(self.getLocalID()))
        self.host = host
        self.port = port
        self.qos = qos
        self.topic = topic
        self.client = None
        self.logger.info("Init: clientId=%s, host=%s, port=%d, qos=%d, topic=%s", 
                         self.client_id, self.host, self.port, self.qos, self.topic)
        
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback handler.
    
        Runs in separate thread (see: loop_start()"""
        self.logger.info("Subscribe to %s", self.topic)
        client.subscribe(self.topic)
            
    def on_message(self, client, userdata, msg):
        """MQTT message callback handler.
    
        Runs in separate thread (see: loop_start()"""
        if self._incoming_plug is None:
            mqtt_thread = threading.current_thread()
            self.logger.info("Creating inside plug in thread %s", mqtt_thread.getName())
            self._incoming_plug = self._incoming.setupPlug(mqtt_thread)
        self._incoming_plug.send_pyobj(msg.payload)


    def start(self):
        """Start the device component, connect to broker and subscribe"""
        assert self.client is None
        
        self.logger.info("Start")
        
        self.logger.info("Activating inside port in thread %s", threading.current_thread().getName())
        self._incoming.activate()
        self._incoming_plug = None
        
        self.client = mqtt.Client(client_id=self.client_id, 
                             clean_session=True, 
                             userdata=None, 
                             protocol=mqtt.MQTTv311, 
                             transport="tcp")
     
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
      
        self.logger.info("Connecting to broker: %s:%d", self.host, self.port)
        self.client.connect_async(host=self.host,
                                    port=self.port,
                                    keepalive=60)

        self.logger.info("Starting client loop")
    
        self.client.loop_start()
            
         
    def on_clock(self):
        """Delayed initialization / start"""
        now = self.clock.recv_pyobj()
        self.clock.halt()
        self.logger.info("On clock (delayed start)")
        
        if self.client is None:
            self.start()
        
            
    def on_outgoing(self):
        msg = self.outgoing.recv_pyobj()
        if self.client is None:
            self.start()
        payload = json.dumps(msg).encode("utf-8")
        self.logger.info("Publish %s", payload)
        self.client.publish(topic=self.topic, payload=payload)
        
    def on__incoming(self):
        payload = self._incoming.recv_pyobj()
        self.logger.info("Subscribe %s", payload)
        msg = json.loads(payload.decode("utf-8"))
        self.incoming.send_pyobj(msg)
    
    def __destroy__(self):			
        self.logger.info("Destroy")
        self.logger.info("Stopping client loop")
        self.client.loop_stop(force=True)   	        	        
