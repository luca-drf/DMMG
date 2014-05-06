import wordorder as wo
import semantic as sv
from nltk import pos_tag, word_tokenize, FreqDist
from word import Word
from nltk.tag.mapping import map_tag
from re import match
from multiprocessing import Pool
from time import time
import json
import os
from nltk import download
from nltk.downloader import Downloader
from sets import Set
import settings


def nltk_updater():
    packages = Set(['brown',
                    'wordnet',
                    'wordnet_ic',
                    'maxent_treebank_pos_tagger',
                    'universal_tagset'])
    d = Downloader()
    for dirpath, dirnames, filenames in os.walk(d.default_download_dir()):
        module = os.path.basename(dirpath)
        if module in packages:
            packages.remove(module)
    for module in packages:
        print 'Missing', module
        download(module)


def filepath_gen(path):
    if os.path.isfile(path):
        yield path
    else:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if not filename.startswith('.'):
                    yield os.path.join(dirpath, filename)


def import_file(filepath):
    """ Take a filepath and return a list of tagged words """
    tokens = []
    f = open(filepath, 'r')
    for line in f:
        tokens.extend(word_tokenize(line))
    f.close()
    return pos_tag(tokens)


def retrieve_model_file(test_filepath):
    return os.path.join(settings.MODELS_DIR, os.path.basename(test_filepath))


def create_corpus(tagged):
    """ Take a list of tagged words and return a corpus as a list of tagged
    words with universal tagging and filtering all non-word entries """
    corpus = []
    for pair in tagged:
        if match(r'[a-zA-Z0-9_-]+', pair[0]):
            try:
                corpus.append(Word(pair[0],
                              map_tag('en-ptb', 'universal', pair[1])))
            except KeyError:
                print 'Part mismatch:', pair[0], pair[1]
    return corpus


def print_stats(order_vector_1, order_vector_2, wos_measure,
                semantic_vector_1, semantic_vector_2, sem_measure,
                overall_similarity, time):

    # print '== Order Vectors =='
    # print order_vector_1
    # print order_vector_2
    print ''
    print 'W.O. Similarity:', wos_measure
    # print ''
    # print '== Semantic Vectors =='
    # print semantic_vector_1
    # print semantic_vector_2
    # print ''
    print 'Semantic Similarity:', sem_measure
    print '---------------------------------'
    print 'Overall Similarity:', overall_similarity,
    print 'Computed in %s sec.' % (time[1] - time[0])


def similarity(delta, file1, file2):
    tw_start = time()
    p = Pool(2)

    print 'Importing files...'
    print file2
    try:
        tagged = p.map_async(import_file, (file1, file2)).get()
    except UnicodeDecodeError as error:
        print error
        print 'File1:', file1
        print 'File2:', file2
        exit(1)

    print 'Creating corpus...'
    corpus = p.map_async(create_corpus, tagged).get()

    print 'Creating joint wordset...'
    joint_word_set = wo.create_jointset(corpus[0], corpus[1])

    print 'Creating order vectors...'
    order_vectors = [p.apply_async(wo.create_ordervec, (c, joint_word_set))
                     for c in corpus]

    # Calculate the Word Order Similarity of the two vectors
    wos_measure = wo.order_similarity(order_vectors[0].get(),
                                      order_vectors[1].get())

    print 'Creating semantic vectors...'
    # fdist = FreqDist(brown.words())
    f = open('dmmg/fdist.json', 'r')
    freqs = json.load(f)
    f.close()
    fdist = FreqDist(freqs)

    semantic_vectors = [p.apply_async(sv.generate, (c, joint_word_set, fdist))
                        for c in corpus]
    sem_measure = sv.sem_similarity(semantic_vectors[0].get(),
                                    semantic_vectors[1].get())
    p.close()
    p.join()
    overall_similarity = delta * sem_measure + (1 - delta) * wos_measure

    tw_stop = time()
    print_stats(order_vectors[0].get(), order_vectors[1].get(), wos_measure,
                semantic_vectors[0].get(), semantic_vectors[1].get(),
                sem_measure, overall_similarity, (tw_start, tw_stop))

    return overall_similarity, sem_measure, wos_measure


class Storage:
    def __init__(self, similarity):
        self.similarity = similarity
        self.elements = []

    def __str__(self):
        return self.elements.__str__() + 'sim: ' + str(self.similarity)

    def __repr__(self):
        return self.elements.__str__() + 'sim: ' + str(self.similarity)

    def store(self, tup):
        if tup[0] >= self.similarity:
            self.elements.append(tup)

    # # The following code is in case we want to track a fixed number of files
    # def store(self, tup):
    #     """Binary search and insert"""
    #     if tup[0] >= self.similarity:
    #         l = 0
    #         r = len(self.elements) - 1
    #         indx = 0
    #         # Store the insertion point in indx
    #         while l <= r:
    #             mid = l + (r - l) / 2
    #             if self.elements[mid] == tup:
    #                 indx = mid + 1
    #                 break
    #             elif self.elements[mid] > tup:
    #                 if l == r:
    #                     indx = mid + 1
    #                 l = mid + 1
    #             else:
    #                 if l == r:
    #                     indx = mid - 1
    #                 r = mid - 1
    #         self.elements.insert(indx, tup)
