from nltk import FreqDist
from nltk.corpus import brown
from numpy import dot, linalg


class SemanticVec:
    def __init__(self):
        self.fdist = FreqDist(brown.words())

    def __best_sim(self, element, corpus):
        best_sim = 0
        best_word = ''
        for word in corpus:
            sim = element.similarity(word)
            if best_sim < sim:
                best_sim = sim
                best_word = word
        return best_word, best_sim

    def generate(self, corpus, joint_wordset):
        vector = [0] * len(joint_wordset)
        for i, element in enumerate(joint_wordset):
            if element in corpus:
                vector[i] = 2 * element.information(self.fdist)
            else:
                word, sim = self.__best_sim(element, corpus)
                if word:
                    vector[i] = (sim *
                                 element.information(self.fdist) *
                                 word.information(self.fdist))
        return vector

    def sem_similarity(self, vector1, vector2):
        return (dot(vector1, vector2) /
                (linalg.norm(vector1) * linalg.norm(vector2)))
