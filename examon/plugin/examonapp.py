
import os
import sys
import signal
import collections
from examon.utils.executor import Executor
from examon.utils.config import Config
from examon.utils.daemon import Daemon


class ExamonApp(Executor):
    def __init__(self, executor='Daemon', configfilename=None):
        if configfilename == None:
            self.configfilename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        else:
            self.configfilename = configfilename
        self.cfg = Config(self.configfilename + '.conf')
        self.conf = self.cfg.get_defaults()
        self.pidfile = None
        self.daemon = None
        self.runmode = 'run'
        super(ExamonApp, self).__init__(executor)
        
    def parse_opt(self):
        self.conf = self.cfg.get_conf()
        self.runmode = self.conf['runmode']
        self.pidfile = self.conf['PID_FILENAME']
        self.daemon = Daemon(self.pidfile, signal.SIGINT)
        
    def examon_tags(self):
        return collections.OrderedDict()

    def run(self):
        if ('stop' == self.runmode):                        
            print "Terminating daemon..."
            self.daemon.stop()
            sys.exit(0)
        elif self.runmode in ['run','start','restart']:
            if self.runmode == 'start':
                print "Daemonize.."
                self.daemon.start()
            elif self.runmode == 'restart':
                print "Restarting Daemon.."
                self.daemon.restart()
            else:
                pass
            print "Starting jobs..."
            self.exec_par()