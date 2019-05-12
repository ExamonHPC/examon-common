# -*- coding: utf-8 -*-
"""
 Mqtt.py - MQTT protocol handler

 Copyright (c) 2014, francesco.beneventi@unibo.it
 
"""

import sys
import zlib
import gzip 
import json
import struct
import StringIO
import logging
#sys.path.append('../../lib/mosquitto-1.3.5/lib/python')
#import mosquitto
import paho.mqtt.client as mosquitto



class Mqtt(object):
    """
        MQTT client
    """
    def __init__(self, brokerip, brokerport, format='csv', intopic=None, outtopic=None, qos=0, retain=False):
        self.brokerip = brokerip
        self.brokerport = brokerport
        self.intopic = intopic
        self.outtopic = outtopic
        self.qos = qos
        self.retain = retain
        self.client = mosquitto.Mosquitto()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.logger = logging.getLogger(__name__)
        
        # set msg format: default = 'csv'
        if format == 'csv':
            self.put_metrics = self._put_metrics_csv
        elif format == 'json':
            self.put_metrics = self._put_metrics_json
        elif format == 'bulk':
            self.put_metrics = self._put_metrics_json_bulk
            
            
    def process(self, client, msg):
        """
            Stream processing method. Override
        """
        pass

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):    # paho
    #def on_connect(self, client, userdata, rc):
        """
            On connect callback
        """
        #print("Connected with result code "+str(rc))
        self.logger.info("Connected with result code %s" % (str(rc)))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if self.intopic:
            #print self.intopic
            self.logger.info("Subscribing to: %s" % (self.intopic))
            self.client.subscribe(self.intopic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        """
            On message callback
        """
        self.process(client,msg)
    
    def _compress(self, payload):
        """
            Compress payload. TODO: replace with blosc
        """
        s = StringIO.StringIO()
        with gzip.GzipFile(fileobj=s, mode='w') as g:
            g.write(payload)
        return s.getvalue()
        
    def _put_metrics_csv(self, metrics, comp=False):
        """
            One value per message: csv.
            Topic is a <key>/<value> sequence obtained from metric['tags'] dict
            Payload is a string cat <value>;<timestamp_epoch_seconds>
        """
        for metric in metrics:
            # build value
            payload = str(metric['value']).encode('utf-8')
            # skip if no value
            if payload == '':
                continue
            payload += (";%.3f" % ((metric['timestamp'])/1000))
            payload = str(payload)
            if comp:
                payload = self._compress(payload)  # TODO: find a better way. This manage both strings and floats
            # build topic 
            topic = '/'.join([(val).encode('utf-8') for pair in metric['tags'].items() for val in pair])
            topic += '/' + (metric['name']).encode('utf-8')
            # sanitize
            topic = topic.replace(' ','_').replace('+','_').replace('#','_').replace('.','_')
            topic = (topic).decode('utf-8')
            # publish
            #logger.debug(topic)
            #logger.debug(value)
            #print topic
            #print payload
            self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,str(payload)))
            try:
                #pass
                self.client.publish(topic, payload=payload, qos=self.qos, retain=self.retain)
            except:
                e = sys.exc_info()[0]
                self.logger.error("Exception in MQTT publish", exc_info=True)
                #print "[%s] Exception in MQTT publish: %s" % ('MQTT', e)
                pass
    
    def _put_metrics_json(self, metrics, comp=False):
        """
            One value per message: json.
            Topic is a pre-defined value (outtopic)
            Payload is the json obtained from metric
        """
        for metric in metrics:
            # build topic 
            topic = self.outtopic
            # build value
            if comp:
                payload = self._compress(json.dumps(metric))
            else: 
                payload = json.dumps(metric)
            # publish
            #logger.debug(topic)
            #logger.debug(value)
            self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,json.dumps(metric)))
            try:
                self.client.publish(topic, payload=payload, qos=self.qos, retain=self.retain)
            except:
                e = sys.exc_info()[0]
                self.logger.error("Exception in MQTT publish", exc_info=True)
                #print "[%s] Exception in MQTT publish: %s" % ('MQTT', e)
                pass
    
    def _put_metrics_json_bulk(self, metrics, comp=True):
        """
            Multiple values per message.
            Topic is a pre-defined value (outtopic)
            Payload is the (compressed) list of metrics
        """
        # build topic 
        topic = self.outtopic
        # build value
        if comp:
            payload = self._compress(json.dumps(metrics))
        else: 
            payload = json.dumps(metrics)
        # publish
        #logger.debug(topic)
        #logger.debug(value)
        self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,json.dumps(metrics)))
        try:
            self.client.publish(topic, payload=payload, qos=self.qos, retain=self.retain)
        except:
            e = sys.exc_info()[0]
            self.logger.error("Exception in MQTT publish", exc_info=True)
            #print "[%s] Exception in MQTT publish: %s" % ('MQTT', e)
            pass
            
        
    def run(self):
        """
            Connect and start MQTT FSM
        """
        #print "connecting MQTT..."
        self.logger.info("Connecting to MQTT server: %s:%s" % (self.brokerip,self.brokerport))
        try:
            self.client.connect(self.brokerip, port=self.brokerport)
        except:
            #print "[MQTT]:Error connecting to server"
            self.logger.error("Exception in MQTT connect", exc_info=True)
            sys.exit(1)
        self.logger.info("MQTT started")
        self.client.loop_start() 