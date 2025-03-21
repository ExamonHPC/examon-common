import sys
import time
import copy
import logging
import psutil


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
        self.workers.append(copy.deepcopy(args))
    
    
    def exec_par(self):
        if self.executor == 'ProcessPool':
            with ProcessPoolExecutor() as pexecutor:
                pfutures = [pexecutor.submit(*worker) for worker in self.workers]
                results = [r.result() for r in as_completed(pfutures)]
            return results
        if self.executor == 'Daemon':
            daemons = []
            process_children = {}  # Store process children mapping
            
            def kill_proc_tree(pid):
                """Kill a process and all its children recursively"""
                # Use stored children if available
                children_to_kill = process_children.get(pid, [])
                
                # Try to get current children if process is still alive
                try:
                    parent = psutil.Process(pid)
                    current_children = parent.children(recursive=True)
                    children_to_kill.extend(current_children)
                    
                    # Kill all children
                    for child in children_to_kill:
                        try:
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Kill parent
                    try:
                        parent.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process already dead, just kill stored children
                    for child in children_to_kill:
                        try:
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                # Clean up stored children
                if pid in process_children:
                    del process_children[pid]
            
            def monitor_process_children():
                """Update the process_children dictionary with current children"""
                for d in daemons:
                    if d['d'].is_alive() and hasattr(d['d'], 'pid'):
                        try:
                            parent = psutil.Process(d['d'].pid)
                            children = parent.children(recursive=True)
                            process_children[d['d'].pid] = children
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            
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
                        # Update process children mapping
                        monitor_process_children()
                        time.sleep(self.keepalivesec)
                        for d in daemons:
                            if d['d'].is_alive() == False:
                                self.logger.warning("Process [%s], died. Try to restart..." % (d['d'].name))
                                # Kill any remaining child processes
                                if hasattr(d['d'], 'pid'):
                                    kill_proc_tree(d['d'].pid)
                                
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
                print("Workers job finished!")
                sys.exit(0) 
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received, terminating all processes...")
                for d in daemons:
                    if d['d'].is_alive() and hasattr(d['d'], 'pid'):
                        kill_proc_tree(d['d'].pid)
                print("Interrupted, all processes terminated.")
                sys.exit(0)