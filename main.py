from music21 import *
import music21 as m21
import time
import requests
from pathlib import Path

class CorpusBase:
    def __init__(self, urls:list, paths:list):
        self.urls = urls
        self.scores = []
        for url in urls:
            self.scores.append(m21.converter.parse(requests.get(url).text))
        mei_conv = converter.subConverters.ConverterMEI()
        for path in paths:
            self.scores.append(mei_conv.parseFile(path))

    def get_note_list(score):   
        self.note_list = note_list_all_parts(self.score)

class ScoreBase: 
    def __init__(self, url):
        self.url = url
        self.score = m21.converter.parse(requests.get(self.url).text)

    def 
