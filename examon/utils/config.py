
import argparse
import ConfigParser


class Config:
    def __init__(self, configfile):
        self.configfile = configfile
        self.defaults = {}
        self.parser = argparse.ArgumentParser()
        # default args
        self.parser.add_argument('runmode', choices=['run','start','restart','stop'], help='Run mode')
        self.parser.add_argument('-b', dest='MQTT_BROKER', help='IP address of the MQTT broker')
        self.parser.add_argument('-p', dest='MQTT_PORT', help='Port of the MQTT broker')
        self.parser.add_argument('-t', dest='MQTT_TOPIC', help='MQTT topic')
        self.parser.add_argument('-s', dest='TS', help='Sampling time (seconds)')
        self.parser.add_argument('-x', dest='PID_FILENAME', help='pid filename')
        self.parser.add_argument('-l', dest='LOG_FILENAME', help='log filename')
        self.parser.add_argument('-d', dest='OUT_PROTOCOL', choices=['mqtt','kairosdb'], default='mqtt', help='select where to send data (default: mqtt)')
        self.parser.add_argument('-f', dest='MQTT_FORMAT', choices=['csv','json','bulk'], default='csv', help='MQTT payload format (default: csv)')
        self.parser.add_argument('--compress', dest='COMPRESS', action='store_true', default=False, help='enable payload compression (default: False)')
        #self.parser.add_argument('--version', action='version', version=version)
        self.parser.add_argument('--kairosdb-server', dest='K_SERVERS', help='kairosdb servers')
        self.parser.add_argument('--kairosdb-port', dest='K_PORT', help='kairosdb port')
        self.parser.add_argument('--kairosdb-user', dest='K_USER', help='kairosdb username')
        self.parser.add_argument('--kairosdb-password', dest='K_PASSWORD', help='kairosdb password')
        self.parser.add_argument('--logfile-size', dest='LOGFILE_SIZE_B', default=5*1024*1024, help='log file size (max) in bytes')
        self.parser.add_argument('--loglevel', dest='LOG_LEVEL', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO', help='log level')
    
    def get_defaults(self):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str  #preserve caps
        config.read(self.configfile) 
        for section in config.sections():
            self.defaults.update(dict(config.items(section)))
        return self.defaults
    
    def update_optparser(self, parser):
        self.parser = parser
    
    def get_conf(self):
        args = vars(self.parser.parse_args())
        conf = self.get_defaults()
        conf.update({k: v for k, v in args.items() if v is not None})
        return conf