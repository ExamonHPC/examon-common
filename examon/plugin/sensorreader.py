
import copy
import time
import json
import collections

from examon.utils.kairosdb import KairosDB

class SensorReader:
    """
        Examon Sensor adapter
    """
    def __init__(self, conf, sensor):
        self.conf = copy.deepcopy(conf)
        self.sensor = sensor
        self.tags = collections.OrderedDict()
        self.read_data = None

    def add_tags(self, tags):
        self.tags = copy.deepcopy(tags)
        
    def get_tags(self):
        return copy.deepcopy(self.tags)
    
    def run(self):
        kd = KairosDB(self.conf['K_SERVERS'], self.conf['K_PORT'], self.conf['K_USER'], self.conf['K_PASSWORD'])
        TS = float(self.conf['TS'])
        while True:
            #t0 = time.time()
            if self.read_data:
                res, headers, payload  = self.read_data(self)
            #t1 = time.time()
            #print "Retrieved and processed %d nodes in %f seconds" % (len(res),(t1-t0),)
            #print json.dumps(res)
            #sys.exit(0)
            t0 = time.time()
            kd.put_metrics(payload)
            #print json.dumps(payload[0:3], indent=4)
            t1 = time.time()
            print "Server %s:...............insert: %d sensors, time: %f sec, insert_rate %f sens/sec" % (self.sensor.server, \
                                                                                                           len(payload),\
                                                                                                           (t1-t0),\
                                                                                                           len(payload)/(t1-t0), )
            time.sleep(TS - (time.time() % TS))