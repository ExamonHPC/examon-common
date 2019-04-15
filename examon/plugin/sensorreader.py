
import copy
import time
import json
import collections

from examon.db.kairosdb import KairosDB
from examon.transport.mqtt import Mqtt

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
        
        if self.conf['OUT_PROTOCOL'] == 'kairosdb':
            self.dest_client = KairosDB(self.conf['K_SERVERS'], self.conf['K_PORT'], self.conf['K_USER'], self.conf['K_PASSWORD'])
        elif self.conf['OUT_PROTOCOL'] == 'mqtt':
            # TODO: add MQTT format in conf
            self.dest_client = Mqtt(self.conf['MQTT_BROKER'], self.conf['MQTT_PORT'], format='csv', outtopic=self.conf['MQTT_TOPIC'])
            self.dest_client.run()
       
    def add_tags(self, tags):
        self.tags = copy.deepcopy(tags)
        
    def get_tags(self):
        return copy.deepcopy(self.tags)
    
    def run(self):
        if not self.read_data:
            raise Exception("'read_data' must be implemented!")

        TS = float(self.conf['TS'])
        while True:
            #t0 = time.time()
            #if self.read_data:
            worker_id, payload  = self.read_data(self)
            #t1 = time.time()
            #print "Retrieved and processed %d nodes in %f seconds" % (len(res),(t1-t0),)
            #print json.dumps(res)
            #sys.exit(0)
            t0 = time.time()
            self.dest_client.put_metrics(payload, comp=self.comp)
            #print json.dumps(payload[0:3], indent=4)
            t1 = time.time()
            print "Worker %s:...............insert: %d sensors, time: %f sec, insert_rate %f sens/sec" % (worker_id, \
                                                                                                           len(payload),\
                                                                                                           (t1-t0),\
                                                                                                           len(payload)/(t1-t0), )
            time.sleep(TS - (time.time() % TS))