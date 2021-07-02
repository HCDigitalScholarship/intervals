from music21 import *
import music21 as m21
import time
# import requests
# httpx appears to be faster than requests, will fit better with an async version
import httpx
from pathlib import Path
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from itertools import combinations


# Unncessary at the moment
# MEINSURI = 'http://www.music-encoding.org/ns/mei'
# MEINS = '{%s}' % MEINSURI
# mei_doc = ET.fromstring(requests.get(path).text)
#   # Find the title from the MEI file and update the Music21 Score metadata
# title = mei_doc.find(f'{MEINS}meiHead//{MEINS}titleStmt/{MEINS}title').text
# score.metadata.title = title
# mei_doc = ET.fromstring(requests.get(path).text)
#   # Find the composer from the MEI file and update the Music21 Score metadata
# composer = mei_doc.find(f'{MEINS}meiHead//{MEINS}respStmt/{MEINS}persName').text
# score.metadata.composer = composer

# An extension of the music21 note class with more information easily accessible

pathDict = {}

class NoteListElement:
    """
    An extension of the music21 note class

    Attributes
    ----------
    note : m21.note.Note
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
    def __init__(self, note: m21.note.Note, metadata, part, partNumber, duration, piece_url, prev_note=None):
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
    def __init__(self, score):
        self.score = score
        self.analyses = {'note_list': None}
        self._intervalMethods = {
            # (quality, directed, compound):   function returning the specified type of interval
            # diatonic with quality
            ('q', True, True): ImportedPiece._qualityUndirectedCompound,
            ('q', True, False): ImportedPiece._qualityDirectedSimple,
            ('q', False, True): lambda cell: cell.name if hasattr(cell, 'name') else cell,
            ('q', False, False): lambda cell: cell.semiSimpleName if hasattr(cell, 'semiSimpleName') else cell,
            # diatonic interals without quality
            ('d', True, True): lambda cell: cell.directedName[1:] if hasattr(cell, 'directedName') else cell,
            ('d', True, False): ImportedPiece._noQualityDirectedSimple,
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
                ser = ser[~ser.index.duplicated()] # remove multiple events at the same offset in a given part
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
            return None
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

    def getDuration(self, df=None, n=1):
        '''
        If no dataframe is passed as the df parameter (the default), return a
        `pandas.DataFrame` of floats giving the duration of notes and rests in 
        each part where 1 = quarternote, 1.5 = a dotted quarter, 4 = a whole 
        note, etc. If a df is passed, then return a df of the same shape giving 
        the duration of each of the slices of this df. This is useful if you 
        want to know what the durations of something other than single notes 
        and rests, such as the durations of intervals.
        
        If n is set, it must be an integer >= 1 and less than the number of 
        rows in df. It determines how many adjacent items have their durations 
        grouped together. To get the duration of single events, n should be 1 
        (default). You could set n=3 if you wanted to get the duration of all 
        consecutive 3-note groups, for example.'''

        if 'Duration' not in self.analyses or df is not None or n != 1:
            _df = self._getM21ObjsNoTies() if df is None else df.copy()
            highestTime = self.score.highestTime
            _df.loc[highestTime, :] = 0
            newCols = []
            for i in range(len(_df.columns)):
                ser = _df.iloc[:, i]
                ser.dropna(inplace=True) 
                vals = ser.index[n:] - ser.index[:-n]
                ser.drop(labels=ser.index[-n:], inplace=True)
                ser[:] = vals
                newCols.append(ser)
            result = pd.concat(newCols, axis=1)
            if df is None and n == 1:
                self.analyses['Duration'] = result
            else:
                return result
        return self.analyses['Duration']

    def _noteRestHelper(self, noteOrRest):
        if noteOrRest.isRest:
            return 'Rest'
        return noteOrRest.nameWithOctave

    def getNoteRest(self):
        '''Return a table of the notes and rests in the piece. Rests are
        designated with the string "Rest". Notes are shown such that middle C
        is "C4".'''
        if 'NoteRest' not in self.analyses:
            df = self._getM21ObjsNoTies().applymap(self._noteRestHelper, na_action='ignore')
            self.analyses['NoteRest'] = df
        return self.analyses['NoteRest']

    def getBeat(self):
        '''
        Return a table of the beat positions of all the notes and rests.
        '''
        if 'Beat' not in self.analyses:
            df = self._getM21ObjsNoTies().applymap(lambda note: note.beat, na_action='ignore')
            self.analyses['Beat'] = df
        return self.analyses['Beat']

    def _getBeatIndex(self):
        '''
        Return a series of the first valid value in each row of .getBeat().
        '''
        if 'BeatIndex' not in self.analyses:
            ser = self.getBeat().apply(lambda row: row.dropna()[0], axis=1)
            self.analyses['BeatIndex'] = ser
        return self.analyses['BeatIndex']

    def detailIndex(self, df, offset=True, measure=True, beat=True):
        '''
        Return the passed dataframe with a multi-index of the measure and beat
        position.
        '''
        cols = [df, self.getMeasure().iloc[:, 0], self._getBeatIndex()]
        names = ['Measure', 'Beat']
        temp = pd.concat(cols, axis=1)
        temp2 = temp.iloc[:, len(df.columns):].ffill()
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

    def getBeatStrength(self):
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

    def getTimeSignature(self):
        """
        Return a data frame containing the time signatures and their offsets
        """

        if 'TimeSignature' not in self.analyses:
            time_signatures = []
            for part in self._getSemiFlatParts():
                time_signatures.append(pd.Series({ts.offset: ts for ts in part.getTimeSignatures()}))
            df = pd.concat(time_signatures, axis=1)
            df = df.applymap(lambda ts: ts.ratioString, na_action='ignore')
            df.columns = self._getPartNames()
            self.analyses['TimeSignature'] = df
        return self.analyses['TimeSignature']

        
    def getMeasure(self):
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

    def getSoundingCount(self):
        """
        This would return a series with the number of parts that currently have
        a note sounding.
        """

        if not 'SoundingCount' in self.analyses:

            nr = self.getNoteRest().ffill()
            df = nr[nr != 'Rest']
            ser = df.count(axis=1)
            ser.name = 'Sounding'

            self.analyses['SoundingCount'] = ser

        return self.analyses['SoundingCount']
        

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

    def _melodifyPart(ser):
        ser.dropna(inplace=True)
        shifted = ser.shift(1)
        partDF = pd.concat([ser, shifted], axis=1)
        res = partDF.apply(ImportedPiece._melodicIntervalHelper, axis=1).dropna()
        return res

    def _getM21MelodicIntervals(self):
        if 'M21MelodicIntervals' not in self.analyses:
            m21Objs = self._getM21ObjsNoTies()
            df = m21Objs.apply(ImportedPiece._melodifyPart)
            self.analyses['M21MelodicIntervals'] = df
        return self.analyses['M21MelodicIntervals']

    def _getRegularM21MelodicIntervals(self, unit):
        m21Objs = self._getM21ObjsNoTies()
        m21Objs = self.regularize(m21Objs, unit=unit)
        return m21Objs.apply(ImportedPiece._melodifyPart)

    def _qualityUndirectedCompound(cell):
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
        if hasattr(cell, 'semiSimpleName'):
            if cell.direction.value == -1:
                return '-' + cell.semiSimpleName[1:] 
            else:
                return cell.semiSimpleName[1:]
        else:
            return cell

    def getMelodic(self, kind='q', directed=True, compound=True, unit=0):
        '''
        Return melodic intervals for all voice pairs. Each melodic interval
        is associated with the starting offset of the second note in the
        interval. If you want melodic intervals measured at a regular duration,
        do not pipe this methods result to the `unit` method. Instead,
        pass the desired regular durational interval as an integer or float as
        the `unit` parameter.

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
            melodic intervals. See the documentation of the `unit` method for
            more about this.
        :returns: `pandas.DataFrame` of melodic intervals in each part
        '''
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, directed, compound)
        key = ('MelodicIntervals', kind, directed, compound)
        if key not in self.analyses or unit:
            df = self._getRegularM21MelodicIntervals(unit) if unit else self._getM21MelodicIntervals()
            df = df.applymap(self._intervalMethods[settings])
            if kind == 'z':
                df = df.applymap(ImportedPiece._zeroIndexIntervals, na_action='ignore')
            if unit:
                return df
            else:
                self.analyses[key] = df
        return self.analyses[key]

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

    def getHarmonic(self, kind='q', directed=True, compound=True):
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
        else: # offsets == 'last':
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
            vals = [', '.join(col.iloc[si[i] : ei[i]]) for i in range(len(si))]
            ser = pd.Series(vals, name=col.name, index=ind)
            return ser

        chunks = ImportedPiece._ngrams_offsets_helper(col, n, offsets)
        chains = pd.concat(chunks, axis=1)
        for excl in exclude:
            chains = chains[(chains != excl).all(1)]
        chains.dropna(inplace=True)
        chains = chains.apply(lambda row: ', '.join(row), axis=1)
        return chains
    
    def getNgrams(self, df=None, n=3, how='columnwise', other=None, held='Held',
                  exclude=['Rest'], interval_settings=('d', True, True), unit=0,
                  offsets='first'):
        '''
        Group sequences of observations in a sliding window "n" events long
        (default n=3). If the `exclude` parameter is passed and any item in that
        list is found in an ngram, that ngram will be removed from the resulting
        DataFrame. Since `exclude` defaults to `['Rest']`, pass an empty list if
        you want to allow rests in your ngrams.

        There are two primary modes for the `how` parameter. When set to
        "columnwise" (default), this is the simple case where the events in each
        column of the `df` DataFrame has its events grouped at the offset of the
        first event in the window. For example, to get 4-grams of melodic
        intervals:

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.getNgrams(df=ip.getMelodic(), n=4)

        If `how` is set to 'modules' this will return contrapuntal modules. In
        this case, if the `df` or `other` parameters are left as None, they will
        be replaced with the current piece's harmonic and melodic intervals
        respectfully. These intervals will be formed according to the
        interval_settings argument, which gets passed to the getMelodic and
        getHarmonic methods (see those methods for an explanation of those
        settings). This makes it easy to make contrapuntal-module ngrams, e.g.:

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.getNgrams(how='modules')

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
        ngrams = ip.getNgrams(how='modules', unit=2)

        Otherwise, you can give specific `df` and/or `other` DataFrames in which
        case the `interval_settings` parameter will be ignored. Also, you can
        use the `held` parameter to be used for when the lower voice sustains a
        note while the upper voice moves. This defaults to 'Held' to distinguish
        between held notes and reiterated notes in the lower voice, but if this
        distinction is not wanted for your query, you may want to pass way a
        unison gets labeled in your `other` DataFrame (e.g. "P1" or "1").
        '''
        if how == 'columnwise':
            return df.apply(ImportedPiece._ngramHelper, args=(n, exclude, offsets))
        if df is None:
            df = self.getHarmonic(*interval_settings)
            if unit:
              df = self.regularize(df, unit)
        if other is None:
            other = self.getMelodic(*interval_settings, unit=unit)
        cols = []
        for pair in df.columns:
            lowerVoice = pair.split('_')[0]
            combo = pd.concat([other[lowerVoice], df[pair]], axis=1)
            combo.fillna({lowerVoice: held}, inplace=True)
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
                col = [''.join([cell
                                for row in combo.iloc[si[i] : ei[i]].values   # second loop
                                for cell in row][2:-1])                       # innermost loop
                       for i in range(len(si))]                               # outermost loop
                col = pd.Series(col)
                if offsets == 'first':
                    col.index = starts.index
                else:
                    col.index = ends.index
            else: # n >= 1
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
    def __init__(self, paths:list):
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
        self.scores = [] # store lists of ImportedPieces generated from the path above
        mei_conv = converter.subConverters.ConverterMEI()
        for path in paths:
            if path in pathDict:
                # if the path has already been "memorized"
                pathScore = ImportedPiece(pathDict[path])
                self.scores.append(pathDict[path])
                print("Memoized piece detected...")
                continue
            elif not path.startswith('http'):
                print("Requesting file from " + str(path) + "...")
                try:
                    score = mei_conv.parseFile(path)
                    pathDict[path] = ImportedPiece(score)
                    self.scores.append(pathDict[path])
                    print("Successfully imported.")
                except:
                    print("Import of " + str(path) + " failed, please check your file path/file type. Continuing to next file...")
            else:
                try:
                    # self.scores.append(m21.converter.parse(requests.get(path).text))
                    score = m21.converter.parse(httpx.get(path).text)
                    pathDict[path] = ImportedPiece(score)
                    self.scores.append(pathDict[path])
                    print("Successfully imported.")
                except:
                    print("Import from " + str(path) + " failed, please check your url. File paths must begin with a '/'. Continuing to next file...")

        if len(self.scores) == 0:
            raise Exception("At least one score must be succesfully imported")

        self.note_list = self.note_list_whole_piece()
        self.no_unisons = self.note_list_no_unisons()

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
                for note in noteList:
                    if note.tie is not None:
                        if note.tie.type == 'start':
                            note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.paths[urls_index], prev_note)
                            score_notes.append(note_obj)
                        else:
                            score_notes[-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.paths[urls_index], prev_note)
                        score_notes.append(note_obj)
                    # Rests carry the last non-rest note as their prev_note
                    if not score_notes[-1].note.isRest:
                        prev_note = score_notes[-1]
                note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, self.paths[urls_index], prev_note)
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
                for note in noteList:
                    if not note.isRest and note.nameWithOctave == prev_pitch:
                        pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.paths[urls_index], prev_note)
                        pure_notes.append(note_obj)
                    if not note.isRest:
                        prev_pitch = note.nameWithOctave
                    else:
                        prev_pitch == 'Rest'
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
                note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, self.paths[urls_index], prev_note)
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
                        for note in voice:
                            for point in offsets:
                                #print(note.offset, point)
                                if point >= note.offset and point < (note.offset + note.quarterLength):
                                    note_obj = NoteListElement(note, score.metadata, part.partName, score.index(part), note.quarterLength, self.paths[urls_index], prev_note)
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
                    stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False, includeEndBoundary=True, includeElementsThatEndAtStart=False)
                    note_at_offset = None
                    for item in stuff_at_offset:
                        if type(item) == m21.note.Note or type(item) == m21.note.Rest:
                            note_at_offset = item
                            break
                    if note_at_offset:
                        note_obj = NoteListElement(note_at_offset, score.metadata, part.partName, score.index(part), min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    else:
                        note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    counter += min_offset
                    if not pure_notes[-1].note.isRest:
                        prev_note = pure_notes[-1]
            note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), 4.0, self.paths[urls_index], prev_note)
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
                    stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False, includeEndBoundary=True, includeElementsThatEndAtStart=False)
                    note_at_offset = None
                    for item in stuff_at_offset:
                        if type(item) == m21.note.Note or type(item) == m21.note.Rest:
                            note_at_offset = item
                            break
                    if note_at_offset:
                        note_obj = NoteListElement(note_at_offset, score.metadata, part.partName, score.index(part), min_offset, self.paths[urls_index], prev_note)
                        note_obj.offset = counter
                        pure_notes.append(note_obj)
                    else:
                        note_obj = NoteListElement(m21.note.Rest(), score.metadata, part.partName, score.index(part), min_offset, self.paths[urls_index], prev_note)
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

            df = pd.DataFrame(part_rows, index = row_names, columns = column_names)
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
        print("Requesting file from " + str(self.url) + "...")
        # Detect if local file of url based on leading /
        if url in pathDict:
            pathScore = ImportedPiece(pathDict[url])
            self.score = pathDict[url].analyses['scores']
            print("Memoized piece detected...")
        else:
            if url[0] == '/':
                try:
                    self.score = converter.subConverters.ConverterMEI().parseFile(url)
                    print("Successfully imported.")
                except:
                    raise Exception("Import from " + str(self.url) + " failed, please check your ath/file type")
            else:
                try:
                    # self.score = m21.converter.parse(requests.get(self.url).text)
                    self.score = m21.converter.parse(httpx.get(self.url).text)
                    print("Successfully imported.")
                except:
                    raise Exception("Import from " + str(self.url) + " failed, please check your url/file type")
        self.note_list = self.note_list_whole_piece()

    def note_list_whole_piece(self):
        """ Creates a note list from the whole piece- default note_list
        """
        pure_notes = []
        parts = self.score.getElementsByClass(stream.Part)
        prev_note = None
        for part in parts:
            noteList = part.flat.getElementsByClass(['Note', 'Rest'])
            for note in noteList:
                if note.tie is not None:
                    if note.tie.type == 'start':
                        note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                        pure_notes.append(note_obj)
                    else:
                        pure_notes[len(pure_notes)-1].duration += note.quarterLength
                else:
                    note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                    pure_notes.append(note_obj)
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url, prev_note)
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
            for note in noteList:
                if not note.isRest and note.nameWithOctave == prev_pitch:
                    pure_notes[len(pure_notes)-1].duration += note.quarterLength
                else:
                    note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                    pure_notes.append(note_obj)
                if not note.isRest:
                    prev_pitch = note.nameWithOctave
                else:
                    prev_pitch == 'Rest'
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url, prev_note)
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
            for note in noteList:
                if note.beat in beats:
                        note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                        pure_notes.append(note_obj)
                        if not pure_notes[-1].note.isRest:
                            prev_note = pure_notes[-1]
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url, prev_note)
            pure_notes.append(note_obj)
        return pure_notes

    def note_list_by_offset(self, offsets:list):
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
                    for note in voice:
                        for point in offsets:
                            if point >= note.offset and point < (note.offset + note.quarterLength):
                                note_obj = NoteListElement(note, self.score.metadata, part.partName, part_number, note.quarterLength, self.url, prev_note)
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
            measures_selected.append(measures[i+measure_start])
        for measure in measures_selected:
            voices = measure.getElementsByClass(stream.Voice)
            for voice in voices:
                for note in voice:
                    print(note.offset)
                    if note.tie is not None:
                        if note.tie.type == 'start':
                            note_obj = NoteListElement(note, self.score.metadata, part_selected.partName, part, note.quarterLength, self.url, prev_note)
                            pure_notes.append(note_obj)
                        else:
                            pure_notes[len(pure_notes)-1].duration += note.quarterLength
                    else:
                        note_obj = NoteListElement(note, self.score.metadata, part_selected.partName, part, note.quarterLength, self.url, prev_note)
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
                measures_selected.append(measures[i+measure_start])
            for measure in measures_selected:
                voices = measure.getElementsByClass(stream.Voice)
                for voice in voices:
                    for note in voice:
                        if note.tie is not None:
                            if note.tie.type == 'start':
                                note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                                pure_notes.append(note_obj)
                            else:
                                pure_notes[len(pure_notes)-1].duration += note.quarterLength
                        else:
                            note_obj = NoteListElement(note, self.score.metadata, part.partName, self.score.index(part), note.quarterLength, self.url, prev_note)
                            pure_notes.append(note_obj)
                        if not pure_notes[-1].note.isRest:
                            prev_note = pure_notes[-1]
            # Added rest to ensure parts don't overlap
            note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url, prev_note)
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
                stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False, includeEndBoundary=True, includeElementsThatEndAtStart=False)
                note_at_offset = None
                for item in stuff_at_offset:
                    if type(item) == m21.note.Note or type(item) == m21.note.Rest:
                        note_at_offset = item
                        break
                if note_at_offset:
                    note_obj = NoteListElement(note_at_offset, self.score.metadata, part.partName, self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                else:
                    note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                if not pure_notes[-1].note.isRest:
                    prev_note = pure_notes[-1]
                counter += min_offset
        note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), 4.0, self.url, prev_note)
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
                stuff_at_offset = part.flat.getElementsByOffset(counter, mustBeginInSpan=False, mustFinishInSpan=False, includeEndBoundary=True, includeElementsThatEndAtStart=False)
                note_at_offset = None
                for item in stuff_at_offset:
                    if type(item) == m21.note.Note or type(item) == m21.note.Rest:
                        note_at_offset = item
                        break
                if note_at_offset:
                    note_obj = NoteListElement(note_at_offset, self.score.metadata, part.partName, self.score.index(part), min_offset, self.url, prev_note)
                    note_obj.offset = counter
                    pure_notes.append(note_obj)
                else:
                    note_obj = NoteListElement(m21.note.Rest(), self.score.metadata, part.partName, self.score.index(part), min_offset, self.url, prev_note)
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

        df = pd.DataFrame(part_rows, index = row_names, columns = column_names)
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
            return "<VectorInterval: Rest, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note, self.note2.note)
        else:
            return "<VectorInterval: {}, First Note: {}, Second Note: {}>".format(self.vector, self.note1.note.nameWithOctave, self.note2.note.nameWithOctave)

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
        """Creates list of VectorInterval objects in terms of generic intervals

        Parameters
        ----------
        notes:
            (frequently self.notes): note list gathered from either CorpusBase or ScoreBase's methods/attributes
        """
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
        ema =  str(self.first_note.note.measureNumber) + "-" + str(self.last_note.note.measureNumber) + "/" + str(self.first_note.partNumber) + "/"
        ema += ("@" + str(self.first_note.note.beat) + "-end")
        for i in range(self.last_note.note.measureNumber - self.first_note.note.measureNumber - 1):
            ema += ",@start-end"
        ema += (",@start-" + str(self.last_note.note.beat))
        self.ema = ema
        try:
            splice = self.first_note.piece_url.index('mei/')
            self.ema_url = "https://ema.crimproject.org/https%3A%2F%2Fcrimproject.org%2Fmei%2F" + str(self.first_note.piece_url[splice + 4:]) + "/" + str(self.ema)
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
    def __init__(self, pattern, matches:list):
        self.pattern = pattern
        self.matches = matches

    def print_exact_matches(self):
        """A facilitated way to display all the matches gathered by a find_exact_matches search
        """
        print("Melodic interval/pattern " + str(self.pattern) + " occurs " + str(len(self.matches)) + " times:")
        for match in self.matches:
            print("In " + str(match.first_note.metadata.title) + " part " + str(match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) +\
            " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(match.durations))
        print("\n")

    def print_close_matches(self):
        """A facilitated way to display all the matches gathered by a find_close_matches search
        """
        print("Occurences of " + str(self.pattern) + " or similar:")
        for match in self.matches:
            print("Pattern " + str(match.pattern) + " appears in " + str(match.first_note.metadata.title) + " part " + str(match.first_note.part) + " beginning in measure " + str(match.first_note.note.measureNumber) +\
            " and ending in measure " + str(match.last_note.note.measureNumber) + ". Notes lengths: " + str(match.durations))
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
            ema_measures += str(match.first_note.note.measureNumber) + "-" + str(match.last_note.note.measureNumber) + ","
            for i in range(match.last_note.note.measureNumber - match.first_note.note.measureNumber + 1):
                ema_parts += str(match.first_note.partNumber) + ","
            ema_beats += "@" + str(match.first_note.note.beat) + "-end,"
            for j in range(match.last_note.note.measureNumber - match.first_note.note.measureNumber - 1):
                ema_beats += "@start-end,"
            ema_beats += "@start-" + str(match.last_note.note.beat) + ","
        self.ema = ema_measures[0:len(ema_measures)-1] + "/" + ema_parts[0:len(ema_parts)-1] + "/" + ema_beats[0:len(ema_beats)-1]

        try:
            splice = self.matches[0].first_note.piece_url.index('mei/')
            self.ema_url = "https://ema.crimproject.org/https%3A%2F%2Fcrimproject.org%2Fmei%2F" + str(self.matches[0].first_note.piece_url[splice + 4:]) + "/" + str(self.ema)
        except:
            self.ema_url = "File must be a crim url (not a file path) to have a valid EMA url"
