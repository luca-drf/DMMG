import wordorder as wo
from semantic import SemanticVec
from word import Word
from sys import argv
from nltk import pos_tag, word_tokenize
from nltk.tag.mapping import map_tag


def import_file(filepath):
    """ Return a list of tagged words """
    tokens = []
    with open(filepath, 'r') as f:
        for line in f:
            tokens.extend(word_tokenize(line))
    return pos_tag(tokens)


def create_corpus(tagged):
    return [Word(pair[0], map_tag('en-ptb', 'universal', pair[1]))
            for pair in tagged]


def print_stats(order_vector_1, order_vector_2, wos_measure,
                semantic_vector_1, semantic_vector_2, sem_measure,
                overall_similarity):

    print '== Order Vectors =='
    print order_vector_1
    print order_vector_2
    print 'W.O. Similarity:', wos_measure
    print ''
    print '== Semantic Vectors =='
    print semantic_vector_1
    print semantic_vector_2
    print ''
    print 'Semantic Similarity:', sem_measure
    print '---------------------------------'
    print 'Overall Similarity:', overall_similarity


def main():
    delta = float(argv[1])
    tagged1 = import_file(argv[2])
    tagged2 = import_file(argv[3])

    corpus_s1 = create_corpus(tagged1)
    corpus_s2 = create_corpus(tagged2)

    # Create the joint word text
    joint_word_set = wo.create_jointset(corpus_s1, corpus_s2)

    # Create the two order vectors
    order_vector_1 = wo.create_ordervec(corpus_s1, joint_word_set)
    order_vector_2 = wo.create_ordervec(corpus_s2, joint_word_set)

    # Calculate the Word Order Similarity of the two vectors
    wos_measure = wo.order_similarity(order_vector_1, order_vector_2)

    # Calculate the two semantic vectors
    sv = SemanticVec()
    semantic_vector_1 = sv.generate(corpus_s1, joint_word_set)
    semantic_vector_2 = sv.generate(corpus_s2, joint_word_set)

    sem_measure = sv.sem_similarity(semantic_vector_1, semantic_vector_2)

    overall_similarity = delta * sem_measure + (1 - delta) * wos_measure

    print_stats(order_vector_1, order_vector_2, wos_measure,
                semantic_vector_1, semantic_vector_2, sem_measure,
                overall_similarity)


if __name__ == "__main__":
    main()
