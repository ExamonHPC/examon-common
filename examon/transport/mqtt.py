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
import io
import logging
import paho.mqtt.client as mosquitto



class Mqtt(object):
    """
        MQTT client
    """
    def __init__(self, brokerip, brokerport, username=None, password=None, format='csv', intopic=None, outtopic=None, qos=0, retain=False, dryrun=False):
        self.brokerip = brokerip
        self.brokerport = brokerport
        self.intopic = intopic
        self.outtopic = outtopic
        self.qos = qos
        self.retain = retain
        self.dryrun = dryrun
        self.client = mosquitto.Mosquitto()
        if username:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.status = 1 # ok
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

    def on_log(self, client, userdata, level, buff):
        self.logger.debug('MQTT logs: %s' % (buff)) 
    
    def on_connect(self, client, userdata, flags, rc):    # paho
    #def on_connect(self, client, userdata, rc):
        """
            On connect callback
        """
        if int(rc) != 0:
            self.logger.error('Error in connect. Result code: %s' % (str(rc)))
            self.logger.info('Closing the MQTT connection')
            self.client.disconnect()
            self.status = 0  # error
        else:
            self.logger.info("Connected with result code %s" % (str(rc)))
        if self.intopic:
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
        s = io.StringIO()
        with gzip.GzipFile(fileobj=s, mode='w') as g:
            g.write(payload)
        return s.getvalue()
        
    def _put_metrics_csv(self, metrics, comp=False):
        """
            One value per message: csv.
            Topic is a <key>/<value> sequence obtained from metric['tags'] dict
            Payload is a string cat <value>;<timestamp_epoch_seconds>
        """
        if not self.status:
            self.logger.error('Bad client status. Exit.')
            sys.exit(1)
        
        for metric in metrics:
            # build value
            payload = str(metric['value'])
            # skip if no value
            if payload == '':
                continue
            payload += (';%.3f' % ((metric['timestamp'])/1000))
            payload = str(payload)
            if comp:
                payload = self._compress(payload)  # TODO: find a better way. This manage both strings and floats
            # build topic 
            topic = '/'.join([(val).replace('/','_') for pair in list(metric['tags'].items()) for val in pair])
            topic += '/' + (metric['name'])
            # sanitize
            topic = topic.replace(' ','_').replace('+','_').replace('#','_')
            topic = (topic)
            # publish
            self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,str(payload)))
            self._publish(topic, payload)

    
    def _put_metrics_json(self, metrics, comp=False):
        """
            One value per message: json.
            Topic is a pre-defined value (outtopic)
            Payload is the json obtained from metric
        """
        if not self.status:
            self.logger.error('Bad client status. Exit.')
            sys.exit(1)
            
        for metric in metrics:
            # build topic 
            topic = self.outtopic
            # build value
            if comp:
                payload = self._compress(json.dumps(metric))
            else: 
                payload = json.dumps(metric)
            # publish
            self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,json.dumps(metric)))
            self._publish(topic, payload)

    
    def _put_metrics_json_bulk(self, metrics, comp=True):
        """
            Multiple values per message.
            Topic is a pre-defined value (outtopic)
            Payload is the (compressed) list of metrics
        """
        if not self.status:
            self.logger.error('Bad client status. Exit.')
            sys.exit(1)
            
        # build topic 
        topic = self.outtopic
        # build value
        if comp:
            payload = self._compress(json.dumps(metrics))
        else: 
            payload = json.dumps(metrics)
        # publish
        self.logger.debug('[MqttPub] Topic: %s - Payload: %s' % (topic,json.dumps(metrics)))
        self._publish(topic, payload)

    def _publish(self, topic, payload):
        if not self.dryrun:
            try:
                self.client.publish(topic, payload=payload, qos=self.qos, retain=self.retain)
            except:
                self.logger.exception('Exception in MQTT publish. Exit.')
                sys.exit(1)
        
    def run(self):
        """
            Connect and start MQTT FSM
        """
        rc = -1
        self.logger.info('Connecting to MQTT server: %s:%s' % (self.brokerip,self.brokerport))
        try:
            rc = self.client.connect(self.brokerip, port=int(self.brokerport))
            self.logger.debug('Connect rc: %d' % (rc))
            if rc != 0:
                raise
        except:
            self.logger.exception('Exception in MQTT connect, rc: %d' % (rc))
            sys.exit(1)
        self.logger.info('MQTT started')
        self.client.loop_start() 
