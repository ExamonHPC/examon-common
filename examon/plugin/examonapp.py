import os
import sys
import signal
import logging
import collections
from logging.handlers import RotatingFileHandler

from examon.utils.executor import Executor
from examon.utils.config import Config
from examon.utils.daemon import Daemon

from concurrent_log_handler import ConcurrentRotatingFileHandler


class ExamonApp(Executor):
    def __init__(self, executor='Daemon', configfilename=None):
        if configfilename is None:
            self.configfilename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        else:
            self.configfilename = configfilename
        self.cfg = Config(self.configfilename + '.conf')
        self.conf = self.cfg.get_defaults()
        self.pidfile = None
        self.daemon = None
        self.runmode = 'run'
        self.logger = logging.getLogger('examon')
        super(ExamonApp, self).__init__(executor, keepalivesec=self.conf.get('KEEPALIVE_SEC', 60))
        
    def parse_opt(self):
        self.conf = self.cfg.get_conf()
        self.runmode = self.conf['runmode']
        self.pidfile = self.conf['PID_FILENAME']
        self.daemon = Daemon(self.pidfile, signal.SIGINT)
        
    def examon_tags(self):
        return collections.OrderedDict()
        
    def set_logging(self):
        LOGFILE_SIZE_B = int(self.conf['LOGFILE_SIZE_B'])
        LOG_LEVEL = getattr(logging, self.conf['LOG_LEVEL'].upper(), None) 
        handler = ConcurrentRotatingFileHandler(
            self.conf['LOG_FILENAME'], 
            mode='a', 
            maxBytes=LOGFILE_SIZE_B, 
            backupCount=2
        )
        log_formatter = logging.Formatter(
            fmt='%(levelname)s - %(asctime)s - [%(processName)s] - [%(filename)s] - %(name)s - %(message)s', 
            datefmt='%d/%m/%Y %I:%M:%S %p'
        )
        handler.setFormatter(log_formatter)                            
        self.logger.addHandler(handler)
        self.logger.setLevel(LOG_LEVEL)
        # if run print logs also to stdout
        if self.runmode == 'run':
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(log_formatter)
            self.logger.addHandler(handler)

    def run(self):
        self.set_logging()
        if self.runmode == 'stop':                        
            print(" Terminating daemon...")
            self.logger.info("Terminating daemon...")
            self.daemon.stop()
            sys.exit(0)
        elif self.runmode in ['run', 'start', 'restart']:
            if self.runmode == 'start':
                print("Daemonize..")
                self.daemon.start()
            elif self.runmode == 'restart':
                print("Restarting Daemon..")
                self.daemon.restart()
            print("Starting jobs...")
            self.exec_par()
