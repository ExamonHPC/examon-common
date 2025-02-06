import sys
import zlib
import gzip 
import json
import requests
import io
import logging

           
class KairosDB:
    """
        KairosDB REST client
    """
    def __init__(self, server, port, user=None, password=None):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.s = requests.Session()
        if self.password:
            self.s.auth = (self.user, self.password)
        #self.s.headers.update({'x-test': 'true'})
        self.logger = logging.getLogger(__name__)
        self.apis = {}
        self.api_server = "http://" + self.server + ":" + self.port
        self.apis['post_metrics'] = self.api_server + "/api/v1/datapoints"
        self.apis['post_query'] = self.api_server + "/api/v1/datapoints/query"
    
    def _compress(self, payload):
        """Compress payload using gzip for HTTP transport"""
        # Convert string payload to bytes before compression
        payload_bytes = payload.encode('utf-8')
        # Compress the bytes
        return gzip.compress(payload_bytes)
    
    def put_metrics(self, metrics, comp=True):
        headers = {}
        response = None
        if comp:
            headers = {'content-type': 'application/gzip'}
            payload = self._compress(json.dumps(metrics))
        else:
            payload = json.dumps(metrics)
        try:
            self.logger.debug("Inserting %d metrics" % len(metrics))
            response = self.s.post(self.apis['post_metrics'], payload, headers=headers)
            response.raise_for_status()
            
            # # DEBUG: send one metric at time
            # for m in metrics:
                # pay = [m]
                # try:
                    # response = self.s.post(self.apis['post_metrics'], json.dumps([m]), headers=headers)
                    # response.raise_for_status()
                # except:
                    # self.logger.error("Exception in post()", exc_info=True)
                    # self.logger.error("Request payload: %s" % (json.dumps(pay, indent=4)))
                    # self.logger.error("Reason %s" % (response.text))
                    
        except:
            #e = sys.exc_info()[0]
            #logger.error("[%s] Exception in post(): %s", "KairosDB", e)
            #self.logger.error("Exception in post()", exc_info=True)
            self.logger.exception("Exception in post()")
            #if response:
            #    self.logger.error("Reason %s" % (response.text))
            #self.logger.error("Request payload: %s" % (json.dumps(pay, indent=4)))
            #print "[%s] Exception in post(): %s" % ("KairosDB", e,)
            #print "[%s] Reason: " % ("KairosDB",)
            #print response.text
            #pass 
    
    def query_metrics(self, query):
        self.logger.debug("query metrics: %s" % repr(query))
        headers = {'Accept-Encoding': 'gzip, deflate'}
        response = self.s.post(self.apis['post_query'], data=json.dumps(query), headers=headers)
        return response.json()