
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from multiprocessing import Process

class Executor(object):
    """
        Execute concurrent workers
    """
    def __init__(self, executor='ProcessPool', keepalivesec=60):
        self.executor = executor
        self.workers = []
        self.keepalivesec = keepalivesec
        self.logger = logging.getLogger('examon')
    
    
    def add_worker(self, *args):
        self.workers.append(args)
    
    
    def exec_par(self):
        if self.executor == 'ProcessPool':
            with ProcessPoolExecutor() as pexecutor:
                pfutures = [pexecutor.submit(*worker) for worker in self.workers]
                results = [r.result() for r in as_completed(pfutures)]
            return results
        if self.executor == 'Daemon':
            daemons = []
            for worker in self.workers:
                if len(worker) > 1:
                    d = Process(target=worker[0], args=worker[1:])
                else:
                    d = Process(target=worker[0])
                daemons.append({'d': d, 'worker': worker})
                d.daemon = True
                d.start()
            try:
                '''
                Auto-restart on failure.
                    Check every keepalivesec seconds if the worker is alive, otherwise 
                    we recreate it.
                '''
                n_worker = len(self.workers)
                if self.keepalivesec > 0:
                    while 1:
                        alive_workers = 0
                        time.sleep(self.keepalivesec)
                        for d in daemons:
                            if d['d'].is_alive() == False:
                                self.logger.warning("Process [%s], died. Try to restart..." % (d['d'].name))
                                if len(d['worker']) > 1:
                                    d_ = Process(target=d['worker'][0], args=d['worker'][1:])
                                else:
                                    d_ = Process(target=d['worker'][0])
                                d['d'] = d_
                                d_.daemon = True
                                d_.start()
                                time.sleep(1)
                                if d_.is_alive() == True:
                                    alive_workers +=1
                            else:
                                alive_workers +=1
                        self.logger.info("%d/%d workers alive" % (alive_workers, n_worker))

                for d in daemons:
                    d['d'].join()
                print "Workers job finished!"
                sys.exit(0) 
            except KeyboardInterrupt:
                print "Interrupted.."