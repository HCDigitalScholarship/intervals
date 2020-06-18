from music21 import *
import music21 as m21
import time
import requests
from pathlib import Path

# An extension of the music21 note class
class NoteListElement:
    def __init__(self, note: m21.note.Note, metadata, part, partNumber, duration, piece_url):
        self.note = note
        self.id = self.note.id
        self.metadata = metadata
        self.part = part
        self.partNumber = partNumber
        self.duration = duration
        self.piece_url = piece_url

    def __str__(self):
        return "<NoteListElement: {}>".format(self.note.name)

# For mass file uploads, only compatible for whole piece analysis, more specific tuning to come
class CorpusBase:
    def __init__(self, urls:list, paths:list):
        self.urls = urls
        self.scores = []
        self.all_urls = []
        for url in urls:
            print("Requesting file from " + str(url) + "...")
            try:
                self.scores.append(m21.converter.parse(requests.get(url).text))
                print("Successfully imported.")
                self.all_urls.append(url)
            except:
                print("Import from " + str(url) + " failed, please check your url/file type. Continuing to next file...")
        mei_conv = converter.subConverters.ConverterMEI()
        for path in paths:
            try:
                self.scores.append(mei_conv.parseFile(path))
                print("Successfully imported.")
                self.all_urls.append(path)
            except:
                print("Import of " + str(path) + " failed, please check your file path/file type. Continuing to next file...")
        if len(self.scores) == 0:
            raise Exception("At least one score must be succesfully imported")
        self.note_list = self.note_list_whole_piece(self.scores, self.all_urls)

    def note_list_whole_piece(self, scores, all_urls):
        pure_notes = []
        urls_index = 0
        for score in scores:
            parts = score.getElementsByClass(stream.Part)
            for part in parts:
                noteList = part.flat.getElementsByClass(['Note', 'Rest'])
                for note in noteList:
                    if note.tie is not None:
                        if note.tie.type == 'start':
                            note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, all_urls[urls_index])
                            pure_notes.append(note_obj)
                        else:
                            pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, all_urls[urls_index])
                        pure_notes.append(note_obj)
                note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, all_urls[urls_index])
                pure_notes.append(note_obj)
            urls_index += 1
        return pure_notes

# For single file uploads, only takes urls at the moment
class ScoreBase:
    def __init__(self, url):
        self.url = url
        print("Requesting file from " + str(self.url) + "...")
        try:
            self.score = m21.converter.parse(requests.get(self.url).text)
            print("Successfully imported.")
        except:
            raise Exception("Import from " + str(self.url) + " failed, please check your url/file type")
        self.note_list = self.note_list_whole_piece(self.score)

    def note_list_whole_piece(self, score):
        pure_notes = []
        parts = score.getElementsByClass(stream.Part)
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for note in noteList:
                if note.tie is not None:
                    if note.tie.type == 'start':
                        note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.url)
                        pure_notes.append(note_obj)
                    else:
                        pure_notes[len(pure_notes)-1].duration += note.quarterLength
                else:
                    note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.url)
                    pure_notes.append(note_obj)
            note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

    def note_list_single_part(self, score, part, measure_start, num_measures):
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
                            note_obj = NoteListElement(note, score.metadata, part_selected.partName, score.index(part), note.quarterLength, self.url)
                            pure_notes.append(note_obj)
                            add_tied_note = False
                        else:
                            add_tied_note = True
                            pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, score.metadata, part_selected.partName, score.index(part), note.quarterLength, self.url)
                        pure_notes.append(note_obj)
        return pure_notes

    def note_list_all_parts(score, measure_start, num_measures):
        pure_notes = []
        add_tied_note = True
        parts = score.getElementsByClass(stream.Part)
        for part in parts:
            measures = part.getElementsByClass(stream.Measure)
            measures_selected = []
            for i in range(num_measures):
                measures_selected.append(measures[i+measure_start])
            for measure in measures_selected:
                voices = measure.getElementsByClass(stream.Voice)
                for voice in voices:
                    for note in voice:
                        if note.tie is not None:
                            if add_tied_note == True:
                                note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.url)
                                pure_notes.append(note_obj)
                                add_tied_note = False
                            else:
                                add_tied_note = True
                                pure_notes[len(pure_notes)-1].duration += note.quarterLength
                        else:
                            note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.url)
                            pure_notes.append(note_obj)
            # Added rest to ensure parts don't overlap
            note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

# An individual vector, not directly used by the user
class VectorInterval:
    def __init__(self, vector, note1: NoteListElement, note2: NoteListElement):
        self.vector = vector
        self.note1 = note1
        self.note2 = note2

    def __str__(self):
        return "<VectorInterval: {}, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note.nameWithOctave, self.note2.note.nameWithOctave)


class IntervalBase:
    def __init__(self, notes):
        self.notes = notes
        self.generic_intervals = self.vectorize_generic(self.notes)
        self.semitone_intervals = self.vectorize_semitone(self.notes)

    def vectorize_semitone(self, notes):
        vec = []
        for i in range(len(notes)-1):
            try:
                interval = VectorInterval(interval.Interval(notes[i].note, notes[i+1].note).semitones, notes[i], notes[i+1])
                vec.append(interval)
            except:
                interval = VectorInterval("Rest", notes[i], notes[i+1])
                vec.append(interval)
        return vec

    def vectorize_generic(self, notes):
        vec = []
        for i in range(len(notes)-1):
            if notes[i].note.isRest or notes[i+1].note.isRest:
                interval_obj = VectorInterval("Rest", notes[i], notes[i+1])
                vec.append(interval_obj)
            else:
                interval_semitones = interval.Interval(notes[i].note, notes[i+1].note).semitones
                interval_obj = VectorInterval(interval.convertSemitoneToSpecifierGeneric(interval_semitones)[1], notes[i], notes[i+1])
                vec.append(interval_obj)
        return vec

# An individual match event- can be used for close matches as well
class Match:
    def __init__(self, pattern, first_note: NoteListElement, last_note: NoteListElement, durations):
        self.pattern = pattern
        self.first_note = first_note
        self.last_note = last_note
        self.ema = str(self.first_note.note.measureNumber) + "-" + str(self.last_note.note.measureNumber) + "/" + str(self.first_note.partNumber) + "/all/raw"
        self.durations = durations

# Object representing all the occurences of a pattern in a list of notes/vectors
class PatternMatches:
    def __init__(self, pattern, matches:list):
        self.pattern = pattern
        self.matches = matches

    def print_exact_matches(self):
        print("Melodic interval/pattern " + str(self.pattern) + " occurs " + str(len(self.matches)) + " times:")
        for match in self.matches:
            print("In " + str(match.first_note.metadata.title) + " part " + str(match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) +\
            " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(match.durations))
        print("\n")

    def print_close_matches(self):
        print("Occurences of " + str(self.pattern) + " or similar:")
        for match in self.matches:
            print("Pattern " + str(match.pattern) + " appears in " + str(match.first_note.metadata.title) + " part " + str(match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) +\
            " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(match.durations))
        print("Said pattern or similar appeared " + str(len(self.matches)) + " times.\n")

# Standalone methods for match analysis
def find_exact_matches(patterns_data, min_matches):
    # A series of arrays are needed to keep track of various data associated with each pattern
    print("Finding exact matches...")
    patterns_nodup, patterns = [], []
    print(patterns_data)
    p = 0
    for pattern in patterns_data:
        patterns.append(pattern[0])
        if pattern[0] not in patterns_nodup:
            patterns_nodup.append(pattern[0])
    m = 0
    # Go through each individual pattern and count up its occurences
    all_matches_list = []
    for p in patterns_nodup:
        amt = patterns.count(p)
        # If a pattern occurs more than the designated threshold, we print out information about its occurences
        if amt > min_matches:
            matches_list = PatternMatches(p, [])
            m += 1
            for a in patterns_data:
                if p == a[0]:
                    exact_match = Match(p, a[1], a[2], a[3])
                    matches_list.matches.append(exact_match)
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact matches.\n")
    return all_matches_list

def find_close_matches(patterns_data, min_matches, threshold):
    # A series of arrays are needed to keep track of various data associated with each pattern
    print("Finding close matches...")
    patterns_nodup = []
    for pat in patterns_data:
        # Build up a list of patterns without duplicates
        if pat[0] not in patterns_nodup:
            patterns_nodup.append(pat[0])
    # Go through each individual pattern and count up its occurences
    all_matches_list = []
    for p in patterns_nodup:
        matches_list = PatternMatches(p, [])
        # If a pattern occurs more than the designated threshold, we print out information about its occurences
        for a in patterns_data:
            match = 0
            for v in range(len(a[0])):
                match += abs(p[v] - a[0][v])
            if match <= threshold:
                close_match = Match(a[0], a[1], a[2], a[3])
                matches_list.matches.append(close_match)
        if len(matches_list.matches) > min_matches:
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact or close matches.\n")
    return all_matches_list

# Allows for the addition of non-moving-window pattern searching approaches
def into_patterns(vectors_list, interval):
    pattern, patterns_data = [], []
    for vectors in vectors_list:
        for i in range(len(vectors)-interval):
            pattern = []
            durations = []
            valid_pattern = True
            durations.append(vectors[i].note1.duration)
            for num_notes in range(interval):
                if vectors[i+num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors[i+num_notes].vector)
                durations.append(vectors[i+num_notes].note2.duration)
            if valid_pattern:
            # Here, with help from vectorize() you can jam in whatever more data you would like about the note
                patterns_data.append((pattern, vectors[i].note1, vectors[i+num_notes].note2, durations))
    return patterns_data

def sortFunc(pattern):
    return len(pattern.matches)

def sort_matches(matches_list):
    matches_list.sort(reverse=True, key=sortFunc)
    return matches_list

def similarity_score(notes1, notes2, pattern_size):
    # A series of arrays are needed to keep track of various data associated with each pattern
    interval = pattern_size
    min_matches = 1
    threshold = 1
    vectors1 = IntervalBase(notes1).generic_intervals
    vectors2 = IntervalBase(notes2).generic_intervals

    pattern, patterns1, patterns_nodup1, patterns2, patterns_nodup2 = [], [], [], [], []

    for i in range(len(vectors1)-interval):
        pattern = []
        durations = []
        valid_pattern = True
        for num_notes in range(interval):
            if vectors1[i+num_notes].vector == 'Rest':
                valid_pattern = False
            pattern.append(vectors1[i+num_notes].vector)
        if valid_pattern:
            patterns1.append(pattern)

    for i in range(len(vectors2)-interval):
        pattern = []
        durations = []
        valid_pattern = True
        for num_notes in range(interval):
            if vectors2[i+num_notes].vector == 'Rest':
                valid_pattern = False
            pattern.append(vectors2[i+num_notes].vector)
        if valid_pattern:
            patterns2.append(pattern)

    for pat in patterns1:
        if pat not in patterns_nodup1:
            patterns_nodup1.append(pat)
    for pat2 in patterns2:
        if pat2 not in patterns_nodup2:
            patterns_nodup2.append(pat2)

    score = 0
    for a in patterns_nodup1:
        if patterns2.count(a) > 0:
            score += 1
    for b in patterns_nodup2:
        if patterns2.count(b) > 0:
            score += 1
    return score / (len(patterns_nodup2) + len(patterns_nodup1))

def similarity_score2(notes1, notes2, pattern_size):
    notes1_title = notes1[0].metadata.title
    vectors1 = IntervalBase(notes1)
    vectors2 = IntervalBase(notes2)
    exact_matches = find_exact_matches([vectors1.generic_intervals, vectors2.generic_intervals], pattern_size, 3)
    close_matches = find_close_matches([vectors1.generic_intervals, vectors2.generic_intervals], pattern_size, 3, 1)
    score = 0
    for matches in exact_matches:
        from1, from2 = 0, 0
        for match in matches.matches:
            if match.first_note.metadata.title == notes1_title:
                from1 += 1
            else:
                from2 += 1
        if from1 == 0 or from2 == 0:
            pass
        elif from2 / from1 > 4 or from1 / from2 > 4:
            score += (len(matches.matches) / 2)
        else:
            score += len(matches.matches)
    #print(score, len(notes1), len(notes2))
    #return score / (len(notes1) + len(notes2))
    return ((len(exact_matches) / (len(notes1) + len(notes2))) + (len(close_matches) / (len(notes1) + len(notes2)))) / 2

#Example usage
# piece1 = ScoreBase('https://crimproject.org/mei/CRIM_Model_0008.mei')
# piece2 = ScoreBase('https://crimproject.org/mei/CRIM_Mass_0005_1.mei')
# larger_base = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0008.mei', 'https://crimproject.org/mei/CRIM_Mass_0003_4.mei', 'https://crimproject.org/mei/CRIM_Model_0006.mei', 'https://crimproject.org/mei/CRIM_Mass_0008_3.mei', 'https://crimproject.org/mei/CRIM_Mass_0018_4.mei', 'https://crimproject.org/mei/CRIM_Mass_0017_1.mei', 'https://crimproject.org/mei/CRIM_Mass_0013_5.mei', 'https://crimproject.org/mei/CRIM_Mass_0012_2.mei', 'https://crimproject.org/mei/CRIM_Mass_0006_3.mei'],[])
base = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0005_1.mei', 'https://crimproject.org/mei/CRIM_Model_0008.mei'],[])
vector = IntervalBase(base.note_list)
patterns = into_patterns([vector.generic_intervals], 5)
matches_list1 = find_exact_matches(patterns, 10)
sort_matches(matches_list1)
for item in matches_list1:
    item.print_exact_matches()
matches_list2 = find_close_matches(patterns, 10, 1)
sort_matches(matches_list2)
for item in matches_list2:
    item.print_close_matches()
# print(similarity_score(piece1.note_list, piece2.note_list, 5))
# print(similarity_score2(piece1.note_list, piece2.note_list, 5))
