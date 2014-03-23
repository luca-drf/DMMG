import os
import multiprocessing as mp
from multiprocessing.managers import SyncManager
import Queue
import time
from maindmmg import dmmg, filepath_gen


IP = '127.0.0.1'
PORT = 55443
AUTH = '2dccd769eca5696d7daf745b4ffb55afe08c41bc'


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


def client_manager(ip, port, AUTH):
    class ServerQManager(SyncManager):
        pass

    ServerQManager.register('get_job_q')
    ServerQManager.register('get_result_q')

    manager = ServerQManager(address=(ip, port), authkey=AUTH)
    manager.connect()

    print 'Client connected to %s:%s' % (ip, port)
    return manager


def dmmg_worker(job_q, result_q):
    myname = mp.current_process().name
    while True:
        try:
            job = job_q.get_nowait()
            print 'dmmg %s got %s file...' % (myname, job)
            sim = dmmg(job[0], job[1], job[2])
            result_q.put((job[2], sim))
            print '  %s done' % myname
        except Queue.Empty:
            return


def worker_manager(s_job_q, s_result_q, nprocs):
    procs = []
    for i in xrange(nprocs):
        p = mp.Process(target=dmmg_worker, args=(s_job_q, s_result_q))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()


def server(args):
    # args --> (delta, query, root)
    manager = server_manager(PORT, AUTH)
    s_job_q = manager.get_job_q()
    s_result_q = manager.get_result_q()

    job_n = 0
    for filepath in filepath_gen(args[2]):
        s_job_q.put((args[0], args[1], filepath))
        job_n += 1

    print 'File query:', os.path.basename(args[1])
    print '---------------------------------------'
    while True:
        filepath, sim = s_result_q.get()
        job_n -= 1

        print 'File:', os.path.basename(filepath), 'Similarity:', sim
        if not job_n:
            break

    print '--- DONE ---'
    time.sleep(2)
    manager.shutdown()


def client():
    # args --> (delta, query, root)
    manager = client_manager(IP, PORT, AUTH)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()

    nprocs = mp.cpu_count() / 2
    worker_manager(job_q, result_q, nprocs)
