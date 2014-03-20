import wordorder as wo
import semantic as sv
from nltk.corpus import brown
from nltk import FreqDist, pos_tag, word_tokenize
from word import Word
from sys import argv
from nltk.tag.mapping import map_tag
from re import match
from multiprocessing import Pool
from time import time


def import_file(filepath):
    """ Take a filepath and return a list of tagged words """
    tokens = []
    with open(filepath, 'r') as f:
        for line in f:
            tokens.extend(word_tokenize(line))
    return pos_tag(tokens)


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


def dmmg(delta, file1, file2):
    tw_start = time()
    p = Pool(2)

    print 'Importing files...'
    tagged = p.map_async(import_file, (file1, file2)).get()

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
    fdist = FreqDist(brown.words())
    semantic_vectors = [p.apply_async(sv.generate, (c, joint_word_set, fdist))
                        for c in corpus]

    sem_measure = sv.sem_similarity(semantic_vectors[0].get(),
                                    semantic_vectors[1].get())

    overall_similarity = delta * sem_measure + (1 - delta) * wos_measure

    tw_stop = time()
    print_stats(order_vectors[0].get(), order_vectors[1].get(), wos_measure,
                semantic_vectors[0].get(), semantic_vectors[1].get(),
                sem_measure, overall_similarity, (tw_start, tw_stop))

if __name__ == "__main__":
    delta, file1, file2 = float(argv[1]), argv[2], argv[3]
    dmmg(delta, file1, file2)
