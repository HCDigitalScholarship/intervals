"""
In this script I play with the crim interface
"""

from main import *
from main_objs import ImportedPiece
import pandas as pd
import music21

def test_time_signature(mei_file):

    corpus = CorpusBase([mei_file])

    model = corpus.scores[0]

    # # print methods we can run with dir
    # print(dir(model))

    # # get documentation
    # print(model.getMelodic.__doc__)

    time_signature = model.getTimeSignature()
    print(time_signature)

def simple_test_time_signature():

    noteC = music21.note.Note("C4", type="half")
    noteD = music21.note.Note("D4", type="quarter")
    noteE = music21.note.Note("E4", type="quarter")
    noteF = music21.note.Note("F4", type="half")

    tsThreeFour = music21.meter.TimeSignature('3/4')

    stream1 = music21.stream.Stream()

    for thisThing in [tsThreeFour, noteC, noteD, noteE, noteF]:
        stream1.append(thisThing)
    
    test = ImportedPiece(stream1)
    test.getTimeSignature()

test_time_signature('https://crimproject.org/mei/CRIM_Model_0008.mei')

# simple_test_time_signature()


