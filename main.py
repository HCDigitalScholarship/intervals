from music21 import *
import music21 as m21
import time
import requests
from pathlib import Path

# An extension of the music21 note class with more information easily accessible
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
            print("Requesting file from " + str(path) + "...")
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

# For single file uploads, only takes urls presently
class ScoreBase:
    def __init__(self, url):
        self.url = url
        print("Requesting file from " + str(self.url) + "...")
        try:
            self.score = m21.converter.parse(requests.get(self.url).text)
            print("Successfully imported.")
        except:
            raise Exception("Import from " + str(self.url) + " failed, please check your url/file type")
        self.note_list = self.note_list_whole_piece()
        self.note_list_down_beats = self.note_list_selected_beats([1,3])

    def note_list_whole_piece(self):
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for note in noteList:
                if note.tie is not None:
                    if note.tie.type == 'start':
                        note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url)
                        pure_notes.append(note_obj)
                    else:
                        pure_notes[len(pure_notes)-1].duration += note.quarterLength
                else:
                    note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url)
                    pure_notes.append(note_obj)
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

    # Gets only notes that start on the specified beats- allows for user specification in case of weird time signatures
    def note_list_selected_beats(self, beats: list):
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for note in noteList:
                if note.beat in beats:
                        note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url)
                        pure_notes.append(note_obj)
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

    # Better tuned for different time signatures
    def note_list_by_offset(self, offsets:list):
        pure_notes = []
        part_number = 0
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            part_number += 1
            measures = part.getElementsByClass(stream.Measure)
            for measure in measures:
                voices = measure.getElementsByClass(stream.Voice)
                for voice in voices:
                    for note in voice:
                        for point in offsets:
                            #print(note.offset, point)
                            if point >= note.offset and point < (note.offset + note.quarterLength):
                                note_obj = NoteListElement(note, self.score.metadata, part.partName, part_number, note.quarterLength, self.url)
                                pure_notes.append(note_obj)
                                break
        return pure_notes

    # Allows for very specific note selection
    def note_list_single_part(self, part, measure_start, num_measures):
        pure_notes = []
        part_selected = self.score.getElementsByClass(stream.Part)[part]
        measures = part_selected.getElementsByClass(stream.Measure)
        measures_selected = []
        for i in range(num_measures):
            measures_selected.append(measures[i+measure_start])
        for measure in measures_selected:
            voices = measure.getElementsByClass(stream.Voice)
            for voice in voices:
                for note in voice:
                    print(note.offset)
                    if note.tie is not None:
                        if note.tie.type == 'start':
                            note_obj = NoteListElement(note, self.score.metadata, part_selected.partName, part, note.quarterLength, self.url)
                            pure_notes.append(note_obj)
                        else:
                            pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, self.score.metadata, part_selected.partName, part, note.quarterLength, self.url)
                        pure_notes.append(note_obj)
        return pure_notes

    # Allows for specific selection in terms of measures, but gets all parts/instruments
    def note_list_all_parts(self, measure_start, num_measures):
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
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
                            if note.tie.type == 'start':
                                note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url)
                                pure_notes.append(note_obj)
                            else:
                                pure_notes[len(pure_notes)-1].duration += note.quarterLength
                        else:
                            note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url)
                            pure_notes.append(note_obj)
            # Added rest to ensure parts don't overlap
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url)
            pure_notes.append(note_obj)
        return pure_notes

# An individual vector, not directly used by the user
class VectorInterval:
    def __init__(self, vector, note1: NoteListElement, note2: NoteListElement):
        self.vector = vector
        self.note1 = note1
        self.note2 = note2

    def __str__(self):
        if self.note1.note.isRest or self.note2.note.isRest:
            return "<VectorInterval: Rest, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note, self.note2.note)
        else:
            return "<VectorInterval: {}, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note.nameWithOctave, self.note2.note.nameWithOctave)

# Allows for selected "vectorizations" given a note list created from either ScoreBase or CorpusBase
class IntervalBase:
    def __init__(self, notes):
        self.notes = notes
        self.generic_intervals = self.vectorize_generic(self.notes)
        self.semitone_intervals = self.vectorize_semitone(self.notes)

    # Construct intervals in terms of semitone distances between notes
    def vectorize_semitone(self, notes):
        vec = []
        for i in range(len(notes)-1):
            if notes[i].note.isRest or notes[i+1].note.isRest:
                interval_obj = VectorInterval("Rest", notes[i], notes[i+1])
                vec.append(interval_obj)
            else:
                interval_semitones = interval.Interval(notes[i].note, notes[i+1].note).semitones
                interval_obj = VectorInterval(interval_semitones, notes[i], notes[i+1])
                vec.append(interval_obj)
        return vec

    # Construct intervals in terms of generic distance between notes
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
        # Construct an ema address for the entire pattern to pass on
        ema =  str(self.first_note.note.measureNumber) + "-" + str(self.last_note.note.measureNumber) + "/" + str(self.first_note.partNumber) + "/"
        ema += ("@" + str(self.first_note.note.beat) + "-end")
        for i in range(self.last_note.note.measureNumber - self.first_note.note.measureNumber - 1):
            ema += ",@start-end"
        ema += (",@start-" + str(self.last_note.note.beat))
        self.ema = ema
        splice = self.first_note.piece_url.index('mei/')
        self.ema_url = "https://ema.crimproject.org/https%3A%2F%2Fcrimproject.org%2Fmei%2F" + str(self.first_note.piece_url[splice + 4:]) + "/" + str(self.ema)
        self.durations = durations

# Object representing all the occurences of a pattern in a list of notes/vectors
# User generally doesn't create this- it is done in the finding matches methods
class PatternMatches:
    def __init__(self, pattern, matches:list):
        self.pattern = pattern
        # matches is a list of Match objects with the same pattern
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
        # If a pattern occurs more than the designated threshold, we add it to our list of matches
        if amt > min_matches:
            matches_list = PatternMatches(p, [])
            m += 1
            for a in patterns_data:
                if p == a[0]:
                    exact_match = Match(p, a[1], a[2], a[3])
                    matches_list.matches.append(exact_match)
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact matches.\n")
    # all_matches_list has a nested structure- it contains a list of PatternMatches objects, which contain a list of individual Match objects
    return all_matches_list

# Finds matches based on a cumulative distance difference between two patterns
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
        # If a pattern occurs more than the designated threshold
        for a in patterns_data:
            match = 0
            # Calculate the "difference" by comparing each vector with the matching on in the other pattern
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
# Needs to be called before any matches can be made
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

# Helper for sort_matches
def sortFunc(pattern):
    return len(pattern.matches)

# Sorting based on the amount of matches each pattern has
def sort_matches(matches_list):
    matches_list.sort(reverse=True, key=sortFunc)
    return matches_list

# Generates a score from 0-1 based on how many patterns within a piece can be found in the other
def similarity_score(notes1, notes2, pattern_size):
    interval = pattern_size
    min_matches = 1
    threshold = 1
    vectors1 = IntervalBase(notes1).generic_intervals
    vectors2 = IntervalBase(notes2).generic_intervals

    # For each piece create a list of all patterns and then a list of unique patterns to compare against it
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
    # With lists assembled we can do an easy comparison
    score = 0
    for a in patterns_nodup1:
        if patterns2.count(a) > 0:
            score += 1
    for b in patterns_nodup2:
        if patterns2.count(b) > 0:
            score += 1
    return score / (len(patterns_nodup2) + len(patterns_nodup1))

# Find all occurences of a specified pattern within a corpus
def find_motif(pieces: CorpusBase, motif: list, generic: bool):
    # Assemble into patterns
    vectors = IntervalBase(pieces.note_list)
    if generic:
        patterns = into_patterns([vectors.generic_intervals], len(motif))
    else:
        patterns = into_patterns([vectors.semitone_intervals], len(motif))
    print("Finding instances of pattern " + str(motif) + ": ")
    # Find all occurences of given motif, print out information associated
    occurences = 0
    for pat in patterns:
        if motif == pat[0]:
            print("Selected pattern occurs in " + str(pat[1].metadata.title) + " part " + str(pat[1].part) + " beginning in measure " + str(pat[1].note.measureNumber) + " and ending in measure " + str(pat[2].note.measureNumber) + ". Note durations: " + str(pat[3]))
            occurences += 1
    print("Selected pattern occurs " + str(occurences) + " times.")

# Given list of matches, write to csv in current working directory
def export_to_csv(matches: list):
    proceed = input("This method will create a csv file in your current working directory. Continue? (y/n): ").lower()
    csv_name = input("Enter a name for your csv file (.csv will be appended): ")
    csv_name += '.csv'
    if proceed != 'y' and proceed != 'yes':
        print("Exiting...")
        return
    import csv
    with open(csv_name, mode='w') as matches_file:
        matches_writer = csv.writer(matches_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        matches_writer.writerow(['Pattern Generating Match', 'Pattern matched', 'Piece Title', 'Part', 'First Note Measure Number', 'Last Note Measure Number', 'Note Durations', 'EMA', 'EMA url'])
        for match_series in matches:
            for match in match_series.matches:
                matches_writer.writerow([match_series.pattern, match.pattern, match.first_note.metadata.title, match.first_note.part, match.first_note.note.measureNumber, match.last_note.note.measureNumber, match.durations, match.ema, match.ema_url])
    print("CSV created in your current working directory.")

# For more naive usage- allows for user interaction, has return value of list of matches
# All features incorporated except non-whole piece selection
def assisted_interface():
    print("You can use ctrl-c to quit exit at any time. If you proceed through the entire process, the matches array will be returned from this function")
    urls = []
    url = input("Enter a url, or 'done' when finished: ")
    while url != 'done':
        urls.append(url)
        url = input("Enter a url, or 'done' when finished: ")
    corpus = CorpusBase(urls, [])
    vectors = IntervalBase(corpus.note_list)
    pattern_size = int(input("Enter the size of pattern you would like to analyze: "))
    interval_type = input("Enter 1 to match using generic intervals or enter 2 to match using semitone intervals: ")
    while interval_type != '1' and interval_type != '2':
        interval_type = input("Invalid input, enter 1 for generic intervals or 2 for semitone intervals: ")
    if interval_type == '1':
        patterns = into_patterns([vectors.generic_intervals], pattern_size)
    if interval_type == '2':
        patterns = into_patterns([vectors.semitone_intervals], pattern_size)
    min_matches = int(input("Enter the minimum number of matches needed to be displayed: "))
    close_or_exact = input("Enter 1 to include close matches or enter 2 for only exact matches: ")
    while close_or_exact != '1' and close_or_exact != '2':
        close_or_exact = input("Invalid input, enter 1 for close matches or 2 for only exact matches: ")
    if close_or_exact == '1':
        max_dif = int(input("Enter the maximum total distance threshold for a close match: "))
        matches = find_close_matches(patterns, min_matches, max_dif)
    if close_or_exact == '2':
        matches = find_exact_matches(patterns, min_matches)
    csv_results = input("Export results to CSV? (y/n): ").lower()
    if csv_results == 'y' or csv_results == 'yes':
        export_to_csv(matches)
    print_results = input("Print results? (y/n): ").lower()
    if print_results == 'y' or print_results == 'yes':
        if close_or_exact == '1':
            for item in matches:
                item.print_close_matches()
        if close_or_exact == '2':
            for item in matches:
                item.print_exact_matches()
    return matches
