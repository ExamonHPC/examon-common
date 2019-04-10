
import zlib
import gzip 
import requests
import StringIO


class KairosDB:
    """
        KairosDB REST client
    """
    def __init__(self, server, port, user=None, password=None):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
    
    
    def _compress(self, payload):
        s = StringIO.StringIO()
        with gzip.GzipFile(fileobj=s, mode='w') as g:
            #g.write(json.dumps([x for x in http_payload_gen()]))
            g.write(json.dumps(payload))
        return s.getvalue()
    
    
    def put_metrics(self, metrics, comp=True):
        api = "http://" + self.server + ":" + self.port + "/api/v1/datapoints"
        headers = {}
        if comp:
            headers = {'content-type': 'application/gzip'}
            payload = self._compress(metrics)
        else:
            payload = metrics
        try:
            if self.user is not None:
                response = requests.post(api, payload, headers=headers, auth=(self.user, self.password))
            else:
                response = requests.post(api, payload, headers=headers)
        except:
            e = sys.exc_info()[0]
            #logger.error("[%s] Exception in post(): %s", "KairosDB", e)
            print "[%s] Exception in post(): %s" % ("KairosDB", e,)
            pass