from music21 import *
# httpx appears to be faster than requests, will fit better with an async version
import httpx
from pathlib import Path
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from itertools import combinations
from itertools import combinations_with_replacement as cwr
import os
import re
import intervals
cwd = os.path.dirname(intervals.__file__)

MEINSURI = 'http://www.music-encoding.org/ns/mei'
MEINS = '{%s}' % MEINSURI
suppliedPattern = re.compile("<supplied.*?(<accid.*?\/>).*?<\/supplied>", flags=re.DOTALL)


pathDict = {}
# An extension of the music21 note class with more information easily accessible
def importScore(path):
    '''
    Import piece and return a music21 score. Return None if there is an error.
    '''
    if path in pathDict:
        print('Memoized piece detected.')
    else:
        if path.startswith('http'):
            print('Downloading remote score...')
            try:
                to_import = httpx.get(path).text
                mei_doc = ET.fromstring(to_import) if path.endswith('.mei') else None
            except:
                print('Error downloading',  str(path) + ', please check',
                      'your url and try again. Continuing to next file.')
                return None
        else:
            if path.endswith('.mei'):
                with open(path, "r") as file:
                    to_import = file.read()
                    mei_doc = ET.fromstring(to_import)
            else:
                mei_doc = None
        try:
            if mei_doc is not None:
                to_import = re.sub(suppliedPattern, '\\1', to_import)
            score = converter.parse(to_import)
            pathDict[path] = ImportedPiece(score, path, mei_doc)
            print("Successfully imported", path)
        except:
            print("Import of", str(path), "failed, please check your file path/url.")
            return None

    return pathDict[path]

# Allows for the addition of non-moving-window pattern searching approaches
# Needs to be called before any matches can be made
def into_patterns(vectors_list, interval):
    """Takes in a series of vector patterns with data attached and finds close matches
    Parameters
    ----------
    vectors_list : list of vectorized lists
        MUST be a list from calling generic_intervals or semitone_intervals on a VectorInterval object
    interval : int
        size of interval to be analyzed
    Returns
    -------
    patterns_data : list of tuples
        A list of vector patterns with additional information about notes attached
    """
    pattern, patterns_data = [], []
    for vectors in vectors_list:
        for i in range(len(vectors) - interval):
            pattern = []
            durations = []
            valid_pattern = True
            durations.append(vectors[i].note1.duration)
            for num_notes in range(interval):
                if vectors[i + num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors[i + num_notes].vector)
                durations.append(vectors[i + num_notes].note2.duration)
            if valid_pattern:
                # Here, with help from vectorize() you can jam in whatever more data you would like about the note
                patterns_data.append((pattern, vectors[i].note1, vectors[i + num_notes].note2, durations))
    return patterns_data

# Potential redesign needed due to unstable nature of having user give over patterns_data
# Potential fix is reincorporating into_patterns back into this method
def find_exact_matches(patterns_data, min_matches=5):
    """Takes in a series of vector patterns with data attached and finds exact matches
    Parameters
    ----------
    patterns_data : return value from into_patterns
        MUST be return value from into_patterns
    min_matches : int, optional
        Minimum number of matches needed to be deemed relevant, defaults to 5
    Returns
    -------
    all_matches_list : list
        A list of PatternMatches objects
    """
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
    """Takes in a series of vector patterns with data attached and finds close matches
    Parameters
    ----------
    patterns_data : return value from into_patterns
        MUST be return value from into_patterns
    min_matches : int, optional
        Minimum number of matches needed to be deemed relevant, defaults to 5
    threshold : int
        Cumulative variance allowed between vector patterns before they are deemed not similar
    Returns
    -------
    all_matches_list : list
        A list of PatternMatches objects
    """
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
            rhytmic_match = 0
            # Calculate the "difference" by comparing each vector with the matching one in the other pattern
            for v in range(len(a[0])):
                rhytmic_match += abs(p[v] - a[0][v])
            if rhytmic_match <= threshold:
                close_match = Match(a[0], a[1], a[2], a[3])
                matches_list.matches.append(close_match)
        if len(matches_list.matches) > min_matches:
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(
        min_matches) + " exact or close matches.\n")
    return all_matches_list

def export_pandas(matches):
    match_data = []
    for match_series in matches:
        for match in match_series.matches:
            match_dict = {
                "pattern_generating_match": match_series.pattern,
                "pattern_matched": match.pattern,
                "piece_title": match.first_note.metadata.title,
                "part": match.first_note.part,
                "start_measure": match.first_note.note.measureNumber,
                "start_beat": match.first_note.note.beat,
                "end_measure": match.last_note.note.measureNumber,
                "end_beat": match.last_note.note.beat,
                "start_offset": match.first_note.offset,
                "end_offset": match.last_note.offset,
                "note_durations": match.durations,
                "ema": match.ema,
                "ema_url": match.ema_url
            }
            match_data.append(match_dict)
    return pd.DataFrame(match_data)

# Filters for the length of the Presentation Type in the Classifier
def limit_offset_size(array, limit):
    under_limit = np.cumsum(array) <= limit
    return array[: sum(under_limit)]

# Gets the the list of offset differences for each group
def get_offset_difference_list(group):
    # if we do sort values as part of the func call, then we don't need this first line
    group = group.sort_values("start_offset")
    group["next_offset"] = group.start_offset.shift(-1)
    offset_difference_list = (group.next_offset - group.start_offset).dropna().tolist()
    return offset_difference_list

# The classifications are done here
# be sure to have the offset difference limit set here and matched in gap check below  80 = ten bars
def classify_offsets(offset_difference_list, offset_difference_limit):
    """
    Put logic for classifying an offset list here
    """
    offset_difference_list = limit_offset_size(offset_difference_list, offset_difference_limit)
    alt_list = offset_difference_list[::2]

    if len(set(offset_difference_list)) == 1 and len(offset_difference_list) > 1:
        return ("PEN", offset_difference_list)
    # elif (len(offset_difference_list) %2 != 0) and (len(set(alt_list)) == 1):
    elif (len(offset_difference_list) % 2 != 0) and (len(set(alt_list)) == 1) and (len(offset_difference_list) >= 3):
        return ("ID", offset_difference_list)
    elif len(offset_difference_list) >= 1:
        return ("Fuga", offset_difference_list)
    else:
        return ("Singleton", offset_difference_list)

def predict_type(group, offset_difference_limit):
    offset_differences = get_offset_difference_list(group)
    predicted_type, offsets = classify_offsets(offset_differences, offset_difference_limit)

    group["predicted_type"] = [predicted_type for i in range(len(group))]
    group["offset_diffs"] = [offsets for i in range(len(group))]
    group["entry_number"] = [i + 1 for i in range(len(group))]
    return group


class NoteListElement:
    """
    An extension of the music21 note class

    Attributes
    ----------
    note : music21.note.Note
        music21 note class
    offset : int
        cumulative offset of note
    id : int
        unique music21 id
    metadata : music21.metadata
        piece metadata- not normally attached to a music21 note
    part : str
        voice name
    partNumber : int
        voice number, not 0 indexed
    duration : int
        note duration
    piece_url : str
        piece url for note
    prev_note : NoteListElement
        prior non-rest note element
    """
    def __init__(self, note: note.Note, metadata, part, partNumber, duration, piece_url, prev_note=None):
        self.note = note
        self.prev_note = prev_note
        self.offset = self.note.offset
        self.id = self.note.id
        self.metadata = metadata
        self.part = part
        self.partNumber = partNumber
        self.duration = duration
        self.piece_url = piece_url

    def __str__(self):
        return "<NoteListElement: {}>".format(self.note.name)


class ImportedPiece:
    def __init__(self, score, path, mei_doc=None):
        self.score = score
        self.path = path
        self.mei_doc = mei_doc
        self.analyses = {'note_list': None}
        if mei_doc is not None:
            title = mei_doc.find('mei:meiHead//mei:titleStmt/mei:title', namespaces={"mei": MEINSURI})
            title = title.text if title is not None and hasattr(title, 'text') else 'Not found'
            title_cleaned = re.sub(r'\n', '', title).strip()
            composer = mei_doc.find('mei:meiHead//mei:titleStmt//mei:persName[@role="composer"]', namespaces={"mei": MEINSURI})
            if composer is None:  # for mei 3 files
                composer = mei_doc.find('mei:meiHead//mei:titleStmt/mei:composer', namespaces={"mei": MEINSURI})
            composer = composer.text if composer is not None and hasattr(composer, 'text') else 'Not found'
            composer_cleaned = re.sub(r'\n', '', composer).strip()
            self.metadata = {'title': title_cleaned, 'composer': composer_cleaned}
        else:
            self.metadata = {'title': 'Not found', 'composer': 'Not found'}
        self._intervalMethods = {
            # (quality, directed, compound):   function returning the specified type of interval
            # diatonic with quality
            ('q', True, True): ImportedPiece._qualityDirectedCompound,
            ('q', True, False): ImportedPiece._qualityDirectedSimple,
            ('q', False, True): lambda cell: cell.name if hasattr(cell, 'name') else cell,
            ('q', False, False): lambda cell: cell.semiSimpleName if hasattr(cell, 'semiSimpleName') else cell,
            # diatonic interals without quality
            ('d', True, True): lambda cell: cell.directedName[1:] if hasattr(cell, 'directedName') else cell,
            ('d', True, False): ImportedPiece._noQualityDirectedSemiSimple,
            ('d', True, 'simple'): ImportedPiece._noQualityDirectedSimple,
            ('d', False, True): lambda cell: cell.name[1:] if hasattr(cell, 'name') else cell,
            ('d', False, False): lambda cell: cell.semiSimpleName[1:] if hasattr(cell, 'semiSimpleName') else cell,
            # chromatic intervals
            ('c', True, True): lambda cell: str(cell.semitones) if hasattr(cell, 'semitones') else cell,
            ('c', True, False): lambda cell: str(cell.semitones % 12) if hasattr(cell, 'semitones') else cell,
            ('c', False, True): lambda cell: str(abs(cell.semitones)) if hasattr(cell, 'semitones') else cell,
            ('c', False, False): lambda cell: str(abs(cell.semitones) % 12) if hasattr(cell, 'semitones') else cell
        }

    def _getPartSeries(self):
        if 'PartSeries' not in self.analyses:
            part_series = []
            for i, flat_part in enumerate(self._getSemiFlatParts()):
                notesAndRests = flat_part.getElementsByClass(['Note', 'Rest'])
                part_name = flat_part.partName or 'Part_' + str(i + 1)
                ser = pd.Series(notesAndRests, name=part_name)
                ser.index = ser.apply(lambda noteOrRest: noteOrRest.offset)
                ser = ser[~ser.index.duplicated()]  # remove multiple events at the same offset in a given part
                part_series.append(ser)
            self.analyses['PartSeries'] = part_series
        return self.analyses['PartSeries']

    def _getSemiFlatParts(self):
        """
        Return and store flat parts inside a piece using the score attribute.
        """
        if 'SemiFlatParts' not in self.analyses:
            parts = self.score.getElementsByClass(stream.Part)
            self.analyses['SemiFlatParts'] = [part.semiFlat for part in parts]
        return self.analyses['SemiFlatParts']

    def _getPartNames(self):
        """
        Return flat names inside a piece using the score attribute.
        """
        if 'PartNames' not in self.analyses:
            part_names = []
            for i, part in enumerate(self._getSemiFlatParts()):
                part_names.append(part.partName or 'Part_' + str(i + 1))
            self.analyses['PartNames'] = part_names
        return self.analyses['PartNames']

    def _getM21Objs(self):
        if 'M21Objs' not in self.analyses:
            part_names = self._getPartNames()
            self.analyses['M21Objs'] = pd.concat(self._getPartSeries(), names=part_names, axis=1)
        return self.analyses['M21Objs']

    def _remove_tied(self, noteOrRest):
        if hasattr(noteOrRest, 'tie') and noteOrRest.tie is not None and noteOrRest.tie.type != 'start':
            return np.nan
        return noteOrRest

    def _getM21ObjsNoTies(self):
        if 'M21ObjsNoTies' not in self.analyses:
            df = self._getM21Objs().applymap(self._remove_tied).dropna(how='all')
            self.analyses['M21ObjsNoTies'] = df
        return self.analyses['M21ObjsNoTies']

    def regularize(self, df, unit=2):
        '''
        Return the passed `pandas.DataFrame` (df) with its observations
        regularized rhythmically. Pass a duration as the `unit` parameter to
        control at what regular distance observations will be made. Durations
        are measured according to the music21 convention where:

        eighth note = .5
        quarter note = 1
        half note = 2
        etc.

        For example, if you pass a dataframe of the notes and rests of a piece,
        and set `unit` to 4, a new whatever is "sounding" (whether a note or a
        rest) at every regular whole note will be kept, and any intervening
        notes or rests will be removed. A breve would get renotated as two
        whole notes.
        Regularization also works with non-integer values. So if you wanted to
        regularize at the swung eigth note, for example, you could set:

        `unit=1/3`
        '''
        spot = df.index[0] * 1000
        end = self.score.highestTime * 1000
        vals = []
        step = unit * 1000
        while spot < end:
            vals.append(spot)
            spot += step
        new_index = pd.Index(vals).map(lambda i: round(i) / 1000)
        res = df.ffill().reindex(new_index, method='pad')
        return res

    def _durationHelper(self, col, n):
        col = col.dropna()
        vals = col.index[n:] - col.index[:-n]
        return pd.Series(vals, col.index[:-n])

    def _maxnDurationHelper(self, _col):
        col = _col.dropna()
        starts = col[(col != 'Rest') & (col.shift(1).isin(('Rest', np.nan)))]
        ends = col[(col == 'Rest') & (col.shift(1) != 'Rest')]
        starts.dropna(inplace=True)
        ends.dropna(inplace=True)
        lenStarts = len(starts)
        colDurs = ends.index[-lenStarts:] - starts.index
        starts[:] = colDurs
        return starts

    def durations(self, df=None, n=1, mask_df=None):
        '''
        If no arguments are passed, return a `pandas.DataFrame` of floats giving
        the duration of notes and rests in each part where 1 = quarternote,
        1.5 = a dotted quarter, 4 = a whole note, etc. If a df is passed, then
        return a df of the same shape giving the duration of each of the cells
        of this df. This is useful if you want to know what the durations of
        something other than single notes and rests, such as the durations of
        intervals. E.g.:

        har = importedPiece.harmonic()
        harDur = importedPiece.durations(df=har)

        The `n` parameter should be an integer greater than zero, or -1. When
        n is a positive integer, it groups together a sliding window of n
        consecutive non-NaN cells in each column. If you pass a df, it will sum
        the durations 'Rest' and non-Rest cell, provided they are in the same
        n-sized window. For example, set n=3 if you wanted to get the durations
        of all 3-event-long pair-wise harmonic events:

        har = importedPiece.harmonic()
        dur_3 = importedPiece.durations(df=har, n=3)

        Setting n to -1 sums the durations of all adjacent non-rest events,
        excluding NaNs. You could use this to find the durations of all melodies
        in a piece. Note that the results of .notes() will be used for the
        `df` parameter if none is provided:

        dur = importedPiece.durations(n=-1)

        You can also pass a `mask_df`, which will serve as a filter, only
        keeping values at the same indecies (i.e. index and columns) as mask_df.
        This is needed to get the durations of ngrams. To get the durations of
        ngrams, pass the same value of n and the samedataframe you passed to
        .ngrams() as the `n` and `df` parameters, then pass your dataframe of
        ngrams as the `mask_df`. For example:

        har = importedPiece.harmonic()
        mel = importedPiece.melodic()
        _n = 5
        ngrams = importedPiece.ngrams(df=har, other=mel, n=_n)
        ngramDurations = importedPiece.durations(df=har, n=_n, mask_df=ngrams)
        '''
        if 'Duration' in self.analyses and df is None and n == 1 and mask_df is None:
            return self.analyses['Duration']
        _df = self.notes().copy() if df is None else df.copy()
        highestTime = self.score.highestTime
        _df.loc[highestTime, :] = 'Rest'  # this is just a placeholder
        if n > 0:
            result = _df.apply(self._durationHelper, args=(n,))
            if df is None and n == 1 and mask_df is None:
                self.analyses['Duration'] = result
        else:  # n == -1
            result = _df.apply(self._maxnDurationHelper)
        result = result.astype('float64')
        result.index = result.index.astype('float64')
        if mask_df is not None:
            mask = mask_df.applymap(lambda cell: True, na_action='ignore')
            result = result[mask]
        return result.dropna(how='all')

    def getDuration(self, df=None, n=1, mask_df=None):
        return self.durations(df, n, mask_df)

    def lyrics(self):
        '''
        Return a dataframe of the lyrics associated with each note in the piece.
        '''
        if 'Lyric' not in self.analyses:
            df = self._getM21ObjsNoTies().applymap(na_action='ignore',
                func=lambda note: note.lyric if note.isNote else None)
            df.fillna(np.nan, inplace=True)
            self.analyses['Lyric'] = df
        return self.analyses['Lyric']
    
    def getLyric(self):
        return self.lyrics()

    def _noteRestHelper(self, noteOrRest):
        if noteOrRest.isRest:
            return 'Rest'
        return noteOrRest.nameWithOctave

    def _combineRests(self, col):
        col = col.dropna()
        return col[(col != 'Rest') | ((col == 'Rest') & (col.shift(1) != 'Rest'))]

    def _combineUnisons(self, col):
        col = col.dropna()
        return col[(col == 'Rest') | (col != col.shift(1))]

    def notes(self, combineRests=True, combineUnisons=False):
        '''
        Return a table of the notes and rests in the piece. Rests are
        designated with the string "Rest". Notes are shown such that middle C
        is "C4".
        If `combineRests` is True (default), non-first consecutive rests will be
        removed, effectively combining consecutive rests in each voice.
        `combineUnisons` works the same way for consecutive attacks on the same
        pitch in a given voice, however, `combineUnisons` defaults to False.
        '''
        if 'Notes' not in self.analyses:
            df = self._getM21ObjsNoTies().applymap(self._noteRestHelper, na_action='ignore')
            self.analyses['Notes'] = df
        ret = self.analyses['Notes'].copy()
        if combineRests:
            ret = ret.apply(self._combineRests)
        if combineUnisons:
            ret = ret.apply(self._combineUnisons)
        return ret

    def getNoteRest(self, combineRests=True, combineUnisons=False):
        return self.notes(combineRests, combineUnisons)

    def _getBeatUnit(self):
        '''
        Return a dataframe of the duration of the beat for each time signature
        object in the piece.
        '''
        tsigs = self._getM21TSigObjs()
        tsigs.columns = self._getPartNames()
        df = tsigs.applymap(lambda tsig: tsig.beatDuration.quarterLength, na_action='ignore')
        return df

    def getBeat(self):
        '''
        Return a table of the beat positions of all the notes and rests. Beats
        are expressed as floats.
        '''
        if 'Beat' not in self.analyses:
            nr = self.notes()
            nrOffs = nr.apply(lambda row: row.index)
            ms = self.measures().apply(lambda row: row.index)
            temp = pd.concat([ms, nr], axis=1)
            ms = temp.iloc[:, :len(ms.columns)].ffill()
            ms = ms[nr.notnull()]
            offFromMeas = nrOffs - ms
            beatDur = self._getBeatUnit()
            temp = pd.concat([beatDur, nr], axis=1)
            beatDur = temp.iloc[:, :len(beatDur.columns)].ffill()
            beatDur = beatDur[nr.notnull()]
            self.analyses['Beat'] = (offFromMeas / beatDur) + 1
        return self.analyses['Beat']

    def _getBeatIndex(self):
        '''
        Return a series of the first valid value in each row of .getBeat().
        '''
        if 'BeatIndex' not in self.analyses:
            ser = self.getBeat().dropna(how='all').apply(lambda row: row.dropna()[0], axis=1)
            self.analyses['BeatIndex'] = ser
        return self.analyses['BeatIndex']

    def detailIndex(self, df, measure=True, beat=True, offset=False, t_sig=False, progress=False, _all=False):
        '''
        Return the passed dataframe with a multi-index of any combination of the
        measure, beat, offset, prevailing time signature, and progress towards
        the end of the piece (0-1) in the index labels. At least one must be
        chosen, and the default is to have measure and beat information, but no
        other information. Pass offset=True to add offsets to index. You can 
        also pass _all=True to include all five types of index information.
        '''
        cols = [df]
        names = []
        if _all:
            measure, beat, offset, t_sig, progress = True, True, True, True, True
        if measure:
            cols.append(self.measures().iloc[:, 0])
            names.append('Measure')
        if beat:
            cols.append(self._getBeatIndex())
            names.append('Beat')
        if offset:
            cols.append(df.index.to_series())
            names.append('Offset')
        if t_sig:
            cols.append(self.timeSignatures().iloc[:, 0])
            names.append('TSig')
        if progress:
            prog = (df.index / self.notes().index[-1]).to_series()
            prog.index = df.index
            cols.append(prog)
            names.append('Progress')
        temp = pd.concat(cols, axis=1)
        temp2 = temp.iloc[:, len(df.columns):].ffill()
        if measure:
            temp2.iloc[:, 0] = temp2.iloc[:, 0].astype(int)
        mi = pd.MultiIndex.from_frame(temp2, names=names)
        ret = temp.iloc[:, :len(df.columns)]
        ret.index = mi
        ret.dropna(inplace=True, how='all')
        ret.sort_index(inplace=True)
        return ret

    def _beatStrengthHelper(self, noteOrRest):
        if hasattr(noteOrRest, 'beatStrength'):
            return noteOrRest.beatStrength
        return noteOrRest

    def beatStrengths(self):
        ''' Returns a table of the beat strengths of all the notes and rests in
        the piece. This follows the music21 conventions where the downbeat is
        equal to 1, and all other metric positions in a measure are given
        smaller numbers approaching zero as their metric weight decreases.
        Results from this method should not be sent to the regularize method.
        '''
        if 'BeatStrength' not in self.analyses:
            df = self._getM21ObjsNoTies().applymap(self._beatStrengthHelper)
            self.analyses['BeatStrength'] = df
        return self.analyses['BeatStrength']

    def getBeatStrength(self):
        return self.beatStrengths()

    def _getM21TSigObjs(self):
        if 'M21TSigObjs' not in self.analyses:
            tsigs = []
            for part in self._getSemiFlatParts():
                tsigs.append(pd.Series({ts.offset: ts for ts in part.getTimeSignatures()}))
            df = pd.concat(tsigs, axis=1)
            self.analyses['M21TSigObjs'] = df
        return self.analyses['M21TSigObjs']

    def timeSignatures(self):
        """
        Return a data frame containing the time signatures and their offsets.
        """
        if 'TimeSignature' not in self.analyses:
            df = self._getM21TSigObjs()
            df = df.applymap(lambda ts: ts.ratioString, na_action='ignore')
            df.columns = self._getPartNames()
            self.analyses['TimeSignature'] = df
        return self.analyses['TimeSignature']

    def getTimeSignature(self):
        return self.timeSignatures()

    def measures(self):
        """
        This method retrieves the offsets of each measure in each voices.
        """
        if "Measure" not in self.analyses:
            parts = self._getSemiFlatParts()
            partMeasures = []
            for part in parts:
                partMeasures.append(pd.Series({m.offset: m.measureNumber \
                    for m in part.getElementsByClass(['Measure'])}))
            df = pd.concat(partMeasures, axis=1)
            df.columns = self._getPartNames()
            self.analyses["Measure"] = df
        return self.analyses["Measure"]

    def getMeasure(self):
        return self.measures()

    def barlines(self):
        """
        This method retrieves some of the barlines. It's not clear how music21
        picks them, but this seems to get all the double barlines which helps
        detect section divisions.
        """
        if "Barline" not in self.analyses:
            parts = self._getSemiFlatParts()
            partBarlines = []
            for part in parts:
                partBarlines.append(pd.Series({b.offset: b.type \
                    for b in part.getElementsByClass(['Barline'])}))
            df = pd.concat(partBarlines, axis=1)
            df.columns = self._getPartNames()
            self.analyses["Barline"] = df
        return self.analyses["Barline"]

    def getBarline(self):
        return self.barlines()

    def soundingCount(self):
        """
        This would return a series with the number of parts that currently have
        a note sounding.
        """

        if not 'SoundingCount' in self.analyses:

            nr = self.notes().ffill()
            df = nr[nr != 'Rest']
            ser = df.count(axis=1)
            ser.name = 'Sounding'

            self.analyses['SoundingCount'] = ser

        return self.analyses['SoundingCount']

    def getSoundingCount(self):
        return self.soundingCount()
  
    def _zeroIndexIntervals(ntrvl):
        '''
        Change diatonic intervals so that they count the number of steps, i.e.
        unison = 0, second = 1, etc.
        '''
        if ntrvl == 'Rest':
            return ntrvl
        val = int(ntrvl)
        if val > 0:
            return str(val - 1)
        return str(val + 1)

    def _harmonicIntervalHelper(row):
        if hasattr(row[1], 'isRest') and hasattr(row[0], 'isRest'):
            if row[1].isRest or row[0].isRest:
                return 'Rest'
            elif row[1].isNote and row[0].isNote:
                return interval.Interval(row[0], row[1])
        return None

    def _melodicIntervalHelper(row):
        if hasattr(row[0], 'isRest'):
            if row[0].isRest:
                return 'Rest'
            elif row[0].isNote and hasattr(row[1], 'isNote') and row[1].isNote:
                return interval.Interval(row[1], row[0])
        return None

    def _melodifyPart(ser, end):
        ser.dropna(inplace=True)
        shifted = ser.shift(1) if end else ser.shift(-1)
        partDF = pd.concat([ser, shifted], axis=1)
        if end:
            res = partDF.apply(ImportedPiece._melodicIntervalHelper, axis=1).dropna()
        else:  # not a typo, this uses _harmonicIntervalHelper if end == False
            res = partDF.apply(ImportedPiece._harmonicIntervalHelper, axis=1).dropna()
        return res

    def _strToM21Obj(cell):
        '''Convert a df cell from a string to a music21 note or rest. NAs are ignored.'''
        if cell == 'Rest':
            return note.Rest()
        return note.Note(cell)

    def _getM21MelodicIntervals(self, end, df):
        key = 'M21MelodicIntervals' + 'End' if end else 'Start'
        if key not in self.analyses or df is not None:
            if df is None:
                m21Objs = self._getM21ObjsNoTies()
            else:
                m21Objs = df.applymap(ImportedPiece._strToM21Obj, na_action='ignore')
            _df = m21Objs.apply(ImportedPiece._melodifyPart, args=(end,))
            if df is not None:
                return _df
            self.analyses[key] = _df
        return self.analyses[key]

    def _getRegularM21MelodicIntervals(self, unit):
        m21Objs = self._getM21ObjsNoTies()
        m21Objs = self.regularize(m21Objs, unit=unit)
        return m21Objs.apply(ImportedPiece._melodifyPart)

    def _qualityDirectedCompound(cell):
        if hasattr(cell, 'direction'):
            if cell.direction.value >= 0:
                return cell.name
            else:
                return '-' + cell.name
        return cell

    def _qualityDirectedSimple(cell):
        if hasattr(cell, 'semiSimpleName'):
            if cell.direction.value > 0:
                return cell.semiSimpleName
            else:
                return '-' + cell.semiSimpleName
        return cell

    def _noQualityDirectedSimple(cell):
        if hasattr(cell, 'simpleName'):
            if cell.direction.value == -1:
                return '-' + cell.simpleName[1:]
            else:
                return cell.simpleName[1:]
        else:
            return cell

    def _noQualityDirectedSemiSimple(cell):
        if hasattr(cell, 'semiSimpleName'):
            if cell.direction.value == -1:
                return '-' + cell.semiSimpleName[1:]
            else:
                return cell.semiSimpleName[1:]
        else:
            return cell

    def _durationalRatioHelper(self, row):
        _row = row.dropna()
        return _row / _row.shift(1)

    def durationalRatios(self, df=None):
        '''
        Return durational ratios of each item in each column compared to the
        previous item in the same column. If a df is passed, it should be of
        float or integer values. If no df is passed, the default results from
        .durations will be used as input (durations of notes and rests).
        '''
        if df is None:
            df = self.durations()
        return df.apply(self._durationalRatioHelper).dropna(how='all')

    def getDurationalRatio(self, df=None):
        return self.durationalRatios(df)

    def distance(self, df=None, n=3):
        '''
        Return the distances between all the values in df which should be a
        dataframe of strings of integer ngrams. Specifically, this is meant for
        0-indexed, directed, and compound melodic ngrams. If nothing is passed
        for df, melodic ngrams of this type will be provided at the value of n
        passed. An alternative that would make sense would be to use chromatic
        melodic intervals instead.
        Usage:

        # Call like this:
        importedPiece.distance()

        # If you don't pass a value for df, you can specify a different value
        # for n to change from the default of 3:
        importedPiece.distance(n=5)

        # If you already have the melodic ngrams calculated for a different
        # aspect of your query, you can pass that as df to save a little
        # runtime on a large query. Note that if you pass something for df,
        # the n parameter will be ignored:
        mel = importedPiece.melodic('z', True, True)
        ngrams = importedPiece.ngrams(df=mel, n=4, exclude=['Rest'])
        importedPiece.distance(df=ngrams)

        # To search the table for the distances from a given pattern, just get
        # the column of that name. This is example looks for distances
        # involving a melodic pattern that goes up a step, down a third, up a
        # step, down a third:
        dist = importedPiece.distance(n=4)
        target = '1, -2, 1, -2'
        col = dist[target]

        # If you then want to filter that column, say to distances less than or
        # equal to 2, do this:
        col[col <= 2]
        '''
        if df is None:
            df = self.melodic('z', True, True)
            df = self.ngrams(df=df, n=n, exclude=['Rest'])
        uni = df.stack().unique()
        ser = pd.Series(uni)
        if isinstance(uni[0], str):
            df = pd.DataFrame.from_records(ser.apply(lambda cell: tuple(int(i) for i in cell.split(', '))))
        else:
            df = pd.DataFrame.from_records(ser.apply(lambda cell: tuple(int(i) for i in cell)))
        cols = [(df - df.loc[i]).abs().apply(sum, axis=1) for i in df.index]
        dist = pd.concat(cols, axis=1)
        dist.columns = uni
        dist.index = uni
        return dist

    def getDistance(self, df=None, n=3):
        return self.distance(df, n)

    def melodic(self, kind='q', directed=True, compound=True, unit=0, end=True, df=None):
        '''
        Return melodic intervals for all voice pairs. Each melodic interval
        is associated with the starting offset of the second note in the
        interval. To associate intervals with the offset of the first notes,
        pass end=False. If you want melodic intervals measured at a regular
        duration, do not pipe this method's result to the `regularize` method.
        Instead, pass the desired regular durational interval as an integer or
        float as the `unit` parameter.

        :param str kind: use "q" (default) for diatonic intervals with quality,
            "d" for diatonic intervals without quality, "z" for zero-indexed
            diatonic intervals without quality (i.e. unison = 0, second = 1,
            etc.), or "c" for chromatic intervals. Only the first character is
            used, and it's case insensitive.
        :param bool directed: defaults to True which shows that the voice that
            is lower on the staff is a higher pitch than the voice that is
            higher on the staff. This is desginated with a "-" prefix.
        :param bool compound: whether to use compound (True, default) or simple
            (False) intervals. In the case of simple diatonic intervals, it
            simplifies to within the octave, so octaves don't get simplified to
            unisons. But for semitonal intervals, an interval of an octave
            (12 semitones) would does get simplified to a unison (0).
        :param int/float unit: regular durational interval at which to measure
            melodic intervals. See the documentation of the `regularize` method
            for more about this.
        :param bool end: True (default) associates each melodic interval with
            the offset of the second note in the interval. Pass False to
            change this to the first note in each interval.
        :param pandas DataFrame df: None (default) is the standard behavior.
            Pass a df of note and rest strings to calculate the melodic interals
            in any dataframe. For example, if you want to find the melodic
            intervals between notes, but don't want to count repetitions of the
            same note as an interval, first run .notes(combineUnisons=True)
            then pass that result as the df parameter for .melodic. Results
            are not cached in this case.
        :returns: `pandas.DataFrame` of melodic intervals in each part
        '''
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, directed, compound)
        key = ('MelodicIntervals', kind, directed, compound, end)
        if key not in self.analyses or unit or df is not None:
            _df = self._getRegularM21MelodicIntervals(unit) if unit else self._getM21MelodicIntervals(end, df)
            _df = _df.applymap(self._intervalMethods[settings])
            if kind == 'z':
                _df = _df.applymap(ImportedPiece._zeroIndexIntervals, na_action='ignore')
            if unit or df is not None:
                return _df
            else:
                self.analyses[key] = _df
        return self.analyses[key]

    def getMelodic(self, kind='q', directed=True, compound=True, unit=0, end=True, df=None):
        return self.melodic(kind, directed, compound, unit, end, df)

    def _getM21HarmonicIntervals(self):
        if 'M21HarmonicIntervals' not in self.analyses:
            m21Objs = self._getM21ObjsNoTies()
            pairs = []
            combos = combinations(range(len(m21Objs.columns) - 1, -1, -1), 2)
            for combo in combos:
                df = m21Objs.iloc[:, list(combo)].dropna(how='all').ffill()
                ser = df.apply(ImportedPiece._harmonicIntervalHelper, axis=1)
                # name each column according to the voice names that make up the intervals, e.g. 'Bassus_Altus'
                ser.name = '_'.join((m21Objs.columns[combo[0]], m21Objs.columns[combo[1]]))
                pairs.append(ser)
            if pairs:
                ret = pd.concat(pairs, axis=1)
            else:
                ret = pd.DataFrame()
            self.analyses['M21HarmonicIntervals'] = ret
        return self.analyses['M21HarmonicIntervals']

    def harmonic(self, kind='q', directed=True, compound=True):
        '''
        Return harmonic intervals for all voice pairs. The voice pairs are
        named with the voice that's lower on the staff given first, and the two
        voices separated with an underscore, e.g. "Bassus_Tenor".

        :param str kind: use "q" (default) for diatonic intervals with quality,
            "d" for diatonic intervals without quality, "z" for zero-indexed
            diatonic intervals without quality (i.e. unison = 0, second = 1,
            etc.), or "c" for chromatic intervals. Only the first character is
            used, and it's case insensitive.
        :param bool directed: defaults to True which shows that the voice that
            is lower on the staff is a higher pitch than the voice that is
            higher on the staff. This is desginated with a "-" prefix.
        :param bool compound: whether to use compound (True, default) or simple
            (False) intervals. In the case of simple diatonic intervals, it
            simplifies to within the octave, so octaves don't get simplified to
            unisons. But for semitonal intervals, an interval of an octave
            (12 semitones) would does get simplified to a unison (0 semitones).
        '''
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, directed, compound)
        key = ('HarmonicIntervals', kind, directed, compound)
        if key not in self.analyses:
            df = self._getM21HarmonicIntervals()
            df = df.applymap(self._intervalMethods[settings])
            if kind == 'z':
                df = df.applymap(ImportedPiece._zeroIndexIntervals, na_action='ignore')
            self.analyses[key] = df
        return self.analyses[key]

    def getHarmonic(self, kind='q', directed=True, compound=True):
        return self.harmonic(kind, directed, compound)

    def _ngrams_offsets_helper(col, n, offsets):
        """
        Generate a list of series that align the notes from one ngrams according
        to the first or the last note's offset.
         :param pandas.Series col: A column that originally contains
         notes and rests.
         :param int n: The size of the ngram.
         :param str offsets: We could input 'first' if we want to group
         the ngrams by their first note's offset, or 'last' if we
         want to group the ngram by the last note's offset.
        :return pandas.Series: a list of shifted series that could be grouped by
        first or the last note's offset.
        """
        if offsets == 'first':
            chunks = [col.shift(-i) for i in range(n)]
        else:  # offsets == 'last':
            chunks = [col.shift(i) for i in range(n - 1, -1, -1)]
        return chunks

    def _ngramHelper(col, n, exclude, offsets):
        col.dropna(inplace=True)
        if n == -1:
            # get the starting and ending elements of ngrams
            starts = col[(col != 'Rest') & (col.shift(1).isin(('Rest', np.nan)))]
            ends = col[(col != 'Rest') & (col.shift(-1).isin(('Rest', np.nan)))]
            si = tuple(col.index.get_loc(i) for i in starts.index)
            ei = tuple(col.index.get_loc(i) + 1 for i in ends.index)
            ind = starts.index if offsets == 'first' else ends.index
            vals = [', '.join(col.iloc[si[i]: ei[i]]) for i in range(len(si))]
            ser = pd.Series(vals, name=col.name, index=ind)
            return ser

        chunks = ImportedPiece._ngrams_offsets_helper(col, n, offsets)
        chains = pd.concat(chunks, axis=1)
        for excl in exclude:
            chains = chains[(chains != excl).all(1)]
        chains.dropna(inplace=True)
        if col.dtype.name == 'str':
            chains = chains.apply(lambda row: ', '.join(row), axis=1)
        else:
            chains = chains.apply(tuple, axis=1)
        return chains

    def ngrams(self, df=None, n=3, how='columnwise', other=None, held='Held',
                  exclude=['Rest'], interval_settings=('d', True, True), unit=0,
                  offsets='first', clarify_rests=True):
        '''
        Group sequences of observations in a sliding window "n" events long
        (default n=3). If the `exclude` parameter is passed and any item in that
        list is found in an ngram, that ngram will be removed from the resulting
        DataFrame. Since `exclude` defaults to `['Rest']`, pass an empty list if
        you want to allow rests in your ngrams.

        There are two primary modes for this method. They were controlled by the
        `how` parameter, but this parameter is now deprecated and the mode is
        determined by what is or is not passed as the `df` and `other` parameters.
        When a dataframe is passed as `df` and nothing is given for `other`, this
        is the simple case where the events in each
        column of the `df` DataFrame are grouped at the offset of the first event
        in the window. For example, to get 4-grams of melodic intervals:

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.ngrams(df=ip.melodic(), n=4)

        For the "module" mode (interval successions) you must either pass dataframes
        to both `df` and `other`, or leave both as None (default). In
        this case, if the `df` or `other` parameters are left as None, they will
        be replaced with the current piece's harmonic and melodic intervals
        respectfully. These intervals will be formed according to the
        interval_settings argument, which gets passed to the getMelodic and
        getHarmonic methods (see those methods for an explanation of those
        settings). This makes it easy to make contrapuntal-module ngrams, e.g.:

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.ngrams()

        There is a special case for "open-ended" module ngrams. Set n=1 and the
        module ngrams will show the vertical interval between two voices,
        followed by the connecting melodic interal in the lower voice, but not
        the next harmonic interval. Open-ended module ngrams can be useful if
        you want to see how long the imitation in two voice parts goes on for.

        Another special case is when `n` is set to -1. This finds the longest
        ngrams at all time points excluding subset ngrams. The returned
        dataframe will have ngrams of length varying between 1 and the longest
        ngram in the piece.

        The `offset` setting can have two modes. If "first" is selected (default option),
        the returned ngrams will be grouped according to their first notes' offsets,
        while if "last" is selected, the returned ngrams will be grouped according
        to the last notes' offsets.

        If you want want "module" ngrams taken at a regular durational interval,
        you can omit passing `df` and `other` dataframes and instead pass the
        desired `interval_settings` and an integer or float for the `unit`
        parameter. See the `.regularize` documentation for how to use this
        parameter. Here's an example that will generate contrapuntal-module
        ngrams at regular minim (half-note) intervals.

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.ngrams(unit=2)

        Otherwise, you can give specific `df` and/or `other` DataFrames in which
        case the `interval_settings` parameter will be ignored. Also, you can
        use the `held` parameter to be used for when the lower voice sustains a
        note while the upper voice moves. This defaults to "Held" to distinguish
        between held notes and reiterated notes in the lower voice, but if this
        distinction is not wanted for your query, you may want to pass the way a
        unison gets labeled in your `other` DataFrame (e.g. "P1" or "1").

        The `clarify_rests` parameter controls whether the melodic motion of the 
        upper voice will be shown when the lower voice has a 'Rest' as its 
        melodic motion. This only applies to module ngrams. If True, the upper
        voice's melodic motions will appear after the lower voice's 'Rest' and
        after a '|' character, e.g. "3_Rest|2, Rest_Held, 5". This is needed for
        the detection of cadential voice function evasion by dropout.
        '''
        if df is not None and other is None:
            how = 'columnwise'
        elif (df is not None and other is not None) or (df is None and other is None):
            how = 'modules'
        if how == 'columnwise':
            return df.apply(ImportedPiece._ngramHelper, args=(n, exclude, offsets))
        if df is None:
            df = self.harmonic(*interval_settings)
            if unit:
                df = self.regularize(df, unit)
        if other is None:
            other = self.melodic(*interval_settings, unit=unit)
        cols = []
        other = other.fillna(held)
        for pair in df.columns:
            lowerVoice, upperVoice = pair.split('_')
            lowerMel = other[lowerVoice].copy()
            if clarify_rests and 'Rest' not in exclude:
                lowerMel[lowerMel == 'Rest'] += '|' + other[upperVoice]
            combo = pd.concat([lowerMel, df[pair]], axis=1)
            combo.dropna(subset=(pair,), inplace=True)
            combo.insert(loc=1, column='Joiner', value=', ')
            combo['_'] = '_'
            if n == -1:
                har = df[pair]
                starts = har[(har != 'Rest') & (har.shift(1).isin(('Rest', np.nan)))]
                ends = har[(har != 'Rest') & (har.shift(-1).isin(('Rest', np.nan)))]
                starts.dropna(inplace=True)
                ends.dropna(inplace=True)
                si = tuple(har.index.get_loc(i) for i in starts.index)
                ei = tuple(har.index.get_loc(i) + 1 for i in ends.index)
                col = [''.join([cell for row in combo.iloc[si[i]: ei[i]].values  # second loop
                                         for cell in row][2:-1])  # innermost loop
                       for i in range(len(si))]  # outermost loop
                col = pd.Series(col)
                if offsets == 'first':
                    col.index = starts.index
                else:
                    col.index = ends.index
            else:  # n >= 1
                lastIndex = -1
                if n == 1:
                    lastIndex = -3
                    n = 2
                combo = ImportedPiece._ngrams_offsets_helper(combo, n, offsets)
                combo = pd.concat(combo, axis=1)
                col = combo.iloc[:, 2:lastIndex].dropna().apply(lambda row: ''.join(row), axis=1)
                if exclude:
                    mask = col.apply(lambda cell: all([excl not in cell for excl in exclude]))
                    col = col[mask]
            col.name = pair
            cols.append(col)
        # in case piece has no harmony and cols stays empty
        if cols:
            return pd.concat(cols, axis=1)
        else:
            return pd.DataFrame()

    def getNgrams(self, df=None, n=3, how='columnwise', other=None, held='Held',
                  exclude=['Rest'], interval_settings=('d', True, True), unit=0,
                  offsets='first', clarify_rests=True):
        return self.ngrams(df=df, n=n, other=other, held=held, exclude=exclude,
            interval_settings=interval_settings, unit=unit, offsets=offsets,
            clarify_rests=clarify_rests)

    def _cvf_helper(self, row, df):
        '''
        Assign the cadential voice function of the lower and upper voices in
        each pair to their respective part name columns.'''
        df.loc[row.name, [row.LowerVoice, row.UpperVoice]] = (row.LowerCVF, row.UpperCVF)

    def _cvf_disambiguate_h(self, row):
        '''
        The 'h' label is used internally to help reduce the amount of false
        positives we get with unprepared 4ths. They are either removed or
        replaced with 'b' labels if they seem to be evaded bassizans cvfs.'''
        if 'h' in row.values:  # h is for potential evaded bassizans that gets confused with a chanson idiom
            if len(row.dropna()) > 2:
                row.replace('h', 'b', inplace=True)
            else:
                row.replace(('C', 'h'), np.nan, inplace=True)
        return row

    def _cvf_simplifier(self, row):
        '''
        Reduce the cadential voice function labels to only what is needed for
        classification. These changes are done on a copy of the cvf table, so
        they don't impact the cvf results. This just makes it simpler to write
        cadenceLabels.'''
        if 't' in row.values and 'T' in row.values:
            row = row.replace('t', np.nan)
        if 'B' in row.values or 'b' in row.values:
            row = row.replace(('t', 'T', 'u'), np.nan)
        return row

    def _lowest_pitch(self, row, m21):
        '''
        Return a column of the lowest pitch at each cadence. m21 is a df of
        music21 Note or Rest objects for the whole piece.'''
        filtered = [note for note in m21.asof(row.name) if note.isNote]
        return min(filtered).nameWithOctave

    def _cadential_pitch(self, row, nr):
        '''
        Return a column of the pitch cadenced to. This is considered to be the
        note the Cantizans cadences to, or if there is no Cantizans, the note
        the Altizans cadences to.'''
        if 'C' in row.values:
            return nr.at[row.name, row.index[np.where(row == 'C')[0][0]]][:-1]
        elif 'A' in row.values:
            return nr.at[row.name, row.index[np.where(row == 'A')[0][0]]][:-1]

    def cvfs(self, keep_keys=False):
        '''
        Return a dataframe of cadential voice functions in the piece. If
        `keep_keys` is set to True, the ngrams that triggered each CVF pair
        will be shown in additional columns in the table.

        Each CVF is represented with a single-character label as follows:

        "C": cantizans motion up a step (can also be ornamented e.g. Landini)
        "T": tenorizans motion down a step (can be ornamented with anticipations)
        "B": bassizans motion up a fourth or down a fifth
        "A": altizans motion, similar to cantizans, but cadences to a fifth
            above a tenorizans instead of an octave
        "L": leaping contratenor motion up an octave at the perfection
        "P": plagal bassizans motion up a fifth or down a fourth
        "Q": quintizans, like a tenorizans, but resolves down by fifth or up by
            fourth to a fourth below the goal tone of the cantizans
        "S": sestizans, occurring in some thicker 16th centurytextures, this is
            where the agent against the cantizans is already the cantizan's note
            of resolution (often results in a simultaneous false relation); the
            melodic motion is down by third at the moment of perfection

        "c": evaded cantizans when it moves to an unexpected note at the perfection
        "t": evaded tenorizans when it goes up by step at the perfection
        "b": evaded bassizans when it goes up by step at the perfection
        "u": evaded bassizans when it goes down by third at the perfection
        (there are no evaded labels for the altizans, plagal bassizans leaping
        contratenor CVFs)
        "s": evaded sestizans when it resolves down by second

        "x": evaded bassizans motion where the voice drops out at the perfection
        "y": evaded cantizans motion where the voice drops out at the perfection
        "z": evaded tenorizans motion where the voice drops out at the perfection

        The way these CVFs combine determines which cadence labels are assigned
        when return_type='cadences'.
        '''
        if not keep_keys and 'CVF' in self.analyses:
            return self.analyses['CVF']
        cadences = pd.read_csv(cwd+'/data/cadences/CVFLabels.csv', index_col='Ngram')
        cadences['N'] = cadences.index.map(lambda i: i.count(', ') + 1)
        ngrams = {n: self.ngrams(how='modules', interval_settings=('d', True, False),
                                    n=n, offsets='last', exclude=[]).stack()
                  for n in cadences.N.unique()}
        hits = [df[df.isin(cadences[cadences.N == n].index)] for n, df in ngrams.items()]
        hits = pd.concat(hits)
        hits.sort_index(level=0, inplace=True)
        hits = hits[~hits.index.duplicated('last')]
        if keep_keys:
            ngramKeys = hits.unstack(level=1)
        hits.name = 'Ngram'
        df = pd.DataFrame(hits)
        df = df.join(cadences, on='Ngram')
        voices = [pair.split('_') for pair in df.index.get_level_values(1)]
        df[['LowerVoice', 'UpperVoice']] = voices
        df.index = df.index.get_level_values(0)
        df.index.names = ('Offset',)
        cvfs = pd.DataFrame(columns=self._getPartNames())
        df.apply(func=self._cvf_helper, axis=1, args=(cvfs,))
        mel = self.melodic('c', True, True)
        mel = mel[cvfs.notnull()].dropna(how='all')
        cvfs = cvfs.apply(self._cvf_disambiguate_h, axis=1).dropna(how='all')
        cvfs = cvfs.astype('object', copy=False)
        cvfs[(cvfs == 'x') & mel.isin(('5', '-7'))] = 'B'
        cvfs[(cvfs == 'y') & mel.isin(('1', '2'))] = 'C'
        cvfs[(cvfs == 'z') & mel.isin(('-1', '-2'))] = 'T'
        self.analyses['CVF'] = cvfs
        if keep_keys:
            cvfs = pd.concat([cvfs, ngramKeys], axis=1)
        return cvfs

    def cadences(self, keep_keys=False):
        '''
        Return a dataframe of cadences in the piece along with metadata about
        these cadence points such as the lowest pitch at moment of cadence, and 
        the cadential goal tone is returned. The SinceLast and ToNext columns
        are the time in quarter notes since the last or to the next cadence. The
        first cadence's SinceLast time and the last cadence's ToNext time are
        the time since/to the beginning/end of the piece. The "Low" and "Tone"
        columns give the pitches of the lowest sounding pitch at the perfection,
        and the goal tone of the cantizans (or altizans if there is no cantizans)
        respectively. These are usually the same pitch class, but not always.
        "Rel" is short for relative, so "RelLow" is the lowest pitch of each
        cadence shown as an interval measured against the last pitch in the
        "Low" column. Likewise, "RelTone" is the cadential tone shown as an
        interval measured against the last pitch in the "Tone" column. If
        `keep_keys` is set to True, the "Key" column will be kept in the cadence
        results table. This corresponds to the combination of cadential voice
        functions and chromatic intervals used as a key to lookup the cadence
        information in the cadenceLabels.csv file. The "Progress" column gives
        the progress toward the end of the piece measured 0-1 where 1 is the 
        time point of the last attack in the piece.        
        '''
        if 'Cadences' in self.analyses:
            if keep_keys:
                return self.analyses['Cadences']
            else:
                return self.analyses['Cadences'].drop('Key', axis=1)

        cvfs = self.cvfs()
        mel = self.melodic('c', True, True)
        mel = mel[cvfs.notnull()].dropna(how='all')
        _cvfs = cvfs.apply(self._cvf_simplifier, axis=1)
        _cvfs.replace(['Q', 's', 'S'], np.nan, inplace=True)
        mel = mel[_cvfs.isin(list('ACTctu'))].reindex_like(_cvfs).fillna('')
        cadKeys = _cvfs + mel
        keys = cadKeys.apply(lambda row: ''.join(row.dropna().sort_values().unique()), axis=1)
        keys.name = 'Key'
        keys = pd.DataFrame(keys)
        cadDict = pd.read_csv(cwd + '/data/cadences/cadenceLabels.csv', index_col=0)
        labels = keys.join(cadDict, on='Key')
        m21 = self._getM21ObjsNoTies().ffill()
        labels['Low'] = labels.apply(self._lowest_pitch, args=(m21,), axis=1)
        final = note.Note(labels.Low.dropna().iat[-1])  # lowest pitch of last cadence
        labels['RelLow'] = labels.Low.apply(lambda x: ImportedPiece._qualityDirectedCompound(interval.Interval(final, note.Note(x))))
        nr = self.notes()
        labels['Tone'] = cvfs.apply(self._cadential_pitch, args=(nr,), axis=1)
        lastTone = note.Note(labels.Tone.dropna().iat[-1])  # last pitch cadenced to
        labels['RelTone'] = labels.Tone.apply(lambda x: ImportedPiece._qualityDirectedCompound(interval.Interval(lastTone, note.Note(x))))
        labels.RelTone = labels.RelTone[labels.Tone.notnull()]
        labels.Tone = labels.Tone.fillna(np.nan)
        tsig = self.timeSignatures().iloc[:, 0]
        tsig.name = 'TSig'
        temp = pd.concat([labels, tsig], axis=1)
        temp['TSig'].ffill(inplace=True)
        labels = temp.loc[labels.index, :]
        labels['Measure'] = self.measures().iloc[:, 0].asof(labels.index).astype(int)
        beat = self.getBeat().loc[labels.index, :]
        labels['Beat'] = beat.bfill(axis=1).iloc[:, 0]
        labels['Progress'] = labels.index / nr.index[-1]
        ndx = labels.index.to_series()
        labels['SinceLast'] = ndx - ndx.shift(1)
        labels.iat[0, -1] = labels.index[0]
        labels['ToNext'] = labels['SinceLast'].shift(-1)
        labels.iat[-1, -1] = self.score.highestTime - labels.index[-1]
        self.analyses['Cadences'] = labels
        if not keep_keys:
            labels = labels.drop('Key', axis=1)
        return labels

    def classifyCadences(self, return_type='cadences', keep_keys=False):
        '''This method has been deprecated. Please use .cvfs() for cadential
        voice function analysis or .cadences() for cadential analysis. In both cases,
        you no longer need the `return_type` parameter and should not pass it.
        The `keep_keys` parameter works the same in those two functions.'''
        print(self.classifyCadences.__doc__)
        if return_type[0].lower() == 'f':
            return self.cvfs(keep_keys=keep_keys)
        else:
            return self.cadences(keep_keys=keep_keys)

    def _alpha_only(value):
        """This helper function is used by HR classifier.  It removes non-alphanumberic characters from lyrics
        """
        if isinstance(value, str):
            return re.sub(r'[^a-zA-Z]', '', value)
        else:
            return value

    def homorhythm(self):
        """This function predicts homorhythmic passages in a given piece.
        The method follows various stages:

        gets durational ngrams, and finds passages in which these are the same in more than two voices at a given offsets
        gets syllables at every offset, and identifies passages where more than two voices are singing the same lyrics_hr
        checks the number of active voices (thus eliminating places where some voices have rests)
        """
        nr = self.notes()
        dur = self.durations(df=nr)
        ng = self.ngrams(df=dur, n=2)
        dur_ngrams = []

        # find passages with more than 2 active voices
        for index, rows in ng.iterrows():

            dur_ngrams_no_nan = [x for x in rows if pd.isnull(x) == False]
            dur_ngrams.append(dur_ngrams_no_nan)

        ng['dur_ngrams'] = dur_ngrams
        # ng['rest_count'] = rests
        ng['active_voices'] = ng['dur_ngrams'].apply(len)
        ng['number_dur_ngrams'] = ng['dur_ngrams'].apply(set).apply(len)
        ng = ng[(ng['number_dur_ngrams'] <2) & (ng['active_voices'] > 2)]

        # check rests in multiple parts
        nr.ffill(inplace=True)
        index_of_rests = []
        rests = []
        for index, rows in nr.iterrows():
            rest_test = [y for y in rows if y == "Rest"]
            rests.append(rest_test)

        #     index_of_rests.append(index)
        nr["rests"] = rests
        nr["rests_count"] = nr["rests"].apply(len)
        full_stop = nr[(nr['rests_count'] > 1) ]
        rests_with_mb = self.detailIndex(full_stop)
        # now get lyric syllables
        lyrics = self.lyrics()
        lyrics = lyrics.applymap(ImportedPiece._alpha_only)
        cols = lyrics.columns
        for col in cols:
            lyrics[col] = lyrics[col].str.lower()
        syll_set = []
        for index2, rows2 in lyrics.iterrows():
            syll_no_nan = [z for z in rows2 if pd.isnull(z) == False]
            syll_set.append(syll_no_nan)
        #     print(syll_no_nan)
        lyrics['syllable_set'] = syll_set

        # create mask consisting of passages with more than two voices actively singing same syllables
        lyrics['active_syll_voices'] = lyrics['syllable_set'].apply(len)
        # count how _many_ syllables at this offset
        lyrics['number_sylls'] = lyrics['syllable_set'].apply(set).apply(len)
        # get count of possible hr passages (several voices with same syllable)
        lyrics_hr = lyrics[(lyrics['active_syll_voices'] > 2) & (lyrics['number_sylls'] < 2)]
        # self.detailIndex(lyrics_hr, offset=True)
        # lyrics['is_hr'] = np.where(lyrics['active_voices'] > 3)
        hr_sylls_mask = lyrics_hr["active_syll_voices"]

        # combine results to show passages where more than 2 voices have the same syllables and durations
        ng = ng[['active_voices', "number_dur_ngrams"]]
        hr = pd.merge(ng, hr_sylls_mask, left_index=True, right_index=True)
        result = self.detailIndex(hr, offset=True)
        return result


    def _entryHelper(self, col):
        """Return True for cells in column that correspond to notes that either
        begin a piece, or immediately preceded by a rest or a double barline."""
        barlines = self.barlines()[col.name]
        _col = col.dropna()
        shifted = _col.shift().fillna('Rest')
        mask = ((_col != 'Rest') & ((shifted == 'Rest') | (barlines == 'double')))
        return mask

    def entryMask(self):
        """Return a dataframe of True, False, or NaN values which can be used as
        a mask (filter). When applied to another dataframe, only the True cells
        in the mask will be kept. Usage:
        piece = importScore('path_to_piece')
        mask = piece.entryMask()
        df = piece.notes()
        df[mask].dropna(how='all')
        """
        nr = self.notes()
        mask = nr.apply(self._entryHelper)
        return mask

    def getEntryMask(self):
        return self.entryMask()

    def entries(self, df=None, n=None):
        """Return a filtered copy of the passed df that only keeps the events in
        that df if they either start a piece or come after a silence. If the df
        parameter is left as None, it will be replaced with the default melodic
        interval results, though with end=False since this is needed specifically
        for this use case.
        In these cases, the offset of each melodic entry is the starting offset of
        the first note in the melody. If you want melodies 4 notes long, for
        example, note that this would be n=3, because four consecutive notes are
        constitute 3 melodic intervals.
        If the n parameter is not None, then the default melodic interval results
        or passed df argument will be replaced with n-long ngrams of those events.
        Note that this does not currently work for dataframes where the columns
        are combinations of voices, e.g. harmonic intervals.
        """
        if df is None:
            df = self.melodic(end=False)
        if n is not None:
            df = self.ngrams(df, n)
        mask = self.entryMask()
        return df[mask].dropna(how='all')

    def getEntries(self, df=None, n=None):
        return self.entries(df, n)

    def _find_entry_int_distance(self, coordinates):
        """This helper function is used as part of classify_entries_as_presentation_types.
        This function finds the melodic intervals between the first notes of
        successive entries in a given presentation type.
        They are represented as intervals with quality and direction, thus P-4, m3, P5, P5, M-9, P-4, P4
        """

        tone_list = []

        all_tones = self.notes()

        for item in coordinates:
            filtered_tones = all_tones.loc[item]
            tone_list.append(filtered_tones)

        noteObjects = [note.Note(tone) for tone in tone_list]
        _ints = [interval.Interval(noteObjects[i], noteObjects[i + 1]) for i in range(len(noteObjects) - 1)]
        entry_ints = []

        for _int in _ints:
            entry_ints.append(_int.directedName)

        return entry_ints

    def _split_by_threshold(seq, max_diff=70):
        """This helper function is used as part of classify_entries_as_presentation_types.
        This function finds gaps between sequences of matching melodic entries.
        The threshold is set to 70 offsets by default--under about 10 measures.
        """
        it = iter(seq)
        last = next(it)
        part = [last]

        for curr in it:
            if curr - last > max_diff:
                yield part
                part = []

            part.append(curr)
            last = curr
            # print(part)

        yield part

    def _classify_by_offset(offset_diffs):
        """This helper function is used as part of classify_entries_as_presentation_types.
        This function predicts the Presentation Types. It relies of the differences between
        the first offsets of successive melodic entries.

        If the offset differences are identical:  PEN
        If the odd-numbered offset differences are identical:  ID, since these represent
        situations in which the entries 1-2 have the same offset difference as entries 3-4
        If the offset differences are all different:  FUGA
        """
        alt_list = offset_diffs[::2]

        if len(set(offset_diffs)) == 1 and len(offset_diffs) > 1:
            return 'PEN'
        # elif (len(offset_difference_list) %2 != 0) and (len(set(alt_list)) == 1):
        elif (len(offset_diffs) % 2 != 0) and (len(set(alt_list)) == 1) and (len(offset_diffs) >= 3):
            return 'ID'
        elif len(offset_diffs) >= 1:
            return 'FUGA'

    def _temp_dict_of_details(self, slist, entry_array, det, matches):
        """This helper function is used as part of classify_entries_as_presentation_types.
        This function assembles various features for the presentation types
        into a single temporary dictionary, which in turn is appended to the dataframe of 'points'
        """

        array = entry_array[entry_array.index.get_level_values(0).isin(slist)]
        short_offset_list = array.index.to_list()
        time_ints = np.diff(array.index).tolist()
        voice_list = array['voice'].to_list()
        tone_coordinates =  list(zip(short_offset_list, voice_list))
        mel_ints = self._find_entry_int_distance(tone_coordinates)
        first_offset = short_offset_list[0]
        meas_beat = det[det.index.get_level_values('Offset').isin(short_offset_list)]
        mb2 = meas_beat.reset_index()
        mb2['mb'] = mb2["Measure"].astype(str) + "/" + mb2["Beat"].astype(str)
        meas_beat_list = mb2['mb'].to_list()

        # temp results for this set
        temp = {"Composer": self.metadata["composer"],
                "Title": self.metadata["title"],
                'First_Offset': first_offset,
                'Offsets': short_offset_list,
                'Measures_Beats': meas_beat_list,
                "Soggetti": matches,
                'Voices': voice_list,
                'Time_Entry_Intervals': time_ints,
                'Melodic_Entry_Intervals': mel_ints}
        return temp

    # #  the following are used to turn the offset diffs and melodic entry intervals
    # # and melodies into strings for the network
    def _offset_joiner(a):
        b = '_'.join(map(str, a))
        return b

    def presentationTypes(self, melodic_ngram_length=4, limit_to_entries=True,
                          edit_distance_threshold=1, include_hidden_types=False,
                          combine_unisons=False):
        """This function uses several other functions to classify the entries in a given piece.
        The output is a list, in order of offset, of each presentation type, including information about
        measures/beats
        starting offset
        soggetti involved
        melodic intervals of entry
        time intervals of entry

        set the length of the soggetti with `melodic_ngram_length`
        set the maximum difference between similar soggetti with `edit_distance_threshold`
        for chromatic vs diatonic, compound, and directed data in soggetti, see `interval_settings`
        to include all the hidden PENs and IDS (those found within longer Fugas),
        use `include_hidden_types == True`.
        For faster (and simpler) listing of points of imitation without hidden forms, use `include_hidden_types == False`

        Example:
        piece = importScore('url')
        piece.presentationTypes(edit_distance_threshold=2)
        """
        nr = self.notes(combineUnisons=combine_unisons)
        mel = self.melodic(df=nr, kind='d', end=False)
        mel_ng = self.ngrams(df=mel, n=melodic_ngram_length)
        if limit_to_entries:
            entries = self.entries(mel_ng)
        else:
            entries = self.ngrams(df=mel, n=melodic_ngram_length)
        
        # entries = self.entries(df=mel_ng, n=n)
        # Classifier with Functions
        points = pd.DataFrame(columns=['Composer',
                    'Title',
                    'First_Offset',
                    'Measures_Beats',
                    'Melodic_Entry_Intervals',
                    'Offsets',
                    'Soggetti',
                    'Time_Entry_Intervals',
                    'Voices',
                    'Presentation_Type'])
        points2 = pd.DataFrame()

        col_order = list(points.columns) + ['Number_Entries', 'Flexed_Entries']

        det = self.detailIndex(nr, offset=True)

        # ngrams of melodic entries
        # for chromatic, use:
        # self.getMelodicEntries(interval_settings=('c', True, True), n=5)
        #mel_ng = self.getMelodicEntries(interval_settings=('c', True, True), n=5)
        mels_stacked = entries.stack().to_frame()
        mels_stacked.rename(columns =  {0:"pattern"}, inplace = True)

        # edit distance, based on side-by-side comparison of melodic ngrams
        # gets flexed and other similar soggetti
        dist = self.distance(entries)
        dist_stack = dist.stack().to_frame()

        # filter distances to threshold.  <2 is good
        distance_factor = edit_distance_threshold + 1
        filtered_dist_stack = dist_stack[dist_stack[0] < distance_factor]
        filtered_dist = filtered_dist_stack.reset_index()
        filtered_dist.rename(columns =  {'level_0':"source", 'level_1':'match'}, inplace = True)

        # Group the filtered distanced patterns
        full_list_of_matches = filtered_dist.groupby('source')['match'].apply(list).reset_index()

        if include_hidden_types == False:
            for matches in full_list_of_matches["match"]:
                related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
                entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})
                offset_list = entry_array.index.to_list()
                split_list = list(ImportedPiece._split_by_threshold(offset_list))
                for item in split_list:
                # here is the list of starting offsets of the original set of entries:  slist
                    temp = self._temp_dict_of_details(item, entry_array, det, matches)
                    points = points.append(temp, ignore_index=True)
                    points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                    # points.drop_duplicates(subset=["First_Offset"], keep='first', inplace = True)
                    points = points[points['Offsets'].apply(len) > 1]

            points["Offsets_Key"] = points["Offsets"].apply(ImportedPiece._offset_joiner)
            points.drop_duplicates(subset=["Offsets_Key"], keep='first', inplace=True)
            points['Flexed_Entries'] = points["Soggetti"].apply(len) > 1
            points["Number_Entries"] = points["Offsets"].apply(len)
            points = points.reindex(columns=col_order).sort_values("First_Offset").reset_index(drop=True)
            return points

        elif include_hidden_types == True:
            hidden_types_list = ["PEN", "ID"]
            for matches in full_list_of_matches["match"]:
                related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
                entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})
                offset_list = entry_array.index.to_list()
                split_list = list(ImportedPiece._split_by_threshold(offset_list))
                for item in split_list:
                # here is the list of starting offsets of the original set of entries:  slist
                    temp = self._temp_dict_of_details(item, entry_array, det, matches)
                    points = points.append(temp, ignore_index=True)
                    points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                    # points.drop_duplicates(subset=["First_Offset"], keep='first', inplace = True)
                    points = points[points['Offsets'].apply(len) > 1]
            # return(points)

                for item in split_list:
                    # here is the list of starting offsets of the original set of entries:  slist
                    temp = self._temp_dict_of_details(item, entry_array, det, matches)
                    lto = len(temp["Offsets"])
                    if lto > 2 :
                        for r in range(3, 6):
                            list_combinations = list(combinations(item, r))
                            for slist in list_combinations:
                                temp = self._temp_dict_of_details(slist, entry_array, det, matches)
                                temp["Presentation_Type"] = ImportedPiece._classify_by_offset(temp['Time_Entry_Intervals'])
                                # print(temp)
                                if 'PEN' in temp["Presentation_Type"]:
                                    points2 = points2.append(temp, ignore_index=True)
                                if 'ID' in temp["Presentation_Type"]:
                                    points2 = points2.append(temp, ignore_index=True)

            # points2 = points2[points2["Presentation_Type"].isin(hidden_types_list)]
            # return(points2)
            points_combined = points.append(points2, ignore_index=True)
            points_combined["Offsets_Key"] = points_combined["Offsets"].apply(ImportedPiece._offset_joiner)
            points_combined.drop_duplicates(subset=["Offsets_Key"], keep='first', inplace=True)
            points_combined['Flexed_Entries'] = points_combined["Soggetti"].apply(len) > 1
            points_combined["Number_Entries"] = points_combined["Offsets"].apply(len)
            # points_combined = points_combined.sort_values("First_Offset").reset_index(drop=True)
            points_combined = points_combined.reindex(columns=col_order).sort_values("First_Offset").reset_index(drop=True)
            return points_combined

def classify_entries_as_presentation_types(piece, nr, mel_ng, entries, edit_distance_threshold, include_hidden_types):

    """This function uses several other functions to classify the entries in a given piece.
    The output is a list, in order of offset, of each presentation type, including information about
    measures/beats
    starting offset
    soggetti involved
    melodic intervals of entry
    time intervals of entry
    set the length of the soggetti with `melodic_ngram_length`
    set the maximum difference between similar soggetti with `edit_distance_threshold`
    for chromatic vs diatonic, compound, and directed data in soggetti, see `interval_settings`
    to include all the hidden PENs and IDS (those found within longer Fugas),
    use `include_hidden_types == True`.
    For faster (and simpler) listing of points of imitation without hidden forms, use `include_hidden_types == False`
    """
    # Classifier with Functions
    points = pd.DataFrame(columns=['Composer',
                 'Title',
                 'First_Offset',
                 'Measures_Beats',
                 'Melodic_Entry_Intervals',
                 'Offsets',
                 'Soggetti',
                 'Time_Entry_Intervals',
                 'Voices',
                 'Presentation_Type'])
    points2 = pd.DataFrame()

    # new_offset_list = []
#     nr = piece.notes()
    det = piece.detailIndex(nr, offset=True)

    # The following are now all set in the Notebook as argument
    # durations and ngrams of durations
    # dur = piece.durations(df=nr)
    # dur_ng = piece.ngrams(df=dur, n=3)

    # ngrams of melodic entries
    # for chromatic, use:
    # piece.getMelodicEntries(interval_settings=('c', True, True), n=5)
    #mel_ng = piece.getMelodicEntries(interval_settings=('c', True, True), n=5)
    mels_stacked = entries.stack().to_frame()
    mels_stacked.rename(columns =  {0:"pattern"}, inplace = True)

    # edit distance, based on side-by-side comparison of melodic ngrams
    # gets flexed and other similar soggetti
    dist = piece.distance(entries)
    dist_stack = dist.stack().to_frame()


    # filter distances to threshold.  <2 is good
    distance_factor = edit_distance_threshold + 1
    filtered_dist_stack = dist_stack[dist_stack[0] < distance_factor]
    filtered_dist = filtered_dist_stack.reset_index()
    filtered_dist.rename(columns =  {'level_0':"source", 'level_1':'match'}, inplace = True)

    # Group the filtered distanced patterns
    full_list_of_matches = filtered_dist.groupby('source')['match'].apply(list).reset_index()

    if include_hidden_types == False:

        for matches in full_list_of_matches["match"]:
            related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
            entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})
            offset_list = entry_array.index.to_list()
            split_list = list(split_by_threshold(offset_list))
            for item in split_list:
            # here is the list of starting offsets of the original set of entries:  slist

                temp = temp_dict_of_details(item, entry_array, det, matches, piece)


                points = points.append(temp, ignore_index=True)
                points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                # points.drop_duplicates(subset=["First_Offset"], keep='first', inplace = True)
                points = points[points['Offsets'].apply(len) > 1]

        points["Offsets_Key"] = points["Offsets"].apply(offset_joiner)
        points.drop_duplicates(subset=["Offsets_Key"], keep='first', inplace = True)
        points['Flexed_Entries'] = points["Soggetti"].apply(len) > 1
        points["Number_Entries"] = points["Offsets"].apply(len)
        col_order = ['Composer',
                 'Title',
                 'First_Offset',
                 'Measures_Beats',
                 'Melodic_Entry_Intervals',
                 'Offsets',
                 'Soggetti',
                 'Time_Entry_Intervals',
                 'Voices',
                 'Presentation_Type',
                  'Number_Entries',
                'Flexed_Entries']
        points = points.reindex(columns=col_order).sort_values("First_Offset").reset_index(drop=True)
        return points

    elif include_hidden_types == True:
        hidden_types_list = ["PEN", "ID"]

        for matches in full_list_of_matches["match"]:
            related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
            entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})
            offset_list = entry_array.index.to_list()
            split_list = list(split_by_threshold(offset_list))
            for item in split_list:
            # here is the list of starting offsets of the original set of entries:  slist

                temp = temp_dict_of_details(item, entry_array, det, matches, piece)


                points = points.append(temp, ignore_index=True)
                points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                # points.drop_duplicates(subset=["First_Offset"], keep='first', inplace = True)
                points = points[points['Offsets'].apply(len) > 1]
        # return(points)


            for item in split_list:
    # #         # here is the list of starting offsets of the original set of entries:  slist

                temp = temp_dict_of_details(item, entry_array, det, matches, piece)
                lto = len(temp["Offsets"])
                if lto > 2 :
                    for r in range(3, 6):
                        list_combinations = list(combinations(item, r))
                        for slist in list_combinations:

                            temp = temp_dict_of_details(slist, entry_array, det, matches, piece)

                            temp["Presentation_Type"] = ImportedPiece._classify_by_offset(temp['Time_Entry_Intervals'])
                            # print(temp)

                            if 'PEN' in temp["Presentation_Type"]:
                                points2 = points2.append(temp, ignore_index=True)
                            if 'ID' in temp["Presentation_Type"]:
                                points2 = points2.append(temp, ignore_index=True)




        # points2 = points2[points2["Presentation_Type"].isin(hidden_types_list)]
        # return(points2)


        points_combined = points.append(points2, ignore_index=True)
        points_combined["Offsets_Key"] = points_combined["Offsets"].apply(offset_joiner)
        points_combined.drop_duplicates(subset=["Offsets_Key"], keep='first', inplace = True)
        points_combined['Flexed_Entries'] = points_combined["Soggetti"].apply(len) > 1
        points_combined["Number_Entries"] = points_combined["Offsets"].apply(len)
        col_order = ['Composer',
                 'Title',
                 'First_Offset',
                 'Measures_Beats',
                 'Melodic_Entry_Intervals',
                 'Offsets',
                 'Soggetti',
                 'Time_Entry_Intervals',
                 'Voices',
                 'Presentation_Type',
                  'Number_Entries',
                'Flexed_Entries']
        # points_combined = points_combined.sort_values("First_Offset").reset_index(drop=True)
        points_combined = points_combined.reindex(columns=col_order).sort_values("First_Offset").reset_index(drop=True)
        return points_combined

def joiner(a):
    """This gets used for visualization routines."""
    b = '_'.join(map(str, a))
    return b
def clean_melody_new(c):
    """This gets used for visualization routines."""
    first_soggetto = list(c[0])
    soggetto_as_word = ImportedPiece._joiner(first_soggetto)
    return soggetto_as_word

#  HR classifier
def find_hr(piece):

    """This function predicts homorhythmic passages in a given piece.
    The method follows various stages:

    gets durational ngrams, and finds passages in which these are the same in more than two voices at a given offsets
    gets syllables at every offset, and identifies passages where more than two voices are singing the same lyrics_hr
    checks the number of active voices (thus eliminating places where some voices have rests)

    """
    return piece.homorhythm()

# For mass file uploads, only compatible for whole piece analysis, more specific tuning to come
class CorpusBase:
    # Need to consider whether users can input certain scores (which means needing urls selected too), or just to do all in the corpus automatically
    """
    A class for importing multiple scores at once

    Attributes
    ----------
    paths : list
        list of file paths and urls of scores to be imported
        file paths MUST begin with a '/', otherwise they will be categoried as urls
    scores : list of music21.Score
        list of music21.Score objects- imported from urls and paths
    note_list : list of NoteListElement
        list of notes constructed from scores
    note_list_no_unisons : list of NoteListElement
        list of notes constructed from scores, combining unisons
    """

    def __init__(self, paths: list):
        """
        Parameters
        ----------
        paths : list
            list file paths/urls to mei files
            file paths MUST begin with a '/', otherwise they will be categoried as urls

        Raises
        ----------
        Exception
            If at least one score isn't succesfully imported, raises error
        """
        self.paths = paths
        self.scores = []  # store lists of ImportedPieces generated from the path above
        for path in paths:
            _score = importScore(path)
            if _score is not None:
                self.scores.append(_score)

        if len(self.scores) == 0:
            raise Exception("At least one score must be succesfully imported")

        self.note_list = self.note_list_whole_piece()
        self.no_unisons = self.note_list_no_unisons()

    def batch(self, func, kwargs={}, metadata=True):
        '''
        Run the `func` on each of the scores in this CorpusBase object and
        return a list of the results. `func` should be a method from the
        ImportedPiece class. If you need to pass arguments to that function,
        pass them as a dictionary of keyword arguments with the kwargs
        parameter. These parameters will be the same for each ImportedPiece
        object as it gets the `func` applied to its score.

        # Example of basic analysis with no added parameters:
        corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])
        func = ImportedPiece.notes  # <- NB there are no parentheses here
        list_of_dfs = corpus.batch(func)

        # Example passing some parameters to `func` calls. Note that you only add
        # the parameters to kwargs that you need to pass. This example returns a
        # list of dataframes of the melodic intervals of each piece in the corpus,
        # and in this case will be chromatic and undirected intervals because of
        # parameters passed in kwargs.
        corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])
        func = ImportedPiece.melodic  # <- NB there are no parentheses here
        kwargs = {'kind': 'c', 'directed': False}
        list_of_dfs = corpus.batch(func, kwargs)

        # Example using batch to count the cadence types from multiple pieces:
        corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])
        list_of_dfs = corpus.batch(ImportedPiece.cadences, metadata=False)
        combined_df = pd.concat(list_of_dfs, ignore_index=True)
        # Get the number of each type of cadence observed:
        cadTypeCounts = combined_df['CadType'].value_counts()
        # Get the number of cadences per Beat level:
        cadTypeCounts = combined_df['Beat'].value_counts()

        When passing on a parameter that is a dataframe, a different dataframe
        is needed for each piece in the corpus. This applies to the parameters
        called "df", "mask_df", and "other". In these cases you should pass a
        list of dataframes in batch's kwargs for that parameter. This makes it
        easy to chain uses of the .batch method.

        # Example using .batch to first get the melodic intervals of each piece
        # in a corpus, and then pass that list of dataframes on to get melodic
        # ngrams for each piece:

        corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])
        func1 = ImportedPiece.melodic
        # NB: you would probably want to set metadata to False for most preliminary results
        list_of_dfs = corpus.batch(func=func1, kwargs={'end': False}, metadata=False)
        func2 = ImportedPiece.ngrams
        list_of_melodic_ngrams = corpus.batch(func=func2, kwargs={'n': 4, 'df': list_of_dfs})
        '''
        post = []
        dfs = ('df', 'mask_df', 'other')
        _kwargs = {key: val for key, val in kwargs.items() if key not in dfs}
        list_args = {key: val for key, val in kwargs.items() if key in dfs}
        for i, score in enumerate(self.scores):
            largs = {key: val[i] for key, val in list_args.items()}
            df = func(score, **_kwargs, **largs)
            if isinstance(df, pd.DataFrame):
                if metadata:
                    df[['Composer', 'Title']] = score.metadata['composer'], score.metadata['title']
            post.append(df)
        return post

    def note_list_whole_piece(self):
        """ Creates a note list from the whole piece for all scores- default note_list
        """
        pure_notes = []
        urls_index = 0
        prev_note = None

        for imported in self.scores:
            # if statement to check if analyses already done else do it
            score = imported.score
            if imported.analyses['note_list']:
                pure_notes += imported.analyses['note_list']
                urls_index += 1
                continue
            parts = score.getElementsByClass(stream.Part)
            score_notes = []
            for part in parts:
                noteList = part.flat.getElementsByClass(['Note', 'Rest'])
                for _note in noteList:
                    if _note.tie is not None:
                        if _note.tie.type == 'start':
                            note_obj = NoteListElement(_note, score.metadata, part.partName, score.index(part),
                                                       _note.quarterLength, self.paths[urls_index], prev_note)
                            score_notes.append(note_obj)
                        else:
                            score_notes[-1].duration += _note.quarterLength
                    else:
                        note_obj = NoteListElement(_note, score.metadata, part.partName, score.index(part),
                                                   _note.quarterLength, self.paths[urls_index], prev_note)
                        score_notes.append(note_obj)
                    # Rests carry the last non-rest note as their prev_note
                    if not score_notes[-1].note.isRest:
                        prev_note = score_notes[-1]
                note_obj = NoteListElement(note.Rest(), score.metadata, part.partName, score.index(part), 4.0,
                                           self.paths[urls_index], prev_note)
                score_notes.append(note_obj)
            urls_index += 1
            # add to dictionary
            imported.analyses['note_list'] = score_notes
            pure_notes += score_notes
        return pure_notes

    def note_list_no_unisons(self):
        """ Creates a note list from the whole piece for all scores combining unisons

        Combines consecutive notes at the same pitch into one note, adding in the duration
        of the next note into the previous one.
        """
        pure_notes = []
        urls_index = 0
        prev_note = None
        for imported in self.scores:
            score = imported.score
            parts = score.getElementsByClass(stream.Part)
            for part in parts:
                noteList = part.flat.getElementsByClass(['Note', 'Rest'])
                prev_pitch = None
                for _note in noteList:
                    if not _note.isRest and _note.nameWithOctave == prev_pitch:
                        pure_notes[len(pure_notes) - 1].duration += _note.quarterLength
                    else:
                        note_obj = NoteListElement(_note, score.metadata, part.partName, score.index(part),
                                                   _note.quarterLength, self.paths[urls_index], prev_note)
                        pure_notes.append(note_obj)
                    if not _note.isRest:
                        prev_pitch = _note.nameWithOctave
                    else:
                        prev_pitch == 'Rest'
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
                note_obj = NoteListElement(note.Rest(), score.metadata, part.partName, score.index(part), 4.0,
                                           self.paths[urls_index], prev_note)
                pure_notes.append(note_obj)
            urls_index += 1
        return pure_notes

    def note_list_selected_offset(self, offsets: list):
        """
        Creates a note list from the whole piece for all scores, going by provided offsets

        Parameters
        ----------
        offsets : list
            offsets within measures to collect notes at (notes collected will be those that are sounding at that offset- not just starting)
        """
        pure_notes = []
        urls_index = 0
        prev_note = None
        for imported in self.scores:
            score = imported.score
            parts = score.getElementsByClass(stream.Part)
            for part in parts:
                measures = part.getElementsByClass(stream.Measure)
                for measure in measures:
                    voices = measure.getElementsByClass(stream.Voice)
                    for voice in voices:
                        for _note in voice:
                            for point in offsets:
                                if point >= _note.offset and point < (_note.offset + _note.quarterLength):
                                    note_obj = NoteListElement(_note, score.metadata, part.partName, score.index(part),
                                                               _note.quarterLength, self.paths[urls_index], prev_note)
                                    pure_notes.append(note_obj)
                                    if not pure_notes[-1].note.isRest:
                                        prev_note = pure_notes[-1]
                                    break
            urls_index += 1
        return pure_notes

    def note_list_incremental_offset(self, min_offset):
        """
        Creates a note list from the whole piece for all scores, sampling at a regular interval- not within a measure

        Parameters
        ----------
        min_offset : int
            sample every x offset- 2 will sample every half note, 1 every quarter note, etc.
        """
        pure_notes = []
        urls_index = 0
        prev_note = None
        for imported in self.scores:
            score = imported.score
            for part in score.getElementsByClass(stream.Part):
                counter = 0
                while counter < score.highestTime - min_offset:
                    stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False,
                                                                    mustFinishInSpan=False, includeEndBoundary=True,
                                                                    includeElementsThatEndAtStart=False)
                    note_at_offset = None
                    for item in stuff_at_offset:
                        if type(item) == note.Note or type(item) == note.Rest:
                            note_at_offset = item
                            break
                    if note_at_offset:
                        note_obj = NoteListElement(note_at_offset, score.metadata, part.partName, score.index(part),
                                                   min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    else:
                        note_obj = NoteListElement(note.Rest(), score.metadata, part.partName, score.index(part),
                                                   min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    counter += min_offset
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
            note_obj = NoteListElement(note.Rest(), score.metadata, part.partName, score.index(part), 4.0,
                                       self.paths[urls_index], prev_note)
        urls_index += 1
        return pure_notes


    def vis_pandas_setup(self, min_offset):
        urls_index = 0
        prev_note = None
        dataframes = []
        for imported in self.scores:
            score = imported.score
            part_rows = []
            pure_notes = []
            row_names = []
            for part in score.getElementsByClass(stream.Part):
                counter = 0
                row_names.append(part.partName)
                while counter < score.highestTime - min_offset:
                    stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False,
                                                                    mustFinishInSpan=False, includeEndBoundary=True,
                                                                    includeElementsThatEndAtStart=False)
                    note_at_offset = None
                    for item in stuff_at_offset:
                        if type(item) == note.Note or type(item) == note.Rest:
                            note_at_offset = item
                            break
                    if note_at_offset:
                        note_obj = NoteListElement(note_at_offset, score.metadata, part.partName, score.index(part),
                                                   min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    else:
                        note_obj = NoteListElement(note.Rest(), score.metadata, part.partName, score.index(part),
                                                   min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    counter += min_offset
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
                part_rows.append(pure_notes)
                pure_notes = []

            column_names = []
            i = 0
            while i < score.highestTime - min_offset:
                column_names.append(i)
                i += min_offset

            df = pd.DataFrame(part_rows, index=row_names, columns=column_names)
            dataframes.append(df)
        return dataframes

# For single file uploads
class ScoreBase:
    """
    A class for importing a single score- offers more precise construction options

    Attributes
    ----------
    url : str
        url or path of mei file
    score : music21.Score
        music21.Score object gathered from mei file import
    note_list : list of NoteListElement
        list of notes constructed from score
    """
    def __init__(self, url):
        """
        Parameters
        ----------
        url:
            url or path of mei file
        Raises
        ----------
        Exception
            If score isn't succesfully imported, raises error
        """
        self.url = url
        self.score = importScore(url)
        if self.score is None:
            raise Exception("Import from", str(self.url),
                            "failed, please check your ath/file type.")
        self.note_list = self.note_list_whole_piece()

    def note_list_whole_piece(self):
        """ Creates a note list from the whole piece- default note_list
        """
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
        prev_note = None
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for _note in noteList:
                if _note.tie is not None:
                    if _note.tie.type == 'start':
                        note_obj = NoteListElement(_note, self.score.metadata, part.partName, self.score.index(part),
                                                   _note.quarterLength, self.url, prev_note)
                        pure_notes.append(note_obj)
                    else:
                        pure_notes[len(pure_notes) - 1].duration += _note.quarterLength
                else:
                    note_obj = NoteListElement(_note, self.score.metadata, part.partName, self.score.index(part),
                                               _note.quarterLength, self.url, prev_note)
                    pure_notes.append(note_obj)
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
            note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0,
                                       self.url, prev_note)
            pure_notes.append(note_obj)
        return pure_notes

    # Combines unison intervals into one note- generally for increased pattern finding
    def note_list_no_unisons(self):
        """ Creates a note list from the whole piece for all scores combining unisons

        Combines consecutive notes at the same pitch into one note, adding in the duration
        of the next note into the previous one.
        """
        pure_notes = []
        urls_index = 0
        prev_note = None
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            prev_pitch = None
            for _note in noteList:
                if not _note.isRest and _note.nameWithOctave == prev_pitch:
                    pure_notes[len(pure_notes) - 1].duration += _note.quarterLength
                else:
                    note_obj = NoteListElement(_note, self.score.metadata, part.partName, self.score.index(part),
                                               _note.quarterLength, self.url, prev_note)
                    pure_notes.append(note_obj)
                if not _note.isRest:
                    prev_pitch = _note.nameWithOctave
                else:
                    prev_pitch == 'Rest'
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
            note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0,
                                       self.url, prev_note)
            pure_notes.append(note_obj)
        urls_index += 1
        return pure_notes

    # Gets only notes that start on the specified beats- allows for user specification in case of weird time signatures
    def note_list_selected_beats(self, beats: list):
        """
        Creates a note list from the whole piece, going by provided beats

        Parameters
        ----------
        beats : list
            collects all notes which begin on specified beat
        """
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
        prev_note = None
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for _note in noteList:
                if _note.beat in beats:
                    note_obj = NoteListElement(_note, self.score.metadata, part.partName, self.score.index(part),
                                               _note.quarterLength, self.url, prev_note)
                    pure_notes.append(note_obj)
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
            note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0,
                                       self.url, prev_note)
            pure_notes.append(note_obj)
        return pure_notes

    def note_list_by_offset(self, offsets: list):
        """
        Creates a note list from the whole piece, going by provided offsets

        Parameters
        ----------
        offsets : list
            offsets within measures to collect notes at (notes collected will be those that are sounding at that offset- not just starting)
        """
        pure_notes = []
        part_number = 0
        prev_note = None
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            part_number += 1
            measures = part.getElementsByClass(stream.Measure)
            for measure in measures:
                voices = measure.getElementsByClass(stream.Voice)
                for voice in voices:
                    for _note in voice:
                        for point in offsets:
                            if point >= _note.offset and point < (_note.offset + _note.quarterLength):
                                note_obj = NoteListElement(_note, self.score.metadata, part.partName, part_number,
                                                           _note.quarterLength, self.url, prev_note)
                                pure_notes.append(note_obj)
                                if not pure_notes[-1].note.isRest:
                                    prev_note = pure_notes[-1]
                                break
        return pure_notes

    # Allows for very specific note selection
    def note_list_single_part(self, part, measure_start, num_measures):
        """
        Creates a note list from a selected measure range within a single voice

        Parameters
        ----------
        part : int
            part number
        measure_start : int
            starting measure
        num_measures : int
            measures until end measure
        """
        pure_notes = []
        part_selected = self.score.getElementsByClass(stream.Part)[part]
        measures = part_selected.getElementsByClass(stream.Measure)
        measures_selected = []
        prev_note = None
        for i in range(num_measures):
            measures_selected.append(measures[i + measure_start])
        for measure in measures_selected:
            voices = measure.getElementsByClass(stream.Voice)
            for voice in voices:
                for _note in voice:
                    print(_note.offset)
                    if _note.tie is not None:
                        if _note.tie.type == 'start':
                            note_obj = NoteListElement(_note, self.score.metadata, part_selected.partName, part,
                                                       _note.quarterLength, self.url, prev_note)
                            pure_notes.append(note_obj)
                        else:
                            pure_notes[len(pure_notes) - 1].duration += _note.quarterLength
                    else:
                        note_obj = NoteListElement(_note, self.score.metadata, part_selected.partName, part,
                                                   _note.quarterLength, self.url, prev_note)
                        pure_notes.append(note_obj)
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
        return pure_notes

    # Allows for specific selection in terms of measures, but gets all parts/instruments
    def note_list_all_parts(self, measure_start, num_measures):
        """
        Creates a note list from a selected measure range over all voices

        Parameters
        ----------
        measure_start : int
            starting measure
        num_measures : int
            measures until end measure
        """
        pure_notes = []
        prev_note = None
        parts = self.score.getElementsByClass(stream.Part)
        for part in parts:
            measures = part.getElementsByClass(stream.Measure)
            measures_selected = []
            for i in range(num_measures):
                measures_selected.append(measures[i + measure_start])
            for measure in measures_selected:
                voices = measure.getElementsByClass(stream.Voice)
                for voice in voices:
                    for _note in voice:
                        if _note.tie is not None:
                            if _note.tie.type == 'start':
                                note_obj = NoteListElement(_note, self.score.metadata, part.partName,
                                                           self.score.index(part), _note.quarterLength, self.url,
                                                           prev_note)
                                pure_notes.append(note_obj)
                            else:
                                pure_notes[len(pure_notes) - 1].duration += _note.quarterLength
                        else:
                            note_obj = NoteListElement(_note, self.score.metadata, part.partName, self.score.index(part),
                                                       _note.quarterLength, self.url, prev_note)
                            pure_notes.append(note_obj)
                        if not pure_notes[-1].note.isRest:
                            prev_note = pure_notes[-1]
            # Added rest to ensure parts don't overlap
            note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0,
                                       self.url, prev_note)
            pure_notes.append(note_obj)
        return pure_notes

    def note_list_incremental_offset(self, min_offset):
        """
        Creates a note list from the whole piece, sampling at a regular interval- not within a measure

        Parameters
        ----------
        min_offset : int
            sample every x offset- 2 will sample every half note, 1 every quarter note, etc.
        """
        pure_notes = []
        prev_note = None
        for part in self.score.getElementsByClass(stream.Part):
            counter = 0
            while counter < self.score.highestTime - min_offset:
                stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False,
                                                                includeEndBoundary=True,
                                                                includeElementsThatEndAtStart=False)
                note_at_offset = None
                for item in stuff_at_offset:
                    if type(item) == note.Note or type(item) == note.Rest:
                        note_at_offset = item
                        break
                if note_at_offset:
                    note_obj = NoteListElement(note_at_offset, self.score.metadata, part.partName,
                                               self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                else:
                    note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName,
                                               self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
                counter += min_offset
        note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0,
                                   self.url, prev_note)
        return pure_notes


    def vis_pandas_setup(self, min_offset):
        part_rows = []
        prev_note = None
        pure_notes = []
        row_names = []
        for part in self.score.getElementsByClass(stream.Part):
            counter = 0
            row_names.append(part.partName)
            while counter < self.score.highestTime - min_offset:
                stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False,
                                                                includeEndBoundary=True,
                                                                includeElementsThatEndAtStart=False)
                note_at_offset = None
                for item in stuff_at_offset:
                    if type(item) == note.Note or type(item) == note.Rest:
                        note_at_offset = item
                        break
                if note_at_offset:
                    note_obj = NoteListElement(note_at_offset, self.score.metadata, part.partName,
                                               self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                else:
                    note_obj = NoteListElement(note.Rest(), self.score.metadata, part.partName,
                                               self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                counter += min_offset
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
            part_rows.append(pure_notes)
            pure_notes = []

        column_names = []
        i = 0
        while i < self.score.highestTime - min_offset:
            column_names.append(i)
            i += min_offset

        df = pd.DataFrame(part_rows, index=row_names, columns=column_names)
        return df

class VectorInterval:
    """
    An individual vector with information about the notes creating it

    Attributes
    ----------
    vector : int or str
        vector- in generic or semitones: is "Rest" if done between a note and a rest
    note1 : NoteListElement
        first note of interval pair
    note2 : NoteListElement
        list of notes constructed from score
    """
    def __init__(self, vector, note1: NoteListElement, note2: NoteListElement):
        self.vector = vector
        self.note1 = note1
        self.note2 = note2

    def __str__(self):
        if self.note1.note.isRest or self.note2.note.isRest:
            return "<VectorInterval: Rest, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note,
                                                                                    self.note2.note)
        else:
            return "<VectorInterval: {}, First Note: {}, Second Note: {}>".format(self.vector,
                                                                                  self.note1.note.nameWithOctave,
                                                                                  self.note2.note.nameWithOctave)

# Allows for selected "vectorizations" given a note list created from either ScoreBase or CorpusBase
# Consider making this a Standalone method- an object seems slightly redundant/hard to justify
class IntervalBase:
    """
    A list of VectorInterval objects created from a note list

    Attributes
    ----------
    notes : list
        note list gathered from either CorpusBase or ScoreBase's methods/attributes
    generic_intervals : list
        creates list of VectorInterval objects in terms of generic intervals
    semitone_intervals : list
        creates list of VectorInterval objects in terms of semitone intervals
    """
    def __init__(self, notes):
        """
        Parameters
        ----------
        notes:
            note list gathered from either CorpusBase or ScoreBase's methods/attributes
        """
        self.notes = notes
        self.generic_intervals = self.vectorize_generic(self.notes)
        self.semitone_intervals = self.vectorize_semitone(self.notes)

    # Construct intervals in terms of semitone distances between notes
    def vectorize_semitone(self, notes):
        """Creates list of VectorInterval objects in terms of semitone intervals

        Parameters
        ----------
        notes:
            (frequently self.notes): note list gathered from either CorpusBase or ScoreBase's methods/attributes
        """
        vec = []
        for i in range(len(notes) - 1):
            if notes[i].note.isRest or notes[i + 1].note.isRest:
                interval_obj = VectorInterval("Rest", notes[i], notes[i + 1])
                vec.append(interval_obj)
            else:
                interval_semitones = interval.Interval(notes[i].note, notes[i + 1].note).semitones
                interval_obj = VectorInterval(interval_semitones, notes[i], notes[i + 1])
                vec.append(interval_obj)
        return vec

    # Construct intervals in terms of generic distance between notes
    def vectorize_generic(self, notes):
        """Creates list of VectorInterval objects in terms of generic intervals

        Parameters
        ----------
        notes:
            (frequently self.notes): note list gathered from either CorpusBase or ScoreBase's methods/attributes
        """
        vec = []
        for i in range(len(notes) - 1):
            if notes[i].note.isRest or notes[i + 1].note.isRest:
                interval_obj = VectorInterval("Rest", notes[i], notes[i + 1])
                vec.append(interval_obj)
            else:
                interval_semitones = interval.Interval(notes[i].note, notes[i + 1].note).semitones
                interval_obj = VectorInterval(interval.convertSemitoneToSpecifierGeneric(interval_semitones)[1],
                                              notes[i], notes[i + 1])
                vec.append(interval_obj)
        return vec

# An individual match event- can be used for close matches as well
class Match:
    """
    A pattern that has been deemed part of a match

    Attributes
    ----------
    pattern : list
        list of vectors in pattern
    first_note : NoteListElement
        first note in the soggetti creating the vector pattern
    last_note : NoteListElement
        last note in the soggetti creating the vector pattern
    durations : list
        list of durations of notes in soggetti creating the vector pattern
    ema : str
        standalone ema snippet for the pattern
    ema_url : str
        url to get mei for the pattern
    """
    def __init__(self, pattern, first_note: NoteListElement, last_note: NoteListElement, durations):
        self.pattern = pattern
        self.first_note = first_note
        self.last_note = last_note
        # Construct an ema address for the entire pattern to pass on
        ema = str(self.first_note.note.measureNumber) + "-" + str(self.last_note.note.measureNumber) + "/" + str(
            self.first_note.partNumber) + "/"
        ema += ("@" + str(self.first_note.note.beat) + "-end")
        for i in range(self.last_note.note.measureNumber - self.first_note.note.measureNumber - 1):
            ema += ",@start-end"
        ema += (",@start-" + str(self.last_note.note.beat))
        self.ema = ema
        try:
            splice = self.first_note.piece_url.index('mei/')
            self.ema_url = "https://ema.crimproject.org/https%3A%2F%2Fcrimproject.org%2Fmei%2F" + str(
                self.first_note.piece_url[splice + 4:]) + "/" + str(self.ema)
        except:
            self.ema_url = "File must be a crim url to have a valid EMA url"
        self.durations = durations

# Object representing all the occurences of a pattern in a list of notes/vectors
# User generally doesn't create this- it is done in the finding matches methods
class PatternMatches:
    """
    A group of Match objects generated from a pattern

    Attributes
    ----------
    pattern : list
        pattern generating matches
    matches : list
        list of Match objects found to be matching the pattern
    """

    def __init__(self, pattern, matches: list):
        self.pattern = pattern
        self.matches = matches

    def print_exact_matches(self):
        """A facilitated way to display all the matches gathered by a find_exact_matches search
        """
        print("Melodic interval/pattern " + str(self.pattern) + " occurs " + str(len(self.matches)) + " times:")
        for match in self.matches:
            print("In " + str(match.first_note.metadata.title) + " part " + str(
                match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) + \
                  " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(
                match.durations))
        print("\n")

    def print_close_matches(self):
        """A facilitated way to display all the matches gathered by a find_close_matches search
        """
        print("Occurences of " + str(self.pattern) + " or similar:")
        for match in self.matches:
            print("Pattern " + str(match.pattern) + " appears in " + str(
                match.first_note.metadata.title) + " part " + str(
                match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) + \
                  " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(
                match.durations))
        print("Said pattern or similar appeared " + str(len(self.matches)) + " times.\n")

class ClassifiedMatch:
    """
    Group of matches classified to be a periodic entry, imitative duo, or fuga

    Attributes
    ----------
    matches : list
        list of Match objects found to be matching the pattern
    type : str
        either "periodic entry", "imitative duo", or "fuga" depending on match classification
    pattern : list
        interval pattern that the matches have in common
    ema : str
        ema address for the series of patterns
    ema_url : str
        url to download mei slice for the series of patterns
    """
    def __init__(self, matches: list, type):
        """
        Parameters
        ----------
        matches : list
            list of Match objects found to be matching the pattern
        type : str
            either "periodic entry", "imitative duo", or "fuga" depending on match classification
        """
        self.matches = matches
        self.type = type
        self.pattern = self.matches[0].pattern

        ema_measures = ""
        ema_parts = ""
        ema_beats = ""
        for match in self.matches:
            ema_measures += str(match.first_note.note.measureNumber) + "-" + str(
                match.last_note.note.measureNumber) + ","
            for i in range(match.last_note.note.measureNumber - match.first_note.note.measureNumber + 1):
                ema_parts += str(match.first_note.partNumber) + ","
            ema_beats += "@" + str(match.first_note.note.beat) + "-end,"
            for j in range(match.last_note.note.measureNumber - match.first_note.note.measureNumber - 1):
                ema_beats += "@start-end,"
            ema_beats += "@start-" + str(match.last_note.note.beat) + ","
        self.ema = ema_measures[0:len(ema_measures) - 1] + "/" + ema_parts[0:len(ema_parts) - 1] + "/" + ema_beats[
                                                                                                         0:len(
                                                                                                             ema_beats) - 1]

        try:
            splice = self.matches[0].first_note.piece_url.index('mei/')
            self.ema_url = "https://ema.crimproject.org/https%3A%2F%2Fcrimproject.org%2Fmei%2F" + str(
                self.matches[0].first_note.piece_url[splice + 4:]) + "/" + str(self.ema)
        except:
            self.ema_url = "File must be a crim url (not a file path) to have a valid EMA url"
