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

"""
mel2 = model.getMelodic(kind='c', directed=False, compound=False).head(20)

File "/Users/dangtrang/OneDrive - brynmawr.edu/summer 2021/crim_intervals/intervals/main_objs.py", 
line 89, in <lambda> ('c', False, False): lambda cell: str(abs(cell.semitones)) % 12 if hasattr(cell, 
'semitones') else cell
TypeError: not all arguments converted during string formatting
"""






