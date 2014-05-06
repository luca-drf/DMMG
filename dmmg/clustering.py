# import sys
import re
from numpy import argmin
from distances import edit_dist
import settings


class InstructionsIndex(dict):
    def __init__(self):
        self.update({'annotation': [],
                     'array': [],
                     'assert': [],
                     'bool': [],
                     'constraint': [],
                     'enum': [],
                     'float': [],
                     'function': [],
                     'int': [],
                     'list': [],
                     'minimize': [],
                     'maximize': [],
                     'predicate': [],
                     'set': [],
                     'string': [],
                     'tuple': [],
                     'var': []})


class FileIndexer:
    def __init__(self, filename):
        self.filename = filename
        self.index = InstructionsIndex()

        self.__filterlines(self.__readfile(filename))

    def __readfile(self, filename):
        s = ''
        f = open(filename, 'r')
        for line in f:
            m = re.match(r'(.*?)(%)', line)
            if m:
                s += m.group(1).replace('\n', '')
            else:
                s += line.replace('\n', '')
        f.close()
        return s

    def __filterlines(self, s):
        tokens = re.split(r';', s)
        for token in tokens:
            token = re.sub(' +', ' ', token)
            for word in re.findall(r'\w+', token):
                if word in self.index:
                    self.index[word].append(token + ';')
                    break


def initialize_clusters(file_dicts):
    """Fill a feature list (InstructionsIndex) set with all the instructions
    passed as file_dicts. Remove a feature if it is not present in all files.
    """
    feature_list = InstructionsIndex()
    for fd in file_dicts:
        for key in fd.index:
            if fd.index[key] == []:
                try:
                    feature_list.pop(key)
                except KeyError:
                    pass

    for fd in file_dicts:
        for key in feature_list:
            feature_list[key].extend([[i] for i in fd.index[key]])
    return feature_list


def update_clustroid(cluster):
    """Update the clustroid in a cluster using the minimum sum of squares"""
    sum_of_squares = []
    for i in xrange(len(cluster)):
        summ = 0
        for j in xrange(i + 1, len(cluster)):
            summ += pow(edit_dist(cluster[i], cluster[j]), 2)
        sum_of_squares.append(summ)
    c_id = argmin(sum_of_squares)
    cluster.append(cluster[c_id])
    del cluster[c_id]


def set_clustroid_mate(listoclusters):
    """For each cluster, set the [-2] element as the closest to the clustroid
    """
    min_dist = float('inf')
    for cluster in listoclusters:
        if len(cluster) == 1:
            continue
        for i in xrange(len(cluster) - 1):
            dist = edit_dist(cluster[i], cluster[-1])
            if min_dist > dist:
                min_dist = dist
                mate_idx = i
        cluster[-2], cluster[mate_idx] = cluster[mate_idx], cluster[-2]


def clusterize(listoclusters):
    """Create clusters starting from a list of lists of single elements"""
    cluster_size = 1
    while cluster_size < settings.CLUSTER_MAX_SIZE:
        min_dist = float('inf')
        for i in xrange(len(listoclusters)):
            for j in xrange(i + 1, len(listoclusters)):
                dist = edit_dist(listoclusters[i][-1], listoclusters[j][-1])
                if dist < min_dist:
                    min_dist = dist
                    to_merge = (i, j)
        listoclusters[to_merge[0]].extend(listoclusters[to_merge[1]])
        update_clustroid(listoclusters[to_merge[0]])
        cluster_size = max(len(l) for l in listoclusters)

    set_clustroid_mate(listoclusters)

# if __name__ == '__main__':
#     files = sys.argv[1], sys.argv[2], sys.argv[3]

#     file_dicts = []
#     for f in files:
#         file_dicts.append(FileIndexer(f))

#     # for d in file_dicts:
#     #     for word in d.index:
#     #         print '%s (%d):\n%s\n' % (word,
#     #                                   len(d.index[word]),
#     #                                   d.index[word])


#     # Prepare the initial set of clusters
#     clusters = initialize_clusters(file_dicts)
#     for keyword in clusters:
#         clusterize(clusters[keyword])

#     for word in clusters:
#         print '%s (%d):\n%s\n' % (word,
#                                   len(clusters[word]),
#                                   clusters[word])
