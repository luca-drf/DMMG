from dmmg import Word
from nltk import FreqDist
from nltk.corpus import brown

import unittest


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.fdist = FreqDist(brown.words())

    def test_information(self):
        word1 = Word('dog', 'NOUN')
        word2 = Word('daewfwf', 'NOUN')

if __name__ == '__main__':
    unittest.main()
