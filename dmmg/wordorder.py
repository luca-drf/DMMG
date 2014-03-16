from sets import Set
from math import sqrt


# Test method
def count_words(corpus):
    #corpus.words() -> list of words
    print len(corpus.words())
    for word in xrange(10):
        print corpus.words()[word]


# Return the Joint word set given to texts
def create_jointset(corpus_a, corpus_b):
    """ Create the Joint Word Set given two corpus (texts)  """
    # Create a set for the Joint Word
    joint_word_set = Set()
    # Create the re to avoid punctuation
    for word in corpus_a:
        joint_word_set.add(word)
    for word in corpus_b:
        joint_word_set.add(word)
    return joint_word_set


# Given a Sentence/Text, a Joint Word Set, and a Lexical Database
# it creates a Word Order Vecor
def create_ordervec(corpus, joint_word_set):
    """ Given a corpus (text) and a joint word set it creates a WOV """
    threshold = 0.2
    #First we create a list of size |corpus| filled with 0s
    word_order_vector = [0] * len(joint_word_set)

    for idx, element in enumerate(joint_word_set):
        for i, word in enumerate(corpus):
          # The word is present in the sentence:
          # fill the order vector with the corresponding index
            if word == element:
                word_order_vector[idx] = i + 1
                break
        # The word is not present in the sentece:
        # find the most similar word and che how much similar it is
        if word_order_vector[idx] == 0:
            # Find the most semantically similar word
            best_sim_val = 0
            for j, word in enumerate(corpus):
                sim_val = word.similarity(element)
                if sim_val > best_sim_val:
                    best_sim_val = sim_val
                    best_index = j + 1
                # Check if we found a (the best) similar word
            if best_sim_val >= threshold:
                print element, best_sim_val, threshold
                print corpus[best_index - 1]
                # If the related word is similar more than the threshold,
                # use its index in the ordered array
                word_order_vector[idx] = best_index
    # Return the vector
    return word_order_vector


# Calculate the Word Order Similarity between two order vectors
def order_similarity(order_vector_1, order_vector_2):
    """ Calculate the Word Order Similarity between two order vectors """
    diff, sum = 0, 0
    for i in xrange(0, len(order_vector_1)):
        diff = diff + pow(order_vector_1[i] - order_vector_2[i], 2)
        sum = sum + pow(order_vector_1[i] + order_vector_2[i], 2)
    return 1 - (sqrt(diff) / sqrt(sum))
