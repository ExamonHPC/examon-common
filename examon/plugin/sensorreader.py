import os
import sys
import copy
import time
import json
import logging
import collections
import _thread

from threading import Timer
from examon.db.kairosdb import KairosDB
from examon.transport.mqtt import Mqtt


# def timeout_handler():
#     logger = logging.getLogger(__name__)
#     logger.error('Timeout in main loop, exiting..')
#     logger.debug('Process PID: %d' % os.getpid())
#     # sys.exit(1)
#     # thread.interrupt_main()
#     #os._exit(1)
#     raise Exception('Timeout in main loop, exiting..')


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
        self.TS = float(self.conf['TS'])
        self.timeout = float(self.conf.get('TIMEOUT', 10*self.TS))
        self.logger = logging.getLogger(__name__)


    def timeout_handler(self):
        #logger = logging.getLogger(__name__)
        self.logger.error('Timeout in main loop, exiting..')
        self.logger.debug('Process PID: %d' % os.getpid())
        #sys.exit(1)
        # thread.interrupt_main()
        os._exit(1)
        #self.running = False

    def add_tag_v(self, v):
        """Sanitize tag values"""
        if (v is not None) and (v != u'') and (v != 'None'):
            ret = v.replace(' ', '_').replace('/', '_').replace('+', '_').replace('#', '_')
        else:
            ret = '_'
        return ret

    def add_payload_v(self, v):
        """Sanitize payload values"""
        if (v is not None) and (v != u'') and (v != 'None'):
            if isinstance(v, str):
                ret = v.replace(';', '_')
            else:
                ret = v
        else:
            ret = '_'
        return ret
      
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
            self.dest_client = Mqtt(
                self.conf['MQTT_BROKER'],
                self.conf['MQTT_PORT'],
                username=self.conf['MQTT_USER'],
                password=self.conf['MQTT_PASSWORD'],
                format=self.conf['MQTT_FORMAT'],
                outtopic=self.conf['MQTT_TOPIC'],
                dryrun=self.conf['DRY_RUN']
            )
            self.dest_client.run()
        
        while True:
            try:
                self.logger.debug("Start timeout timer")
                timeout_timer = Timer(self.timeout, self.timeout_handler)  # timeout after 3*sampling time
                timeout_timer.start()
                
                t0 = time.time()
                worker_id, payload = self.read_data(self)
                t1 = time.time()
                self.logger.info(
                    "Worker [%s] - Retrieved and processed %d metrics in %f seconds",
                    worker_id, len(payload), (t1-t0)
                )
                
                t0 = time.time()
                self.dest_client.put_metrics(payload, comp=self.comp)
                t1 = time.time()
                
                self.logger.debug(
                    "Worker [%s] - Insert: %d sensors, time: %f sec, insert_rate: %f sens/sec",
                    worker_id,
                    len(payload),
                    (t1-t0),
                    len(payload)/(t1-t0)
                )
            except Exception:
                self.logger.exception('Uncaught exception in main loop!')
                self.logger.debug("Cancel timeout timer")
                timeout_timer.cancel()
                continue
            
            self.logger.debug("Cancel timeout timer")
            timeout_timer.cancel()
            
            self.logger.debug("Start new loop")
            time.sleep(self.TS - (time.time() % self.TS))
