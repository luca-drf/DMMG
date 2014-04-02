import multiprocessing as mp
from multiprocessing.managers import SyncManager
from dmmgmain import dmmg
import Queue
import settings


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


def start():
    # args --> (delta, query, root)
    manager = client_manager(settings.SERVER, settings.PORT, settings.AUTH)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()

    nprocs = mp.cpu_count() / 2
    worker_manager(job_q, result_q, nprocs)
