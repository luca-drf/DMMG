import Queue
import time
from multiprocessing.managers import SyncManager
from dmmgmain import filepath_gen
import os
import settings


def server_manager(port, AUTH):
    job_q = Queue.Queue()
    result_q = Queue.Queue()

    class JobQManager(SyncManager):
        pass

    JobQManager.register('get_job_q', callable=lambda: job_q)
    JobQManager.register('get_result_q', callable=lambda: result_q)

    manager = JobQManager(address=('', port), authkey=AUTH)
    manager.start()
    print 'Server started at port %s' % port
    return manager


def start(args):
    tw_start = time.time()
    # args --> (delta, query, root)
    manager = server_manager(settings.PORT, settings.AUTH)
    s_job_q = manager.get_job_q()
    s_result_q = manager.get_result_q()

    job_n = 0
    for filepath in filepath_gen(args[2]):
        s_job_q.put((args[0], args[1], filepath))
        job_n += 1

    print 'File query:', os.path.basename(args[1])
    print '---------------------------------------'
    while True:
        filepath, sim, sem, wos = s_result_q.get()
        job_n -= 1

        print '%s SIM: %.3f SE: %.3f WO: %.3f' % (os.path.basename(filepath),
                                                  sim,
                                                  sem,
                                                  wos)
        if not job_n:
            break

    print '--- DONE ---'
    tw_stop = time.time()
    print 'Computed in %s sec.' % (tw_stop - tw_start)

    time.sleep(2)
    manager.shutdown()
