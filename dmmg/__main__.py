import wordorder as wo
from word import Word
from sys import argv
import nltk
from nltk.tag.mapping import map_tag
# import re
# from nltk.corpus import PlaintextCorpusReader


def import_file(filepath):
    """ Return a list of tagged words """
    tokens = []
    with open(filepath, 'r') as f:
        for line in f:
            tokens.extend(nltk.word_tokenize(line))
    return nltk.pos_tag(tokens)


def create_corpus(tagged):
    return [Word(pair[0], map_tag('en-ptb', 'universal', pair[1]))
            for pair in tagged]


def main():
    tagged1 = import_file(argv[1])
    tagged2 = import_file(argv[2])

    corpus_s1 = create_corpus(tagged1)
    corpus_s2 = create_corpus(tagged2)

    # Split the paths and the files' names
    # splitter = re.compile(r'(.*?)([a-zA-Z0-9._-]+$)')
    # match_s1 = splitter.findall(path_sentence_1)
    # match_s2 = splitter.findall(path_sentence_2)

    # # Create two corpus: one for each sentence/text
    # corpus_root_s1, filename_s1 = match_s1[0][0], match_s1[0][1]
    # corpus_root_s2, filename_s2 = match_s2[0][0], match_s2[0][1]
    # corpus_s1 = PlaintextCorpusReader(corpus_root_s1, filename_s1)
    # corpus_s2 = PlaintextCorpusReader(corpus_root_s2, filename_s2)

    # Create the joint word text
    joint_word_set = wo.create_jointset(corpus_s1, corpus_s2)

    # Create the two order vectors
    order_vector_1 = wo.create_ordervec(corpus_s1, joint_word_set)
    order_vector_2 = wo.create_ordervec(corpus_s2, joint_word_set)

    # Calculate the Word Order Similarity of the two vectors
    wos_measure = wo.order_similarity(order_vector_1, order_vector_2)

    print wos_measure


if __name__ == "__main__":
    main()
