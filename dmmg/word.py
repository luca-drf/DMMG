from nltk.corpus import wordnet as wn
# from re import match
from math import log


class Word:
    def __init__(self, word, part):
        self.string = str(word)  # The string representing the word
        self.part = part   # The part of speech {ADJ, ADV, NOUN, VERB...}

    def __str__(self):
        return "%s/%s" % (self.string, self.part)

    def __repr__(self):
        return "%s/%s" % (self.string, self.part)

    def __hash__(self):
        return hash((self.string, self.part))

    def __lt__(self, other):
        return self.string < other.string

    def __le__(self, other):
        return self.string <= other.string

    def __eq__(self, other):
        return (self.string == other.string) and (self.part == other.part)

    def __ne__(self, other):
        return (self.string != other.string) or (self.part != other.part)

    def __gt__(self, other):
        return self.string > other.string

    def __ge__(self, other):
        return self.string >= other.string

    def similarity(self, other):
        """ Return Wu & Palmer Similarity between two words.
        Return 0 if words' parts are not equals """
        part = self.__part_converter(self.part)
        if part != self.__part_converter(other.part):
            return 0
        tresh = 0.2
        sss = wn.synsets(self.string, part)
        sso = wn.synsets(other.string, part)
        best_sim = 0
        for ss in sss:
            # if not match('^' + self.string + '\..+', ss.name()):
                # continue
            for so in sso:
                # if not match('^' + other.string + '\..+', so.name()):
                    # continue
                sim = ss.wup_similarity(so)
                if (tresh < sim) and (best_sim < sim):
                    best_sim = sim
        return best_sim

    def information(self, fdist):
        """ Return the Information for this word given a probability
        distribution (FreqDist) """
        freq = fdist.get(self.string)
        if not freq:
            freq = 0
        return 1 - (log(freq + 1) / log(fdist.N() + 1))

    def __part_converter(self, part):
        if part == 'NOUN':
            return wn.NOUN
        elif part == 'VERB':
            return wn.VERB
        elif part == 'ADJ':
            return wn.ADJ
        elif part == 'ADV':
            return wn.ADV
        else:
            return ''
