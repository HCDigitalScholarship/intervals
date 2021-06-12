"""
In this script I play with the crim interface
"""

from main import *
import pandas as pd

corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0017.mei'])

model = corpus.scores[0]

# print methods we can run with dir
print(dir(model))

# get documentation
print(model.getMelodic.__doc__)

mel2 = model.getMelodic(kind='c', directed=False, compound=False)
print(mel2)






