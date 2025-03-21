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
    def __init__(self, server, port, user=None, password=None, timeout=60, debug=False):
        self.server = server
        self.port = port
        self.user = user
        self.debug = debug
        self.password = password
        self.s = requests.Session()
        self.s.timeout = timeout
        if self.password:
            self.s.auth = (self.user, self.password)
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
            headers = {'Content-Type': 'application/gzip'}
            payload = self._compress(json.dumps(metrics))
        else:
            payload = json.dumps(metrics)
        try:
            if not self.debug:
                self.logger.debug("Inserting %d metrics" % len(metrics))
                response = self.s.post(self.apis['post_metrics'], payload, headers=headers)
                response.raise_for_status()
            
            # DEBUG: send one metric at time
            else:  # TODO: Make this configurable
                for m in metrics:
                    pay = [m]
                    try:
                        response = self.s.post(self.apis['post_metrics'], json.dumps([m]), headers=headers)
                        response.raise_for_status()
                    except:
                        self.logger.exception("Exception in post()")
                        self.logger.error("Request payload: %s" % (json.dumps(pay, indent=4)))
                        raise                     
        except:
            self.logger.exception("Exception in post()")
            raise
    
    def query_metrics(self, query):
        response = None
        try:
            self.logger.debug("query metrics: %s" % repr(query))
            headers = {'Accept-Encoding': 'gzip, deflate'}
            response = self.s.post(self.apis['post_query'], data=json.dumps(query), headers=headers)
            response.raise_for_status()
            return response.json()
        except:
            self.logger.exception("Exception in post()")
            raise
