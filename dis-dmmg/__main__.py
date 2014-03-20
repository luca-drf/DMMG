import os
import sys
import multiprocessing
from multiprocessing import Pool
from multiprocessing.managers import SyncManager
import Queue
import time


IP = '127.0.0.1'
PORTNUM = 55444
AUTHKEY = 'shufflin'
DATA_ROOT = '/Users/radome/src/Prove/Python_Multiprocess/data'


def make_server_manager(port, authkey):
    job_q = Queue.Queue()
    result_q = Queue.Queue()

    class JobQueueManager(SyncManager):
        pass

    JobQueueManager.register('get_job_q', callable=lambda: job_q)
    JobQueueManager.register('get_result_q', callable=lambda: result_q)

    manager = JobQueueManager(address=('', port), authkey=authkey)
    manager.start()
    print 'Server started at port %s' % port
    return manager


def make_client_manager(ip, port, authkey):
    class ServerQueueManager(SyncManager):
        pass

    ServerQueueManager.register('get_job_q')
    ServerQueueManager.register('get_result_q')

    manager = ServerQueueManager(address=(ip, port), authkey=authkey)
    manager.connect()

    print 'Client connected to %s:%s' % (ip, port)
    return manager


def multi_hash(value):
    print 'hash', multiprocessing.current_process().name
    return hash(value)


def dmmg(job):
    p = Pool(2)
    result = p.map_async(multi_hash, job)
    return result.get()[0] + result.get()[1]


def dmmg_worker(job_q, result_q):
    myname = multiprocessing.current_process().name
    while True:
        try:
            job = job_q.get_nowait()
            print 'dmmg %s got %s file...' % (myname, job)
            sim = dmmg(job)
            result_q.put((job[1], sim))
            print '  %s done' % myname
        except Queue.Empty:
            return


def mp_dmmg(shared_job_q, shared_result_q, nprocs):
    procs = []
    for i in range(nprocs):
        p = multiprocessing.Process(target=dmmg_worker,
                                    args=(shared_job_q, shared_result_q))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()


def server(query):
    manager = make_server_manager(PORTNUM, AUTHKEY)
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()
    job_n = 0

    for dirpath, dirnames, filenames in os.walk(DATA_ROOT):
        for filename in filenames:
            shared_job_q.put((query, os.path.join(dirpath, filename)))
            job_n += 1

    while True:
        filepath, sim = shared_result_q.get()
        job_n -= 1
        if sim != (hash(filepath) + hash(query)):
            print 'HASH MISMATCH:', filepath, sim
        else:
            print filepath, 'OK'
        if not job_n:
            break

    print '--- DONE ---'
    time.sleep(2)
    manager.shutdown()


def client():
    manager = make_client_manager(IP, PORTNUM, AUTHKEY)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()

    nprocs = multiprocessing.cpu_count() / 2
    mp_dmmg(job_q, result_q, nprocs)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        server(sys.argv[2])
    else:
        client()
