import sys
sys.path.append('..')
from dmmg.clustering import FileIndexer, initialize_clusters, clusterize
from dmmg.dmmgmain import filepath_gen
from dmmg.dmmgserver import extract_snippets

if __name__ == '__main__':
    source = sys.argv[1]
    index_list = []

    for f in filepath_gen(source):
        index_list.append(FileIndexer(f))

    cluster_dict = initialize_clusters(index_list)

    for key in cluster_dict:
        clusterize(cluster_dict[key])

    for word in cluster_dict:
        print '%s (%d):\n%s\n' % (word,
                                  len(cluster_dict[word]),
                                  cluster_dict[word])

    snippets = extract_snippets(cluster_dict)

    for key in snippets:
        print snippets[key]
