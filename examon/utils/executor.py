
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from multiprocessing import Process

class Executor(object):
    """
        Execute concurrent workers
    """
    def __init__(self, executor='ProcessPool'):
        self.executor = executor
        self.workers = []
    
    
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
                daemons.append(d)
                d.daemon = True
                d.start()
            try:
                for d in daemons:
                    d.join()
                print "Workers job finished!"
                sys.exit(0) 
            except KeyboardInterrupt:
                print "Interrupted.."