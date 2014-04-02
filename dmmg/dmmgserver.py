import Queue
import time
from multiprocessing.managers import SyncManager
from dmmgmain import filepath_gen
import os
import settings
from sets import Set


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


def file_manager(query_path, test_path):
    queryset = Set([])
    testset = Set([])
    for query_filepath in filepath_gen(query_path):
        queryset.add(query_filepath)
    for test_filepath in filepath_gen(test_path):
        testset.add(test_filepath)
    return queryset, testset


def start(args):
    tw_start = time.time()
    # args --> (delta, query, root)
    manager = server_manager(settings.PORT, settings.AUTH)
    s_job_q = manager.get_job_q()
    s_result_q = manager.get_result_q()

    queryset, testset = file_manager(args[1], args[2])
    job_n = 0
    for query_filepath in queryset:
        try:
            testset.remove(query_filepath)
        except KeyError:
            pass
        for test_filepath in testset:
            s_job_q.put((args[0], query_filepath, test_filepath))
            job_n += 1

    while True:
        query_filepath, test_filepath, sim, sem, wos = s_result_q.get()
        job_n -= 1

        print ('Q: %s\nT: %s\nSIM: %.3f SE: %.3f WO: %.3f\n'
               % (os.path.basename(query_filepath),
                  os.path.basename(test_filepath),
                  sim,
                  sem,
                  wos))
        if not job_n:
            break

    print '--- DONE ---'
    tw_stop = time.time()
    print 'Computed in %s sec.' % (tw_stop - tw_start)

    time.sleep(2)
    manager.shutdown()
