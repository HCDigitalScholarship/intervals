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

class NoteListElement:
    def __init__(self, note: m21.Note, piece_title, part, duration, piece_url):
        self.note = note
        self.id = self.note.id
        self.piece_title = piece_title
        self.part = part
        self.duration = duration
        self.piece_url = piece_url

class ScoreBase:  
    def __init__(self, url):
        self.url = url
        self.score = m21.converter.parse(requests.get(self.url).text)
        self.note_list = self.note_list_whole_piece(self.score)

    def note_list_whole_piece(self, score):
        pure_notes = []
        parts = score.getElementsByClass(stream.Part)
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for note in noteList:
                if note.tie is not None:
                    if note.tie.type == 'start':
                        note_obj = NoteListElement(note, score.metadata, part.partName, note.quarterLength, self.url)
                        pure_notes.append(note_obj)
                    else:
                        pure_notes[len(pure_notes)-1].duration += note.quarterLength
                else:
                    note_obj = NoteListElement(note, score.metadata, part.partName, note.quarterLength, self.url)
                    pure_notes.append(note_obj)
            note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

    def get_specific_note_list(self, score, part, measure_start, num_measures):
        pure_notes = []
        add_tied_note = True
        part_selected = score.getElementsByClass(stream.Part)[part]
        measures = part_selected.getElementsByClass(stream.Measure)
        measures_selected = []
        for i in range(num_measures):
            measures_selected.append(measures[i+measure_start])
        for measure in measures_selected:
            voices = measure.getElementsByClass(stream.Voice)
            for voice in voices:
                for note in voice:
                    if note.tie is not None:
                        if add_tied_note == True:
                            note_obj = NoteListElement(note, score.metadata.title, part_selected.partName, note.measureNumber, note.quarterLength)
                            pure_notes.append(note_obj)
                            add_tied_note = False
                        else:
                            add_tied_note = True
                            pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, score.metadata.title, part_selected.partName, note.measureNumber, note.quarterLength)
                        pure_notes.append(note_obj)
        return pure_notes
        

    