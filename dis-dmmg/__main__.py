import os
import sys
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing.managers import SyncManager
import Queue
import time


IP = '127.0.0.1'
PORT = 55443
AUTH = '2dccd769eca5696d7daf745b4ffb55afe08c41bc'
DATA_ROOT = ''


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


def multi_hash(value):
    print 'hash', mp.current_process().name
    return hash(value)


def dmmg(job):
    p = Pool(2)
    result = p.map_async(multi_hash, job)
    return result.get()[0] + result.get()[1]


def dmmg_worker(job_q, result_q):
    myname = mp.current_process().name
    while True:
        try:
            job = job_q.get_nowait()
            print 'dmmg %s got %s file...' % (myname, job)
            sim = dmmg(job)
            result_q.put((job[1], sim))
            print '  %s done' % myname
        except Queue.Empty:
            return


def mp_dmmg(s_job_q, s_result_q, nprocs):
    procs = []
    for i in xrange(nprocs):
        p = mp.Process(target=dmmg_worker, args=(s_job_q, s_result_q))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()


def server(query):
    manager = server_manager(PORT, AUTH)
    s_job_q = manager.get_job_q()
    s_result_q = manager.get_result_q()
    job_n = 0

    for dirpath, dirnames, filenames in os.walk(DATA_ROOT):
        for filename in filenames:
            s_job_q.put((query, os.path.join(dirpath, filename)))
            job_n += 1

    while True:
        filepath, sim = s_result_q.get()
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
    manager = client_manager(IP, PORT, AUTH)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()

    nprocs = mp.cpu_count() / 2
    mp_dmmg(job_q, result_q, nprocs)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        server(sys.argv[2])
    else:
        client()
