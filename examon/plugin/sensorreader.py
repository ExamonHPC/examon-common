import os
import sys
import copy
import time
import json
import logging
import collections
import thread 

from threading import Timer
from examon.db.kairosdb import KairosDB
from examon.transport.mqtt import Mqtt


def timeout_handler():
    logger = logging.getLogger(__name__)
    logger.error('Timeout in main loop, exiting..')
    logger.debug('Process PID: %d' % os.getpid())
    #sys.exit(1)
    #thread.interrupt_main()
    os._exit(1)

class SensorReader:
    """
        Examon Sensor adapter
    """
    def __init__(self, conf, sensor):
        self.conf = copy.deepcopy(conf)
        self.sensor = sensor
        self.tags = collections.OrderedDict()
        self.read_data = None
        self.dest_client = None
        self.comp = self.conf['COMPRESS']
        self.logger = logging.getLogger(__name__)
        
        # if self.conf['OUT_PROTOCOL'] == 'kairosdb':
            # self.dest_client = KairosDB(self.conf['K_SERVERS'], self.conf['K_PORT'], self.conf['K_USER'], self.conf['K_PASSWORD'])
        # elif self.conf['OUT_PROTOCOL'] == 'mqtt':
            # # TODO: add MQTT format in conf
            # self.dest_client = Mqtt(self.conf['MQTT_BROKER'], self.conf['MQTT_PORT'], format=self.conf['MQTT_FORMAT'], outtopic=self.conf['MQTT_TOPIC'])
            # self.dest_client.run()
       
    def add_tags(self, tags):
        self.tags = copy.deepcopy(tags)
        
    def get_tags(self):
        return copy.deepcopy(self.tags)
    
    def run(self):
        if not self.read_data:
            raise Exception("'read_data' must be implemented!")
            
        if self.conf['OUT_PROTOCOL'] == 'kairosdb':
            self.dest_client = KairosDB(self.conf['K_SERVERS'], self.conf['K_PORT'], self.conf['K_USER'], self.conf['K_PASSWORD'])
        elif self.conf['OUT_PROTOCOL'] == 'mqtt':
            # TODO: add MQTT format in conf
            self.dest_client = Mqtt(self.conf['MQTT_BROKER'], self.conf['MQTT_PORT'], username=self.conf['MQTT_USER'], password=self.conf['MQTT_PASSWORD'], format=self.conf['MQTT_FORMAT'], outtopic=self.conf['MQTT_TOPIC'], dryrun=self.conf['DRY_RUN'])
            self.dest_client.run()
        
        TS = float(self.conf['TS'])
        
        while True:
            try:
                self.logger.debug("Start timeout timer")
                timeout_timer = Timer(10*TS, timeout_handler)  #timeout after 3*sampling time
                timeout_timer.start()
                
                t0 = time.time()
                #if self.read_data:
                worker_id, payload = self.read_data(self)
                t1 = time.time()
                #print "Retrieved and processed %d nodes in %f seconds" % (len(res),(t1-t0),)
                self.logger.info("Worker [%s] - Retrieved and processed %d metrics in %f seconds" % (worker_id, len(payload),(t1-t0),))
                #print json.dumps(res)
                #sys.exit(0)
                t0 = time.time()
                self.dest_client.put_metrics(payload, comp=self.comp)
                t1 = time.time()
                #print json.dumps(payload[0:3], indent=4)
                # print "Worker %s:...............insert: %d sensors, time: %f sec, insert_rate %f sens/sec" % (worker_id, \
                                                                                                               # len(payload),\
                                                                                                               # (t1-t0),\
                                                                                                               # len(payload)/(t1-t0), )
                self.logger.debug("Worker [%s] - Insert: %d sensors, time: %f sec, insert_rate: %f sens/sec" % (worker_id, \
                                                                                                               len(payload),\
                                                                                                           (t1-t0),\
                                                                                                           len(payload)/(t1-t0), ))
            except Exception:
                self.logger.exception('Uncaught exception in main loop!')
                self.logger.debug("Cancel timeout timer")
                timeout_timer.cancel()
                continue
            
            self.logger.debug("Cancel timeout timer")
            timeout_timer.cancel()
            
            self.logger.debug("Start new loop")
            time.sleep(TS - (time.time() % TS))
