import time
from sys import stderr
import multiprocessing as mp
from multiprocessing.managers import SyncManager
from dmmgmain import filepath_gen, Storage, retrieve_model_file
import os
from sets import Set
from clustering import FileIndexer, initialize_clusters, InstructionsIndex
from mzparse import compute_snippet_elements
import settings


def server_manager(port, AUTH):
    job_q = mp.JoinableQueue()
    result_q = mp.Queue()
    jobs_e = mp.Event()

    class JobManager(SyncManager):
        pass

    JobManager.register('get_job_q', callable=lambda: job_q)
    JobManager.register('get_result_q', callable=lambda: result_q)
    JobManager.register('get_jobs_e', callable=lambda: jobs_e)

    manager = JobManager(address=('', port), authkey=AUTH)
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


def send_similarity_tasks(delta, queryset, testset, s_job_q):
    job_n = 0
    for query_filepath in queryset:
        try:
            testset.remove(query_filepath)
        except KeyError:
            pass
        for test_filepath in testset:
            s_job_q.put(('s', (delta, query_filepath, test_filepath)))
            job_n += 1
    return job_n


def retrieve_similarity_results(job_n, s_result_q):
    similarities = Storage(settings.SIM_FILE)
    while True:
        query_filepath, test_filepath, sim, sem, wos = s_result_q.get()
        similarities.store((sim, test_filepath))
        job_n -= 1

        print ('Q: %s\nT: %s\nSIM: %.3f SE: %.3f WO: %.3f\n'
               % (os.path.basename(query_filepath),
                  os.path.basename(test_filepath),
                  sim,
                  sem,
                  wos))
        if not job_n:
            break
    return similarities


def send_clustering_tasks(similarities, s_job_q):
    file_dicts = []
    for e in similarities.elements:
        file_dicts.append(FileIndexer(retrieve_model_file(e[1])))

    # for d in file_dicts:
    #     for word in d.index:
    #         print '%s (%d):\n%s\n' % (word,
    #                                   len(d.index[word]),
    #                                   d.index[word])

    # Prepare the initial set of clusters
    file_clusters = initialize_clusters(file_dicts)
    job_n = 0
    for keyword in file_clusters:
        # print 'sending:', keyword
        # print file_clusters[keyword]
        s_job_q.put(('c', keyword, file_clusters[keyword]))
        job_n += 1
    return job_n


def retrieve_clustering_results(job_n, s_result_q):
    clusters = InstructionsIndex()
    while True:
        keyword, clusterized = s_result_q.get()
        clusters[keyword] = clusterized
        job_n -= 1

        if not job_n:
            break
    return clusters


def extract_snippets(clusters):
    snippet_dict = {}
    for key in clusters:
        for cluster in clusters[key]:
            if len(cluster) == 1:
                # snippet_elems = cluster[0]
                snippet_elems = []
            else:
                snippet_elems = compute_snippet_elements(cluster[-1],
                                                         cluster[-2])
            snippet_dict.setdefault(key, []).append(snippet_elems)
    return snippet_dict


def nicely_print(snippets):
    for key in snippets:
        for snippet in snippets[key][0]:
            if key in snippet:
                print snippet


def start(args):
    # args --> (delta, query, root)
    tw_start = time.time()
    delta = args[0] if args[0] else settings.DEFAULT_DELTA
    manager = server_manager(settings.PORT, settings.AUTH)
    s_job_q = manager.get_job_q()
    s_result_q = manager.get_result_q()
    s_jobs_e = manager.get_jobs_e()

    queryset, testset = file_manager(args[1], args[2])
    try:
        s_jobs_e.set()
        job_n = send_similarity_tasks(delta, queryset, testset, s_job_q)

        similarities = retrieve_similarity_results(job_n, s_result_q)

        print 'Similar models found:'
        for e in similarities.elements:
            print 'Model: %s, Sim: %f' % (os.path.basename(e[1]), e[0])

        job_n = send_clustering_tasks(similarities, s_job_q)

        clusters = retrieve_clustering_results(job_n, s_result_q)

        # for word in clusters:
        #     print '%s (%d):\n%s\n' % (word,
        #                               len(clusters[word]),
        #                               clusters[word])

        snippets = extract_snippets(clusters)

        print ''
        print 'Suggestions:'
        nicely_print(snippets)

    except KeyboardInterrupt:
        stderr.write(" Caught KeyboardInterrupt, sending halt to workers")
        err = 1
    else:
        print '--- DONE ---'
        err = 0
    finally:
        s_jobs_e.clear()
        time.sleep(2)
        manager.shutdown()

    tw_stop = time.time()
    print 'Computed in %s sec.' % (tw_stop - tw_start)
    exit(err)
