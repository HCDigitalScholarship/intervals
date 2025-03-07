from music21 import *
# httpx appears to be faster than requests, will fit better with an async version
import httpx
from pathlib import Path
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from itertools import combinations
from itertools import combinations_with_replacement as cwr
from more_itertools import consecutive_groups
import os
import re
import collections
import verovio
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import plotly.express as px
from glob import glob
from IPython.display import display, SVG, HTML
import json
import urllib.parse
main_objs_dir = os.path.dirname(os.path.abspath(__file__))

MEINSURI = 'http://www.music-encoding.org/ns/mei'
MEINS = '{%s}' % MEINSURI
suppliedPattern = re.compile("<supplied.*?(<accid.*?\/>).*?<\/supplied>", flags=re.DOTALL)
datePattern = re.compile('date isodate="(1\d*)')

accepted_filetypes = ('mei', 'mid', 'midi', 'abc', 'xml', 'musicxml')
pathDict = {}

_directedNameMemos = {}  
def _directed_name_from_note_strings(note1, note2):
    key = (note1.nameWithOctave, note2.nameWithOctave)
    if key not in _directedNameMemos:
        ret = interval.Interval(note1, note2).directedName
        _directedNameMemos[key] = ret
        return ret
    else:
        return _directedNameMemos[key]

# An extension of the music21 note class with more information easily accessible
def importScore(path, recurse=False, verbose=False):
    '''
    Import piece or group of pieces and return an ImportedPiece or CorpusBase object respectively.
    Return None if there is an error. This function accepts piece urls, and local paths. A list of
    the accepted file formats can be found in the accepted_filetypes tuple. This function also
    accepts directories and will import all the score files within a passed directory. Set
    recurse=True (default False) to import all score files from the passed directory *and* those
    of all subdirectories. Set verbose=True (default False) to print out confirmation of import
    success for each piece. If any errors are encountered, these issues will be printed out
    regardless of verbose setting.
    '''
    if os.path.isdir(path):
        files = os.listdir(path)
        files = [os.path.join(path, file) for file in files]
        scores = []
        for file in files:
            if os.path.isdir(file) and recurse:
                score_list = importScore(file, recurse, verbose)
                if score_list is not None and len(score_list.scores):
                    scores.extend(score_list.scores)
            elif os.path.isfile(file):
                score = importScore(file, verbose=verbose)
                if score is not None:
                    scores.append(score)

        if len(scores):
            return CorpusBase(scores)
        elif verbose:
            print('No scores found in this directory: {}'.format(path))
        return

    date = None
    if path in pathDict and verbose:
        print('Previously imported piece detected.')
    else:
        mei_doc = None
        if path.startswith('http'):
            if verbose:
                print('Downloading remote score...')
            try:
                to_import = httpx.get(path).text
                mei_doc = ET.fromstring(to_import) if path.endswith('.mei') else None
            except:
                print('Error downloading',  str(path) + ', please check',
                      'your url and try again. Continuing to next file.')
                return None
        elif os.path.isfile(path):  # `path` is formatted like a file path
            ending = path.rsplit('.', 1)[1]
            if ending not in accepted_filetypes:
                return None
            if path.endswith('.mei'):
                try:
                    with open(path, "r") as file:
                        to_import = file.read()
                        mei_doc = ET.fromstring(to_import)
                except ET.ParseError as err:
                    print('Error reading the mei file tree of {}'.format(path), err, sep='\n')
            else:
                to_import = path
        else: # `path` is actually the string of an entire piece, used for user-supplied piece in streamlit
            to_import = path
            if '<mei' in path[:1000]: # is an <mei> element in the beginning of the piece?
                try:
                    mei_doc = ET.fromstring(to_import)
                except ET.ParseError as err:
                    print('Error reading this mei file:'.format(path[:200], err, sep='\n'))
        try:
            if mei_doc is not None:
                to_import = re.sub(suppliedPattern, '\\1', to_import)
                _date = re.search(datePattern, to_import)
                if _date:
                    date = int(_date.group(1))
            score = converter.parse(to_import)
            pathDict[path] = ImportedPiece(score, path, mei_doc, date)
            if verbose:
                print("Successfully imported", path[:180])
        except:
            print("Import of", str(path[:180]), "failed, please check your file, path, or url.")
            return None

    return pathDict[path]

def Crimport(path, recurse=False, verbose=False):
    '''
    Better naming convention for importing single files or directories of files. This is
    an alias for importScore. See that method's doc string for instructions.'''
    return importScore(path, recurse, verbose)

def _getCVFTable():
    if 'CVFTable' not in pathDict:
        pathDict['CVFTable'] = pd.read_csv(main_objs_dir + '/data/cadences/CVFLabels.csv', index_col='Ngram')
    return pathDict['CVFTable']

def _getCadenceTable():
    if 'CadenceTable' not in pathDict:
        pathDict['CadenceTable'] = pd.read_csv(main_objs_dir + '/data/cadences/cadenceLabels.csv', index_col=0)
    return pathDict['CadenceTable']


class ImportedPiece:
    def __init__(self, score, path, mei_doc=None, date=None):
        self.score = score
        self.path = path
        self.file_name = path.rsplit('.', 1)[0].rsplit('/')[-1]
        self.mei_doc = mei_doc
        self.analyses = {'note_list': None}
        title, composer = path, 'Not found'
        if mei_doc is not None:
            title = mei_doc.find('mei:meiHead//mei:titleStmt/mei:title', namespaces={"mei": MEINSURI})
            if title is not None and hasattr(title, 'text'):
                title = re.sub(r'\n', '', title.text).strip()
            composer = mei_doc.find('mei:meiHead//mei:titleStmt//mei:persName[@role="composer"]', namespaces={"mei": MEINSURI})
            if composer is None:  # for mei 3 files
                composer = mei_doc.find('mei:meiHead//mei:titleStmt/mei:composer', namespaces={"mei": MEINSURI})
            if composer is not None and hasattr(composer, 'text'):
                composer = re.sub(r'\n', '', composer.text).strip()
        else:
            if self.score.metadata.title is not None:
                title = self.score.metadata.title
            if self.score.metadata.composer is not None:
                composer = self.score.metadata.composer
        self.metadata = {'title': title, 'composer': composer, 'date': date}
        if not self.metadata['date']:
            if hasattr(self.score.metadata, 'date') and self.score.metadata.date is not None and self.score.metadata.date != 'None':
                self.metadata['date'] = int(self.score.metadata.date[:4])
            elif hasattr(self.score.metadata, 'dateCreated') and self.score.metadata.date is not None and self.score.metadata.dateCreated != 'None':
            # music21 v8 replaced date with dateCreated and date will be removed in v10
                self.metadata['date'] = int(self.score.metadata.dateCreated[:4])

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

    def _getFlatParts(self):
        """
        Return and store flat parts inside a piece using the score attribute.
        """
        if 'FlatParts' not in self.analyses:
            parts = self.score.getElementsByClass(stream.Part)
            self.analyses['FlatParts'] = [part.flatten() for part in parts]
        return self.analyses['FlatParts']

    def _getPartNames(self):
        """
        Return flat names inside a piece using the score attribute.
        """
        if 'PartNames' not in self.analyses:
            part_names = []
            name_set = set()
            for i, part in enumerate(self._getFlatParts()):
                name = part.partName or 'Part-' + str(i + 1)
                if name in name_set:
                    name = 'Part-' + str(i + 1)
                elif '_' in name:
                    print('\n*** Warning: it is problematic to have an underscore in a part name so _ was replaced with -. ***\n')
                    name = name.replace('_', '-')
                else:
                    name_set.add(name)
                part_names.append(name)
            self.analyses['PartNames'] = part_names
        return self.analyses['PartNames']

    def _getPartSeries(self):
        if 'PartSeries' not in self.analyses:
            part_series = []
            part_names = self._getPartNames()
            for i, flat_part in enumerate(self._getFlatParts()):
                notesAndRests = flat_part.getElementsByClass(['Note', 'Rest', 'Chord'])
                notesAndRests = [max(noteOrRest.notes) if noteOrRest.isChord else noteOrRest for noteOrRest in notesAndRests]
                ser = pd.Series(notesAndRests, name=part_names[i])
                ser.index = ser.apply(lambda noteOrRest: noteOrRest.offset)
                ser = ser[~ser.index.duplicated()]  # remove multiple events at the same offset in a given part
                part_series.append(ser)
            self.analyses['PartSeries'] = part_series
        return self.analyses['PartSeries']

    def _getPartNumberDict(self):
        '''
        Return a dictionary mapping part names to their numerical position on the staff,
        starting at 1 and counting from the highest voice.'''
        if 'PartNumberDict' not in self.analyses:
            parts = self._getPartNames()
            names2nums = {part: str(i + 1) for i, part in enumerate(parts)}
            self.analyses['PartNumberDict'] = names2nums
        return self.analyses['PartNumberDict']

    def numberParts(self, df):
        '''
        Return the passed df with the part names in the columns replaced with numbers
        where 1 is the highest staff. Works with single parts and multi-part column names.
        The df's column names are changed in place, so make a copy before calling this method
        if you don't want your original df to get changed.'''
        _dict = self._getPartNumberDict()
        cols = ['_'.join(_dict.get(part, part) for part in col.split('_')) for col in df.columns]
        res = df.copy()
        res.columns = cols
        return res

    def _getM21Objs(self):
        if 'M21Objs' not in self.analyses:
            part_names = self._getPartNames()
            self.analyses['M21Objs'] = pd.concat(self._getPartSeries(), names=part_names, axis=1, sort=True)
        return self.analyses['M21Objs']

    def _remove_tied(self, noteOrRest):
        if hasattr(noteOrRest, 'tie') and noteOrRest.tie is not None and noteOrRest.tie.type != 'start':
            return np.nan
        return noteOrRest

    def _getM21ObjsNoTies(self):
        if 'M21ObjsNoTies' not in self.analyses:
            df = self._getM21Objs().map(self._remove_tied).dropna(how='all')
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
        starts = col[(col != 'Rest') & (col.shift(1).isin(('Rest', None)))]
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
        consecutive non-NaN cells in each column.

        If you pass a df, it will sum
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
        This is needed to get the durations of ngrams.

        To get the durations of ngrams, pass the same value of n and the same
        dataframe you passed to .ngrams() as the `n` and `df` parameters,
        then pass your dataframe of ngrams as the `mask_df`. For example:

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
            mask = mask_df.map(lambda cell: True, na_action='ignore')
            result = result[mask]
        return result.dropna(how='all')

    def lyrics(self, strip=True):
        '''
        Return a dataframe of the lyrics associated with each note in the piece.
        If `strip` is True (default), then the lyrics will be stripped of leading
        and trailing whitespace and dashes. If `strip` is False, then the lyrics will
        be returned as they are in the score. Notes without lyrics are shown as NaN.
        '''
        key = ('Lyrics', strip)
        if key not in self.analyses:
            m21Objs = self._getM21ObjsNoTies()
            if strip:
                df = m21Objs.map(na_action='ignore',
                    func=lambda cell: cell.lyric.strip('\n \t-') if (cell.isNote and cell.lyric) else np.nan )
            else: 
                df = m21Objs.map(na_action='ignore',
                    func=lambda cell: cell.lyric if cell.isNote else np.nan)
            self.analyses[key] = df
        return self.analyses[key]

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
            df = self._getM21ObjsNoTies().map(self._noteRestHelper, na_action='ignore')
            self.analyses['Notes'] = df
        ret = self.analyses['Notes'].copy()
        if combineRests:
            ret = ret.apply(self._combineRests)
        if combineUnisons:
            ret = ret.apply(self._combineUnisons)
        return ret

    def _m21Expressions(self):
        '''
        Get all the expressions from music21. This includes fermatas, mordents, etc.
        '''
        if 'm21Expressions' not in self.analyses:
            df = self._getM21ObjsNoTies().map(lambda noteOrRest: noteOrRest.expressions, na_action='ignore')
            self.analyses['m21Expressions'] = df
        return self.analyses['m21Expressions']

    def fermatas(self):
        '''
        Get all the fermatas in a piece. A fermata is designated by a True value.
        '''
        if 'Fermatas' not in self.analyses:
            df = self._m21Expressions().map(
                lambda exps: any(isinstance(exp, expressions.Fermata) for exp in exps), na_action='ignore')
            self.analyses['Fermatas'] = df
        return self.analyses['Fermatas']

    def lowLine(self):
        '''
        Return a series that corresponds to the lowest sounding note of the piece at
        any given moment. Attack information cannot be reliably preserved so
        consecutive repeated notes and rests are combined. If all parts have a rest,
        then "Rest" is shown for that stretch of the piece.'''
        if 'LowLine' not in self.analyses:
            # use m21 objects so that you can do comparison with min
            notes = self._getM21ObjsNoTies()
            # you can't compare notes and rests, so replace rests with a really high note
            highNote = note.Note('C9')
            notes = notes.map(lambda n: highNote if n.isRest else n, na_action='ignore')
            notes.ffill(inplace=True)
            lowLine = notes.apply(min, axis=1)
            lowLine = lowLine.apply(lambda n: n.nameWithOctave)
            lowLine.replace('C9', 'Rest', inplace=True)
            lowLine.name = 'Low Line'
            self.analyses['LowLine'] = lowLine[lowLine != lowLine.shift()]
        return self.analyses['LowLine']

    def final(self):
        '''
        Return the final of the piece, defined as the lowest sounding note at
        the end of the piece.'''
        if 'Final' not in self.analyses:
            lowLine = self.lowLine()
            if len(lowLine.index):
                final = lowLine.iat[-1]
            else:
                final = None
            if final == 'Rest' and len(lowLine.index) > 1:
                final = lowLine.iat[-2]
            self.analyses['Final'] = final
        return self.analyses['Final']

    def highLine(self):
        '''
        Return a series that corresponds to the highest sounding note of the piece at
        any given moment. Attack information cannot be reliably preserved so
        consecutive repeated notes and rests are combined. If all parts have a rest,
        then "Rest" is shown for that stretch of the piece.'''
        if 'HighLine' not in self.analyses:
            # use m21 objects so that you can do comparison with min
            notes = self._getM21ObjsNoTies()
            # you can't compare notes and rests, so replace rests with a really high note
            lowNote = note.Note('C', octave=-9)
            notes = notes.map(lambda n: lowNote if n.isRest else n, na_action='ignore')
            notes.ffill(inplace=True)
            highLine = notes.apply(max, axis=1)
            highLine = highLine.apply(lambda n: n.nameWithOctave)
            highLine.replace('C-9', 'Rest', inplace=True)
            highLine.name = 'High Line'
            self.analyses['HighLine'] = highLine[highLine != highLine.shift()]
        return self.analyses['HighLine']

    def _emaRowHelper(self, row):
        measures = list(range(row.iat[0], row.iat[2] + 1))
        mCount = row.iat[2] - row.iat[0] + 1
        parts = row.iloc[4:].dropna().index
        part_strings = '+'.join({part for combo in parts for part in combo.split('_')})
        num_parts = part_strings.count('+') + 1

        beats = []
        for meas in measures:
            if meas == row.iat[0] and meas == row.iat[2]:
                beats.append('+'.join(['@{}-{}'.format(row.iat[1], row.iat[3])]*num_parts))
            elif meas == row.iat[0]:  # meas < row.iat[2]
                beats.append('+'.join(['@{}-end'.format(row.iat[1])]*num_parts))
            elif meas > row.iat[0] and meas < row.iat[2]:
                beats.append('+'.join(['@all']*num_parts))
            else: # meas > row.iat[0] and meas == row.iat[2]
                beats.append('+'.join(['@start-{}'.format(row.iat[3])]*num_parts))

        post = ['{}-{}'.format(row.iat[0], row.iat[2]), # measures
            ','.join([part_strings]*mCount),    # parts
            ','.join(beats)]                    # beats
        return '/'.join(post)

    def combineEmaAddresses(self, emas):
        '''
        Given a list of EMA addresses, `emas`, return a single ema address that combines them into one.
        '''
        if isinstance(emas, str):
            return emas
        if len(emas) == 1:
            return emas[0]
        chunks = []
        num_parts = len(self._getPartNames())
        last_m = self.measures().iat[-1, 0]
        for ema in emas:
            ema = ema.replace('start', '1')
            _measures, _parts, _beats = ema.split('/')
            _beats = _beats.replace('1.0-', '1-')
            _beats = _beats.replace('1.0@', '1@')
            measures, parts, beats = _measures.split(','), _parts.split(','), _beats.split(',') 
            for i, meas in enumerate(measures):
                # handle measures
                if meas == 'all':
                    meas == '1-{}'.format(last_m)  # measures 1 through the final measure
                meas = meas.replace('end', str(last_m))
                if '-' in meas:   # this is a measure range, e.g. 9-12
                    start, end = meas.split('-')
                    ms = [str(m) for m in range(int(start), int(end) + 1)]
                    meas = ms[0]
                    measures[i+1:i+1] = ms[1:]
                # handle beats
                if beats[i] == '@all' or beats[i] == '@1-end':
                    bs = '@all'
                else:
                    bs = beats[i].split('+')
                # handle parts
                if parts[i] == 'all':
                    ps = [str(x) for x in range(1, num_parts + 1)]
                else:
                    ps = parts[i].replace('end', str(num_parts))
                    ps = ps.split('+')
                    for _j, _p in enumerate(ps):
                        if '-' in _p:
                            start, end = _p.split('-')
                            if end == 'end':
                                end = num_parts
                            parts_in_range = [str(part) for part in range(int(start), int(end) + 1)]
                            for part in parts_in_range:
                                if isinstance(bs, str):
                                    chunks.append((meas, part, bs))
                                else:
                                    chunks.append((meas, part, bs[_j]))
                        if isinstance(bs, str):
                            chunks.append((meas, _p, bs))
                        else:
                            chunks.append((meas, _p, bs[_j]))
                                    
        # collect the beats for the addresses at the same measure and part
        mp2bs = {}
        for chunk in chunks:
            key = (chunk[0], chunk[1])
            if key not in mp2bs:
                mp2bs[key] = [chunk[2]]
            else:
                mp2bs[key].append(chunk[2])

        # combine the beats into one for each measure-part combo
        slices = [(*mp, '@all') if '@all' in bs else (*mp, ''.join(set(bs))) for mp, bs in mp2bs.items()]
        # sort by part number, then by measure so the slices are ordered by measure then part number
        df = pd.DataFrame(slices, columns=['Measure', 'Part', 'Beat']).sort_values(['Measure', 'Part'])
        mpost = df.Measure.unique()
        ppost = ','.join(['+'.join(df.loc[df.Measure == _m, 'Part']) for _m in mpost])
        bpost = ','.join(['+'.join(df.loc[df.Measure == _m, 'Beat']) for _m in mpost])
        mpost = ','.join(mpost)
        return '/'.join((mpost, ppost, bpost))

    def _hr_helper(self, row, ngrams):
        this_hr = row["Offset"]
        ret = ngrams.loc[[this_hr]]
        full_ema = self.emaAddresses(df=ret, mode='')
        full_ema = full_ema.reset_index()
        ema = full_ema['EMA']
        return ema

    def _ptype_ema_helper(self, row, ngrams):
        # initialize dict and df
        dictionary = {}
        filtered_df = pd.DataFrame()
        # get row values for offsets and voices
        offsets = row['Offsets']
        voices = row['Voices']
        # make dict
        for f, s in zip(offsets, voices):
            if f not in dictionary:
                dictionary[f] = []
            dictionary[f].append(s)
        # slice of ngrams corresponding to this point
        short_ngrams = ngrams.loc[offsets]
        # use dict values to build offset and column sets
        for offset, voice_list in dictionary.items():
            columns_to_replace = short_ngrams.columns.difference(voice_list)
            # Replace the values with NaN
            # updated 4/24 to remove repeating voice error
            short_ngrams.loc[offset, columns_to_replace] = np.nan
            short_ngrams.dropna(how='all', inplace=True)
        emas = self.emaAddresses(df=short_ngrams, mode='')
        complete_ema = self.combineEmaAddresses(emas)
        return complete_ema

    def emaAddresses(self, df=None, mode=''):
        '''
        Return a df that's the same shape as the passed df. Currently only works for 1D ngrams,
        like melodic ngrams. The `mode` parameter is detected automatically if it isn't passed.

        ***Example***
        mel = piece.melodic()
        ng = piece.ngrams(df=mel, n=4, offsets='both')
        ema = piece.emaAddresses(df=ng)
        ***
        '''
        if isinstance(df, pd.DataFrame):
            ret = df.copy()
        if mode == 'melodic':
            newCols = []
            for i in range(len(ret.columns)):
                part = ret.iloc[:, i].dropna()
                notes = self.notes().loc[:, part.name].dropna()
                new_index = []
                for (_first, _last) in part.index:
                    new_index.append((notes.loc[:_first].index[-2], _last))
                part.index = pd.MultiIndex.from_tuples(new_index, names=part.index.names)
                newCols.append(part)
            ret = pd.concat(newCols, axis=1, sort=True)
        elif mode.startswith('c'):  # cadences/cvfs mode
            ret = self.cvfs(keep_keys=True, offsets='both').copy()
            ngrams = ret.iloc[:, len(self._getPartNames()):]
            addresses = self.emaAddresses(df=ngrams, mode='')
            if isinstance(df, pd.DataFrame) and ('First' in df.index.names and 'Last' in df.index.names):
                return addresses
            else:
                uni = addresses.index.levels[-1].unique()
                ret = pd.Series(index=uni, name='EMA').astype(str)
                for un in uni:
                    val = self.combineEmaAddresses(addresses.loc[(slice(None), un)].to_list())
                    ret.at[un] = val
                return ret
        # hr mode--works with HR dataframe, adding ema address to each hr passage (= row).  
        # pass in output of hr = piece.homorhythm() as the df and set mode = 'hr'
        elif mode == 'homorhythm': # hr mode
            if isinstance(df, pd.DataFrame):
                hr = df.copy()
                ngram_length = int(hr.iloc[0]['ngram_length'])
                nr = self.notes()
                dur = self.durations(df = nr)
                ngrams = self.ngrams(df = dur, n = ngram_length, offsets = 'both', exclude=[])
                hr = hr.reset_index()
                hr['ema'] = hr.apply(lambda row: self._hr_helper(row, ngrams), axis=1)
                hr.set_index(['Measure', 'Beat', 'Offset'], inplace=True)
                return hr  
        # for ptypes output
        # pass in output of p_types = piece.presentationTypes() as the df and set mode = 'p_types'
        elif mode == 'p_types': # p_type mode
            if isinstance(df, pd.DataFrame):
                p_types = df.copy()
                ngram_length = len(p_types.iloc[0]['Soggetti'][0])
                mel = self.melodic(end=False)
                ngrams = self.ngrams(df = mel, offsets = 'both', n = ngram_length)
                p_types['ema'] = p_types.apply(lambda row: self._ptype_ema_helper(row, ngrams), axis=1)
                return p_types
        
        if isinstance(df, pd.DataFrame):
            if len(df) >= 1:
                idf = ret.index.to_frame()
                _measures = self.measures().iloc[:, 0]
                measures = idf.map(lambda i: _measures.loc[:i].iat[-1])
                _beats = self.beatIndex()
                beats = idf.map(lambda i: _beats[i])
                res = pd.concat([measures['First'], beats['First'], measures['Last'], beats['Last']], axis=1, sort=True)
                res.columns = ['First Measure', 'First Beat', 'Last Measure', 'Last Beat']
                ret = self.numberParts(ret)
                res = pd.concat([res, ret], axis=1, sort=True)
                res = res.apply(self._emaRowHelper, axis=1)
                res.name = 'EMA'
                return res

    def linkExamples(self, df, piece_url='', mode=''):
        '''
        Given a dataframe of EMA addresses, return a dataframe of clickable
        links to the EMA React app. The `piece_url` parameter is the URL of the
        piece on the EMA React app. If you don't pass a `piece_url`, the method
        will try to construct one based on the piece's metadata. The resulting
        dataframe will have the same data results, but instead of plain text
        they will be links to highlighted examples of each result.
        '''
        if piece_url == '':
            if self.path.startswith('https://'):
                piece_url = self.path
            else:
                print('No piece URL was passed and the piece was not downloaded from a public respository. Please provide a piece_url.')
                return

        if mode != '':
            mode = mode.lower()
        else:   # detect mode if it is not passed
            if 'hr_voices' in df.columns:
                mode = 'homorhythm'
                data_col_name = 'hr_voices'
                ema = pd.DataFrame(self.emaAddresses(df, mode=mode)['ema'])
            elif 'Presentation_Type' in df.columns:
                mode = 'p_types'
                data_col_name = 'Presentation_Type'
                ema = pd.DataFrame(self.emaAddresses(df, mode=mode)['ema'])
            elif 'CVFs' in df.columns:
                mode = 'cadences'
                data_col_name = 'CadType'
                ema = pd.DataFrame(self.emaAddresses(df, mode=mode))
            elif all(self._getPartNames() == df.columns):
                if any(char in df.values for char in 'CAyca'):
                    print('Running on cadences which have the same ema addresses as cvfs...')
                    return self.linkExamples(self.cadences(), piece_url)
                else:
                    mode = 'melodic'

        fmt = '<a href="{}&{}" rel="noopener noreferrer" target="_blank">{}</a>'
        if mode == 'melodic':
            res = []
            # this loop is needed because the "last" offset of df is the beginning
            # of it's last event, whereas in temp it's the beginning of the next event
            for col in range(len(df.columns)):
                col_urls = pd.DataFrame(self.emaAddresses(df.take([col], axis=1), mode=mode).dropna())
                col_urls = col_urls.map(ImportedPiece._constructColumnwiseUrl, na_action='ignore', piece_url=piece_url)
                col_data = df.iloc[:, col].dropna()
                links = [] if col_data.empty else [fmt.format(url,
                                                              urllib.parse.urlencode({'observation': f' {col_data.iat[ii]}'}),
                                                              col_data.iat[ii])
                                                   for ii, url in enumerate(col_urls['EMA'])]
                col_links = pd.Series(links, name=col_data.name, index=col_data.index)   # use df's index vals
                res.append(col_links)
            res = pd.concat(res, axis=1, sort=True)
        else:
            col_urls = ema.map(lambda cell: ImportedPiece._constructColumnwiseUrl(cell, piece_url), na_action='ignore')
            col_data = df.loc[:, data_col_name]
            links = [fmt.format(col_urls.iat[col_urls.index.get_loc(ndx), 0],
                                urllib.parse.urlencode({'observation': f' {col_data.at[ndx]}'}),
                                col_data.at[ndx])
                    if isinstance(col_data.at[ndx], (str, list)) else np.nan for ndx in col_data.index]
            res = df.copy()
            res[data_col_name] = links
            if 'ema' in res.columns:
                res.drop(columns='ema', inplace=True)
        display(HTML(res.to_html(render_links=True, escape=False)))

    def _constructColumnwiseUrl(cell, piece_url):
        ema_expression = ''.join(("/", cell, "/highlight"))
        ema_measures = re.findall(r'\d+', cell.split("/", 1)[0])
        ema_measure_integers = [int(x) for x in ema_measures]
        min_meas = min(ema_measure_integers)
        max_meas = max(ema_measure_integers)
        mr = f"{min_meas}-{max_meas}"
        # not needed as of 4/24
        # measure_range = {"measureRange": mr}
        # json_string = json.dumps(measure_range)
        # encoded_mr = urllib.parse.quote(json_string)
        params = {
            "pieceURL": piece_url,
            "ema_expression": ema_expression,
            "measure_range": mr
        }
        query_string = urllib.parse.urlencode(params)
        react_app_url = "https://eleon024.github.io/ema_react_app/"
        url = ''.join((react_app_url, '?', query_string))
        return url

    def _getBeatUnit(self):
        '''
        Return a dataframe of the duration of the beat for each time signature
        object in the piece. The duration is expressed as a float where 1.0 is
        a quarter note, 0.5 is an eighth note, etc. This is useful for
        calculating the beat strength of notes and rests.
        '''
        tsigs = self._getM21TSigObjs()
        tsigs.columns = self._getPartNames()
        df = tsigs.map(lambda tsig: tsig.beatDuration.quarterLength, na_action='ignore')
        return df

    def beats(self):
        '''
        Return a table of the beat positions of all the notes and rests.

        Beats are expressed as floats. The downbeat of each measure is 1.0, and
        all other metric positions in a measure are given smaller numbers
        approaching zero as their metric weight decreases. Results from this
        method should not be sent to the regularize method.
        '''
        if 'Beats' not in self.analyses:
            nr = self.notes()
            nrOffs = nr.apply(lambda row: row.index)
            ms = self.measures().apply(lambda row: row.index)
            temp = pd.concat([ms, nr], axis=1, sort=True)
            ms = temp.iloc[:, :len(ms.columns)].ffill()
            ms = ms[nr.notnull()]
            offFromMeas = nrOffs - ms
            beatDur = self._getBeatUnit()
            temp = pd.concat([beatDur, nr], axis=1, sort=True)
            beatDur = temp.iloc[:, :len(beatDur.columns)].ffill()
            beatDur = beatDur[nr.notnull()]
            self.analyses['Beats'] = (offFromMeas / beatDur) + 1
        return self.analyses['Beats']

    def beatIndex(self):
        '''
        Return a series of the first valid value in each row of .beats().

        This is useful for getting the beat position of a given timepoint (i.e.
        index value) in the piece. Results from this method should not be sent to
        the regularize method. You would use this method to lookup the beat
        position of a given offset (timepoint) in a piece. Provided there is a
        note or rest in any voice at that offset, the beatIndex results will
        have a value at that index.
        '''
        if 'BeatIndex' not in self.analyses:
            ser = self.beats().dropna(how='all').apply(lambda row: row.dropna().iat[0], axis=1)
            self.analyses['BeatIndex'] = ser
        return self.analyses['BeatIndex']

    def detailIndex(self, df, measure=True, beat=True, offset=False, t_sig=False,
        sounding=False, progress=False, lowest=False, highest=False, _all=False):
        '''
        Return the passed dataframe with a multi-index of any combination of the
        measure, beat, offset, prevailing time signature, and progress towards
        the end of the piece (0-1) in the index labels. At least one must be
        chosen, and the default is to have measure and beat information, but no
        other information. Here are all the boolean parameters that default to False,
        but that you can set to true if you also want to see them:

        * offset: row's offset (distance in quarter notes from beginning, 1.0 = one quarter note)
        * t_sig: the prevailing time signature
        * sounding: how many voices are sounding (i.e. not resting) at this point
        * progress: 0-1 how far along in the piece this moment is, 0 = beginning, 1 = last attack onset
        * lowest: the lowest sounding note at this moment
        * highest: the highest sounding note at this moment

        You can also pass _all=True to include all five types of index information.
        '''
        cols = [df]
        names = []
        if _all:
            measure, beat, offset, t_sig, sounding, progress, lowest, highest = [True] * 8
        if measure:
            cols.append(self.measures().iloc[:, 0])
            names.append('Measure')
        if beat:
            cols.append(self.beatIndex())
            names.append('Beat')
        if offset:
            cols.append(df.index.to_series())
            names.append('Offset')
        if t_sig:
            cols.append(self.timeSignatures().iloc[:, 0])
            names.append('TSig')
        if sounding:
            cols.append(self.soundingCount())
            names.append('Sounding')
        if progress:
            prog = (df.index / self.notes().index[-1]).to_series()
            prog.index = df.index
            cols.append(prog)
            names.append('Progress')
        if lowest:
            cols.append(self.lowLine())
            names.append('Lowest')
        if highest:
            cols.append(self.highLine())
            names.append('Highest')
        temp = pd.concat(cols, axis=1, sort=True)
        temp2 = temp.iloc[:, len(df.columns):].ffill()
        if measure:
            temp2.iloc[:, 0] = temp2.iloc[:, 0].astype(int)
        mi = pd.MultiIndex.from_frame(temp2, names=names)
        ret = temp.iloc[:, :len(df.columns)].copy()
        ret.index = mi
        ret.dropna(inplace=True, how='all')
        ret.sort_index(inplace=True)
        return ret

    def di(self, df, measure=True, beat=True, offset=False, t_sig=False, sounding=False,
        progress=False, lowest=False, highest=False, _all=False):
        """
        Convenience shortcut for .detailIndex. See that method's documentation for instructions.
        """
        return self.detailIndex(df=df, measure=measure, beat=beat, offset=offset, t_sig=t_sig,
            sounding=sounding, progress=progress, lowest=lowest, highest=highest, _all=_all)

    def _beatStrengthHelper(self, noteOrRest):
        '''
        Return the beat strength of a note or rest.

        This follows the music21 conventions where the downbeat is equal to 1, and
        all other metric positions in a measure are given smaller numbers approaching
        zero as their metric weight decreases.
        '''
        if hasattr(noteOrRest, 'beatStrength'):
            return noteOrRest.beatStrength
        return noteOrRest

    def beatStrengths(self):
        '''
        Returns a table of the beat strengths of all the notes and rests in
        the piece. This follows the music21 conventions where the downbeat is
        equal to 1, and all other metric positions in a measure are given
        smaller numbers approaching zero as their metric weight decreases.
        Results from this method should not be sent to the regularize method.
        '''
        if 'BeatStrength' not in self.analyses:
            df = self._getM21ObjsNoTies().map(self._beatStrengthHelper)
            self.analyses['BeatStrength'] = df
        return self.analyses['BeatStrength']

    def _getM21TSigObjs(self):
        '''
        Return a dataframe of the time signature objects in the piece.

        This is useful for getting the prevailing time signature at any given
        moment in the piece.
        '''
        if 'M21TSigObjs' not in self.analyses:
            tsigs = []
            for part in self._getFlatParts():
                tsigs.append(pd.Series({ts.offset: ts for ts in part.getTimeSignatures()}))
            df = pd.concat(tsigs, axis=1, sort=True)
            self.analyses['M21TSigObjs'] = df
        return self.analyses['M21TSigObjs']

    def timeSignatures(self):
        """
        Return a data frame containing the time signatures and their offsets.

        This is useful for getting the prevailing time signature at any given
        moment in the piece. The time signature is expressed as a string taken
        from music21's .ratioString attribute. For example, 4/4 time is
        expressed as "4/4", 3/4 time is expressed as "3/4", etc.
        """
        if 'TimeSignature' not in self.analyses:
            df = self._getM21TSigObjs()
            df = df.map(lambda ts: ts.ratioString, na_action='ignore')
            df.columns = self._getPartNames()
            self.analyses['TimeSignature'] = df
        return self.analyses['TimeSignature']

    def measures(self):
        """
        This method retrieves the offsets of each measure in each voice.

        Measures are expressed as integers.
        """
        if "Measure" not in self.analyses:
            parts = self._getFlatParts()
            partMeasures = []
            for part in parts:
                partMeasures.append(pd.Series({m.offset: m.measureNumber \
                    for m in part.makeMeasures().getElementsByClass(['Measure'])}))
            df = pd.concat(partMeasures, axis=1, sort=True)
            df.columns = self._getPartNames()
            self.analyses["Measure"] = df
        return self.analyses["Measure"]

    def barlines(self):
        """
        This method retrieves some of the barlines. It's not clear how music21
        picks them, but this seems to get all the double barlines which helps
        detect section divisions.
        """
        if "Barline" not in self.analyses:
            parts = self._getFlatParts()
            partBarlines = []
            for part in parts:
                partBarlines.append(pd.Series({b.offset: b.type \
                    for b in part.getElementsByClass(['Barline'])}))
            df = pd.concat(partBarlines, axis=1, sort=True)
            df.columns = self._getPartNames()
            self.analyses["Barline"] = df
        return self.analyses["Barline"]

    def soundingCount(self):
        """
        Return a series with the number of parts that currently sounding.

        This information is included the .cadences method so you can filter cadence
        results based on how many voices are sounding at the time of the cadence.
        It is also available in the .detailIndex method to add this information to
        almost any dataframe CRIM-Intervals provides.
        """
        if not 'SoundingCount' in self.analyses:
            nr = self.notes().ffill()
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
        if hasattr(row.iat[1], 'isRest') and hasattr(row.iat[0], 'isRest'):
            if row.iat[1].isRest or row.iat[0].isRest:
                return 'Rest'
            elif row.iat[1].isNote and row.iat[0].isNote:
                return interval.Interval(row.iat[0], row.iat[1])
        return np.nan

    def _melodicIntervalHelper(row):
        if hasattr(row.iat[0], 'isRest'):
            if row.iat[0].isRest:
                return 'Rest'
            elif row.iat[0].isNote and hasattr(row.iat[1], 'isNote') and row.iat[1].isNote:
                return interval.Interval(row.iat[1], row.iat[0])
        return np.nan

    def _melodifyPart(ser, end):
        '''
        Convert a series of music21 notes or rests to melodic intervals.

        If end is True, the intervals will be from the end of the note to the start
        of the next note. If end is False, the intervals will be from the start of
        the note to the start of the next note.
        '''
        ser.dropna(inplace=True)
        shifted = ser.shift(1) if end else ser.shift(-1)
        partDF = pd.concat([ser, shifted], axis=1, sort=True)
        if end:
            res = partDF.apply(ImportedPiece._melodicIntervalHelper, axis=1).dropna()
        else:  # not a typo, this uses _harmonicIntervalHelper if end == False
            res = partDF.apply(ImportedPiece._harmonicIntervalHelper, axis=1).dropna()
        return res

    def _strToM21Obj(cell):
        '''
        Convert a df cell from a string to a music21 note or rest. NAs are ignored.'''
        if cell == 'Rest':
            return note.Rest()
        return note.Note(cell)

    def _getM21MelodicIntervals(self, end, df):
        key = 'M21MelodicIntervals' + 'End' if end else 'Start'
        if key not in self.analyses or df is not None:
            if df is None:
                m21Objs = self._getM21ObjsNoTies()
            else:
                m21Objs = df.map(ImportedPiece._strToM21Obj, na_action='ignore')
            _df = m21Objs.apply(ImportedPiece._melodifyPart, args=(end,))
            if df is not None:
                return _df
            self.analyses[key] = _df
        return self.analyses[key]

    def _getRegularM21MelodicIntervals(self, unit):
        m21Objs = self._getM21ObjsNoTies()
        m21Objs = self.regularize(m21Objs, unit=unit)
        return m21Objs.apply(ImportedPiece._melodifyPart, args=(True,))

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

    def _durationalRatioHelper(self, row, end):
        _row = row.dropna()
        res = _row / _row.shift(1)
        if not end:
            res = res.shift(-1)
        return res

    def durationalRatios(self, df=None, end=True):
        '''
        Return durational ratios of each item in each column compared to the
        previous item in the same column. If a df is passed, it should be of
        float or integer values. If no df is passed, the default results from
        .durations will be used as input (durations of notes and rests).

        The `end` parameter works the same as for .melodic(). It associates the
        durational ratios with the start of the first event rather than with the
        start of the second event.
        '''
        cachable = False
        key = ('DurationalRatios', end)
        if df is None:
            cachable = True
            if key in self.analyses:
                return self.analyses['DurationalRatios']
            df = self.durations()
        res = df.apply(self._durationalRatioHelper, args=(end,)).dropna(how='all')
        if cachable:
            self.analyses['DurationalRatios'] = res
        return res

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

        If you don't pass a value for df, you can specify a different value
        for n to change from the default of 3:

        importedPiece.distance(n=5)


        If you already have the melodic ngrams calculated for a different
        aspect of your query, you can pass that as df to save a little
        runtime on a large query. Note that if you pass something for df,
        the n parameter will be ignored:

        mel = importedPiece.melodic('z', True, True)
        ngrams = importedPiece.ngrams(df=mel, n=4, exclude=['Rest'])
        importedPiece.distance(df=ngrams)

        To search the table for the distances from a given pattern, just get
        the column of that name. This is example looks for distances
        involving a melodic pattern that goes up a step, down a third, up a
        step, down a third:

        dist = importedPiece.distance(n=4)
        target = '1, -2, 1, -2'
        col = dist[target]

        If you then want to filter that column, say to distances less than or
        equal to 2, do this:

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
        dist = pd.concat(cols, axis=1, sort=True)
        dist.columns = uni
        dist.index = uni
        return dist

    # July 2022 helper for flexed entries
    def _flexed_sum(self, item, head_flex):
        if item[0] <= head_flex:
            item[0] = 0
        return sum(item)

    # July 2022 helper for flexed entries updated
    def flexed_distance(self, head_flex, df=None, n=3):
          '''
          Return the distances between all the values in df which should be a
          dataframe of strings of integer ngrams. Specifically, this is meant for
          0-indexed, directed, and compound melodic ngrams. If nothing is passed
          for df, melodic ngrams of this type will be provided at the value of n
          passed. An alternative that would make sense would be to use chromatic
          melodic intervals instead.

          This function differs from "distance" in that it treats the first item in
          each ngram differently from the others.  That is, the first item can "flex"
          differently from the remainder.  Thus users can choose a overal body_flex
          of "0" while still allowing flexing only at the head of the ngram.

          The default flex is up to "1" unit of difference, but passing the "head_flex"
          argument allows users to set their own threshold.

          This function is meant mainly for melodic ngrams, but it can also be used
          for durational ngrams.

          Usage:

          # Call like this:
          importedPiece.flexed_distance()

          # If you don't pass a value for df, you can specify a different value
          # for n to change from the default of 3:
          importedPiece.flexed_distance(n=5)

          # If you already have the melodic ngrams calculated for a different
          # aspect of your query, you can pass that as df to save a little
          # runtime on a large query. Note that if you pass something for df,
          # the n parameter will be ignored:
          mel = importedPiece.melodic('z', True, True)
          ngrams = importedPiece.ngrams(df=mel, n=4, exclude=['Rest'])
          importedPiece.flexed_distance(df=ngrams)

          # To search the table for the distances from a given pattern, just get
          # the column of that name. This is example looks for distances
          # involving a melodic pattern that goes up a step, down a third, up a
          # step, down a third:
          dist = importedPiece.flexed_distance(n=4)
          target = '1, -2, 1, -2'
          col = dist[target]

          # If you then want to filter that column, say to flexed distances less than or
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
          cols = [(df - df.loc[i]).abs().apply(self._flexed_sum, axis=1, args=(head_flex,)) for i in df.index]
          dist = pd.concat(cols, axis=1, sort=True)
          dist.columns = uni
          dist.index = uni
          return dist

    def melodic(self, kind='q', directed=True, compound=True, unit=0, end=True, df=None):
        '''
        Return melodic intervals for all voice pairs. Each melodic interval
        is associated with the starting offset of the second note in the
        interval.

        * To associate intervals with the offset of the first notes,
        pass end=False.

        * If you want melodic intervals measured at a regular
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
            _df = _df.map(self._intervalMethods[settings], na_action='ignore')
            if kind == 'z':
                _df = _df.map(ImportedPiece._zeroIndexIntervals, na_action='ignore')
            if unit or df is not None:
                return _df
            else:
                self.analyses[key] = _df
        return self.analyses[key]

    def _patternToSeries(self, pattern):
        output_list = []
        output_list.append(0)
        output_list.append(pattern[0])
        for i in range(1, len(pattern)):
            output_list.append(sum(pattern[0:i]) + pattern[i])
        return output_list

    def _createGraphList(self, pattern_list):
        '''
        helper function for graphing interval families
        '''
        graph_list = []
        for item in pattern_list:
            if isinstance(item, tuple):
                temp_item = list(map(lambda x: int(x), item))
            elif isinstance(item, str):
                temp_item = list(map(lambda x: int(x), item.split(', ')))
            else:
                print("Intervals are not of type: String or Tuple")
                return None
            graph_list.append(self._patternToSeries(temp_item))
        return graph_list

    # do we need to set a default length for the following?
    # is the typical use code correct? Do we pass in piece?
    def graphIntervalFamilies(self, length=4, combineUnisons=True, kind="d", end=False, variableLength=False, suggestedPattern=None, useEntries=True, arriveAt=None, includeLegend=False):

        '''
        It is possible to select:

        length=4
        combineUnisons=True
        kind="d"
        end=False
        variableLength=False
        suggestedPattern=None
        useEntries=True

        Graphing the Interval Families with `length=4` and `useEntries=True` by default:

        Typical use:
        graphIntervalFamilies()

        Another useful option is `variableLength=True`, therefore including **all unique patterns up to the specified length**:

        graphIntervalFamilies(length=4, variableLength=True)

        We can narrow down patterns of interested by specifying `suggestedPattern=Tuple(Str*)`, for example looking for **all patterns that start with `-2, -2`**:

        graphIntervalFamilies(length=4, variableLength=True, suggestedPattern=("4", "2"))

        '''
        # runs sns plot layout
        self._plot_default()

        local_ngrams = pd.DataFrame(columns=self.notes().columns)

        if length < 1:
            print("Please use length >= 1")
            return None

        if kind not in ["d", "z", "c"]:
            print("\n Warning: you might encounter an error due to using an uncommon interval kind. \n Currently, we have been working with \"z\", \"d\", and \"c\"")

        if variableLength:
            loop_start = 1
        else:
            loop_start = length

        for i in range(loop_start, length + 1):
            loop_notes = self.notes(combineUnisons=True)
            loop_melodic = self.melodic(df=loop_notes, kind=kind, end=end)
            if useEntries:
                loop_ngrams = self.entries(df=loop_melodic, n=int(i), exclude=["Rest"]).fillna('')
            else:
                loop_ngrams = self.ngrams(df=loop_melodic, exclude=["Rest"], n=int(i)).fillna('')
            local_ngrams = pd.concat([local_ngrams, loop_ngrams], sort=True)

        total_unique_ngrams_list = list(filter(lambda x: x != "", list(set(local_ngrams.values.flatten().tolist()))))

        if suggestedPattern:
            matching_unique_ngrams_list = list(map(lambda x: x if ",".join(x).startswith(",".join(suggestedPattern)) else "", total_unique_ngrams_list))
            total_unique_ngrams_list = list(filter(lambda x: x != "", matching_unique_ngrams_list))
            if len(total_unique_ngrams_list) < 1:
                print("No patterns matching the suggestedPattern found")
                return None

        graph_pattern_list = self._createGraphList(total_unique_ngrams_list)

        if arriveAt != None:
            graph_pattern_list = list(filter(lambda x: x[-1] == arriveAt, graph_pattern_list))
            if len(graph_pattern_list) < 1:
                print("No patterns arriving at arriveAt found")
                return None

        for pattern in graph_pattern_list:
            plt.plot(pattern, alpha=0.35, lw=6)
        plt.yticks(np.arange(min(list(map(lambda x: sorted(x)[0], graph_pattern_list))) - 1, max(list(map(lambda x: sorted(x)[-1], graph_pattern_list))) + 1, 1.0))
        plt.xticks(np.arange(0, max(list(map(lambda x: len(x), graph_pattern_list))), 1.0))
        if includeLegend:
            plt.title("Total Number of Patterns: " + str(len(graph_pattern_list)) + "\n Piece Name: " + self.metadata["title"])
        plt.show()


    def _getM21HarmonicIntervals(self, againstLow=False, df=None):
        """
        Return m21 interval objects for every pair of intervals in the piece.

        This does all pairs between voices if againstLow is False (default) or
        each voice against the lowest sounding note if againstLow is True.
        """
        key = ('M21HarmonicIntervals', againstLow)
        if key not in self.analyses:
            if df is None:
                m21Objs = self._getM21ObjsNoTies()
            else:
                sampleVal = df.stack(future_stack=True).dropna().iat[0]
                if isinstance(sampleVal, str):
                    m21Objs = df.map(ImportedPiece._strToM21Obj, na_action='ignore')
                else:
                    m21Objs = df
            pairs = []
            if againstLow:
                low = self.lowLine()
                if df is not None:
                    low = low.loc[df.index[0]: df.index[-1]]
                low = low.apply(lambda val: note.Note(val) if val != 'Rest' else note.Rest())
                lowIndex = len(m21Objs.columns)
                combos = [(lowIndex, x) for x in range(len(m21Objs.columns))]
                m21Objs = pd.concat([m21Objs, low], axis=1)
            else:
                combos = combinations(range(len(m21Objs.columns) - 1, -1, -1), 2)
            for combo in combos:
                df = m21Objs.iloc[:, list(combo)].dropna(how='all').ffill()
                ser = df.apply(ImportedPiece._harmonicIntervalHelper, axis=1)
                # name each column according to the voice names that make up the intervals, e.g. 'Bassus_Altus'
                ser.name = '_'.join((m21Objs.columns[combo[0]], m21Objs.columns[combo[1]]))
                pairs.append(ser)
            if pairs:
                ret = pd.concat(pairs, axis=1, sort=True)
            else:
                ret = pd.DataFrame()

            self.analyses[key] = ret
        return self.analyses[key]

    def harmonic(self, kind='q', directed=True, compound=True, againstLow=False, df=None):
        '''
        Return harmonic intervals for all voice pairs.

        The voice pairs are named with the voice that's lower on the staff given first,
        and the two voices separated with an underscore, e.g. "Bassus_Tenor". If againstLow
        is True, intervals will be measured against the lowest sounding note.

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
        :param bool againstLow: if False (default) harmonic intervals between
            all pairs of voices will be returned. If True harmonic intervals of
            each voice against the lowest sounding note at each moment is returned.
        :param pandas DataFrame df: None (default) is the standard behavior. Pass a
            df of note and rest strings or music21 objects to calculate the harmonic
            interals in any dataframe.
        :returns: `pandas.DataFrame` of harmonic intervals in each pair in the
            format specified by the `kind`, `directed`, and `compound` parameters.
        '''
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, directed, compound)
        key = ('HarmonicIntervals', kind, directed, compound, againstLow)
        if df is not None or key not in self.analyses:
            _df = self._getM21HarmonicIntervals(againstLow, df)
            _df = _df.map(self._intervalMethods[settings], na_action='ignore')
            if kind == 'z':
                _df = _df.map(ImportedPiece._zeroIndexIntervals, na_action='ignore')
            _df = _df.sort_index()
            if df is not None:
                self.analyses[key] = _df
            else:
                return _df
        return self.analyses[key]
    
    def sonorities(self, kind='d', directed=True, compound='simple', sort=True):
        """
        Return a dataframe of sonorities that are similar to a continuo part but not reduced.

        There is a sonority observed every time any part in the piece has an attack. The
        `kind`, `directed`, and `compound` parameters are passed unchanged to .harmonic and
        will control the type of intervals used. In all cases Rests are ignored. `sort` will
        sort the values before returning them, and remove duplicates as well as any unisons
        against the lowest line.
        """
        har = self.harmonic(kind=kind, directed=directed, compound=compound, againstLow=True).ffill()
        if sort:
            son = har.apply(lambda row: '/'.join(sorted([note for note in row.unique() if note != 'Rest'], reverse=True)[:-1]), axis=1)
        else:
            son = har.apply(lambda row: '/'.join([note for note in row.unique() if note != 'Rest']), axis=1)
        son.name = 'Sonority'
        return pd.DataFrame(son)

    def _entry_ngram_helper(self, n):
        """
        This private method is used by the moduleFinder function, which compares
        shared modules across pieces in a corpus.

        The method finds the entries, then uses these locations to determine
        the contrapuntal modules that occur in those places.  Of course the
        contrapuntal modules involve all voices active at given moment, and so not all of them will be the result of the entries themselves.

        """
        entries = self.entries()
        cols = entries.columns.to_list()
        modules = self.ngrams(n=n, held='1', exclude=[], show_both=True)
        combined = entries.join(modules)
        entry_modules = combined.drop(cols, axis=1).dropna(how='all').fillna('')

        return entry_modules

    def _ngrams_offsets_helper(col, _n, offsets):
        """
        Generate a list of series that align the notes from one ngrams according
        to the first or the last note's offset.
            :param pandas.Series col: A column that originally contains
                notes and rests.
            :param int n: The size of the ngram.
            :param str offsets: We could input 'first' if we want to group
                the ngrams by their first note's offset, 'last' if we
                want to group the ngram by the last note's offset, or 'both' if we
                want to multi-index on both of these simultaneously.
            :return pandas.DataFrame: a DataFrame of ngrams sorted by the
                first or last note's offset, or by both with a multi-index.
        """
        if offsets == 'both':
            first = pd.concat([col.shift(-i) for i in range(_n)], axis=1, sort=True)
            last = pd.concat([col.shift(i) for i in range(_n - 1, -1, -1)], axis=1, sort=True)
            mi = pd.MultiIndex.from_arrays([first.index[:-_n + 1], last.index[_n - 1:]], names=['First', 'Last'])
            chunks = first.iloc[:-_n + 1].copy()
            chunks.index = mi
        elif offsets == 'last':
            chunks = pd.concat([col.shift(i) for i in range(_n - 1, -1, -1)], axis=1, sort=True)
        else: # offsets == 'first'
            chunks = pd.concat([col.shift(-i) for i in range(_n)], axis=1, sort=True)
        return chunks

    def _ngramHelper(col, n, exclude, offsets):
        col.dropna(inplace=True)
        if n == -1:
            # get the starting and ending elements of ngrams
            starts = col[(col != 'Rest') & (col.shift(1).isin(('Rest', np.nan)))]
            ends = col[(col != 'Rest') & (col.shift(-1).isin(('Rest', np.nan)))]
            si = tuple(col.index.get_loc(i) for i in starts.index)
            ei = tuple(col.index.get_loc(i) + 1 for i in ends.index)
            if offsets == 'last':
                ind = ends.index
            elif offsets == 'both':
                ind = pd.MultiIndex.from_arrays([starts.index, ends.index], names=['First', 'Last'])
            else: # offsets == 'first'
                ind = starts.index
            vals = [', '.join(col.iloc[si[i]: ei[i]]) for i in range(len(si))]
            ser = pd.Series(vals, name=col.name, index=ind)
            return ser

        chains = ImportedPiece._ngrams_offsets_helper(col, n, offsets)
        if len(exclude):
            chains = chains[chains.apply(lambda row: row.str.contains('|'.join(exclude), regex=True)) == False]
        chains.dropna(inplace=True)
        if col.dtype.name == 'str':
            chains = chains.apply(lambda row: ', '.join(row), axis=1)
        else:
            chains = chains.apply(tuple, axis=1)
        return chains

    def ngrams(self, df=None, n=3, how='columnwise', other=None, held='Held',
                  exclude=['Rest'], interval_settings=('d', True, True), unit=0,
                  offsets='first', show_both=False):
        '''
        Generate n-grams from the given dataframe (df) or from the harmonic and
        melodic intervals of the piece.

        Group sequences of observations in a sliding window "n" events long
        (default n=3). Whether `df` and/or `other` parameters are passed determines
        how the ngrams are assembled. When a `df` is passed but no `other` is passed,
        the columns of the `df` are the data source. When both `df` and `other`
        parameters are passed, contrapuntal-module ngrams are generated. Similarly,
        if neither `df` nor `other` dataframes are provided, they will be supplied
        according to the interval_settings parameter. These contrapuntal-module
        ngrams are useful to assign specific labels to all 2-voice combinations `n`
        events long. For our ngrams, an "event" is a note or rest in either voice. This
        method accepts the following parameters.

        Parameters:
        df : pandas.DataFrame
            A DataFrame of note and rest strings. If `df` is None, harmonic intervals
            will be supplied by the .harmonic method according to the `interval_settings`
            parameter.
        n : int
            The size of the ngrams. If `n` is set to -1, the longest ngrams at
            all time points excluding subset ngrams will be returned.
        how : str
            This parameter is deprecated. The mode is now determined by what is
            or is not passed as the `df` and `other` parameters.
        other : pandas.DataFrame
            A DataFrame of melodic motions. If provided, the method will return
            contrapuntal-module ngrams. This will also happen if neither `df` nor
            `other` are provided.
        held : str
            The label for when one voice sustains a note while the other voice moves.
            This defaults to "Held" to distinguish between held notes and reiterated ones
            but you may want to pass the way a unison gets labeled in your `other`
            DataFrame (e.g. "P1" or "1").
        exclude : list
            A list of strings that will be used to filter out ngrams that contain any
            of the strings in the list. The default is to exclude rests and most likely
            you will want to leave this setting as is.
        interval_settings : tuple
            A tuple of settings that will be passed to the .harmonic and .melodic
            methods if `df` and `other` are not provided. The first item in the tuple
            is the kind of interval to use. The second item is whether to use directed
            intervals. The third item is whether to use compound intervals.
        unit : int or float
            If you want to measure the intervals at a regular durational interval,
            pass the desired regular durational interval as an integer or float.
        offsets : str
            If "first" is selected (default option), the returned ngrams will be
            grouped according to their first notes' offsets, while if "last" is
            selected, the returned ngrams will be grouped according to the last
            notes' offsets. You can also set offsets to "both" in which case a
            dataframe with a multi-index of both the starting and ending offsets
            will be returned.
        show_both : bool
            If True, the melodic motion of both voices in contrapuntal modules are
            shown. If False, only the melodic motion of the lower voice is shown.
            This added information is needed to disambiguate some complex contrapuntal
            modules.

        When a dataframe is passed as `df` and nothing is given for `other`, this
        is the simple case where the events in each column of the `df` DataFrame
        are grouped at the offset of the first event in the window. For example,
        to get 4-grams of melodic intervals:

        ip = ImportedPiece('path_to_piece')
        ngrams = ip.ngrams(df=ip.melodic(), n=4)

        For the "module" mode (interval successions) you must either pass dataframes
        to both `df` and `other`, or leave both as None (default). In
        this case, if the `df` or `other` parameters are left as None, they will
        be replaced with the current piece's harmonic and melodic intervals
        respectively. These intervals will be formed according to the
        interval_settings argument, which gets passed to the melodic and
        harmonic methods (see those methods for an explanation of those
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

        The `show_both` parameter controls whether the melodic motion of both
        voices in contrapuntal modules are shown. If True, the melodic motions of
        the two voices appear with a colon between them in the format lower:upper
        e.g. "3_-2:1, 4_1:-2, 3_-5:2, 8". This is needed for the detection of
        cadential voice function evasion by dropout and also to be able to detect
        which voice attacks at a dissonance.
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
        if '_' not in df.columns[0] and 'Sonority' != df.columns[0]:  # df is not a pair of voices, but rather info about 1 voice at a time
            _df = df.map(str, na_action='ignore')
            _other = other.map(str, na_action='ignore')
            ret = _df + '_' + _other
            return self.ngrams(df=ret, n=n, exclude=exclude, offsets=offsets)
        for pair in df.columns:
            if pair == 'Sonority':
                lowerVoice = other.columns[0]
                lowerMel = other.iloc[:, 0].copy()
            else:
                lowerVoice, upperVoice = pair.split('_')
                lowerMel = other[lowerVoice].copy()
            if show_both and 'Rest' not in exclude:
                lowerMel += ':' + other[upperVoice]
            # can't use pd.concat here because of an issue with pandas, maybe a bug
            combo = pd.DataFrame(lowerMel).join(df[pair], how='outer')
            combo.dropna(subset=(pair,), inplace=True)
            filler = held + ':' + held if show_both else held
            combo[lowerVoice] = combo[lowerVoice].fillna(filler)
            combo.insert(loc=1, column='Joiner', value=', ')
            combo['_'] = '_'
            if n == -1:
                har = df[pair].dropna()
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
                if offsets == 'last':
                    col.index = ends.index
                elif offsets == 'both':
                    col.index = pd.MultiIndex.from_arrays([starts.index, ends.index], names=['First', 'Last'])
                else: # offsets == 'first'
                    col.index = starts.index
            else:  # n >= 1
                lastIndex = -1
                if n == 1:
                    lastIndex = -3
                    n = 2
                combo = ImportedPiece._ngrams_offsets_helper(combo, n, offsets)
                col = combo.iloc[:, 2:lastIndex].dropna().apply(lambda row: ''.join(row), axis=1)
                if exclude:
                    mask = col.apply(lambda cell: all([excl not in cell for excl in exclude]))
                    col = col[mask]
            col.name = pair
            cols.append(col)
        # in case piece has no harmony and cols stays empty
        if cols:
            return pd.concat(cols, axis=1, sort=True)
        else:
            return pd.DataFrame()

    def ic(self, module, generic=False, df=None):
        '''
        *** Invertible Counterpoint and Double Counterpoint Finder ***
        This method takes a string of a module and finds all the instances of
        that module at any level of inversion. The module is an interval
        succession in the format of what you get from the .ngrams() method.
        Specifically, you would need to show melodic motion of both voices,
        which you can do by running the .ngrams() method with these
        parameters: exclude=[], show_both=True, held=1, interval_settings('d', True, True)

        In this method, Invertible Counterpoint is where we have a repetition of
        the given module but where the upper and lower melodies have been exchanged.
        Double Counterpoint is when the module repeats and the melody of each
        part is the same as before, but the harmonic intervals are all off by a
        given amount. This is like Invertible Counterpoint, but the parts have
        not actually crossed.

        Usage:
        piece.ic('7_1:-2, 6_-2:2, 8')

        Notice that the intervals used must be diatonic and without quality.

        The `generic` setting changes the output from the different interval
        successions observed that are at some level of invertible counterpoint
        from the passed module, to a generic form where the level of invertible
        counterpoint is given. This is particularly useful if you want to
        compare how invertible counterpoint is used as a technique among
        different pieces.
        '''
        har_regex = '[^_]*'
        target1, target2 = [], []
        chunks = module.split(', ')
        for chunk in chunks:
            if '_' not in chunk:
                target1.append(har_regex)
                target2.append(har_regex)
                break
            temp = re.split('_|:', chunk)
            mel1 = temp[1]
            mel2 = temp[2]
            target1.append('{}_{}:{}'.format(har_regex, mel1, mel2))
            target2.append('{}_{}:{}'.format(har_regex, mel2, mel1))
        target1 = ', '.join(target1)
        target2 = ', '.join(target2)
        _n = 1 + module.count(',')
        if df is None:
            ngrams = self.ngrams(n=_n, held='1', exclude=[], show_both=True)
        else:
            ngrams = df.copy()
        mask1 = ngrams.apply(lambda row: row.str.contains(target1, regex=True))
        mask2 = ngrams.apply(lambda row: row.str.contains(target2, regex=True))
        if not generic:
            return ngrams[(mask1 | mask2)].dropna(how='all')
        else:
            reference_int = int(module.rsplit(' ', 1)[-1])
            prefix = 'DBL'
            def _icHelper(repetition):
                '''
                Helper function to calculate the level of invertible counterpoint at which
                a repetition is found. This only gets used when the `generic` setting of
                .ic() is set to True.
                '''
                last_har_int = int(repetition.rsplit(' ', 1)[-1])
                if (module == repetition) or (reference_int % 7 == last_har_int % 7 and reference_int > 0 and last_har_int > 0):
                    return 'Repeat'
                if prefix == 'DBL':
                    val = last_har_int - reference_int
                    if val > 0:
                        val += 1
                    else:
                        val -= 1
                elif ((last_har_int > 0 and reference_int > 0) or (last_har_int + reference_int < 0)):
                    val = last_har_int + reference_int - 1
                else:
                    val = last_har_int + reference_int + 1
                return '{}@{}'.format(prefix, val)
            res1 = ngrams[mask1].dropna(how='all').map(_icHelper, na_action='ignore')
            prefix = 'IC'
            res2 = ngrams[mask2].dropna(how='all').map(_icHelper, na_action='ignore')
            res1.update(res2)
            return res1

    def _cvf_helper(self, row, df):
        '''
        Assign the cadential voice function of the lower and upper voices in
        each pair to their respective part name columns. This allows any label from
        any pair to overwrite the label from a previous pair. The one exception is
        that a Cantizans can't overwrite an Altizans, and if it tries to, the
        accompanying Bassizans gets rewritten to be a Qunitizans.'''
        if (row.name in df.index and 'A' in df.loc[(slice(None), row.name[1]), row.UpperVoice].values
            and row.LowerCVF == 'B' and row.UpperCVF == 'C'):
            df.loc[row.name, [row.LowerVoice, row.UpperVoice]] = ('Q', 'A')
        elif (row.name in df.index and 'A' in df.loc[(slice(None), row.name[1]), row.LowerVoice].values
            and row.LowerCVF == 'C' and row.UpperCVF == 'B'):
            df.loc[row.name, [row.LowerVoice, row.UpperVoice]] = ('A', 'Q')
        elif (row.name in df.index and 'A' in df.loc[(slice(None), row.name[1]), row.UpperVoice].values
            and row.UpperCVF == 'C'):
            df.loc[row.name, [row.LowerVoice, row.UpperVoice]] = (row.LowerCVF, 'A')
        else:
            df.loc[row.name, [row.LowerVoice, row.UpperVoice]] = (row.LowerCVF, row.UpperCVF)

    def _cvf_disambiguate_h(self, row):
        '''
        The 'h' label is used internally to help reduce the amount of false
        positives we get with unprepared 4ths. They are either removed or
        replaced with 'b' labels if they seem to be evaded bassizans cvfs.'''
        if not row.empty and 'h' in row.values:  # h is for potential evaded bassizans that gets confused with a chanson idiom
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
            row = row.replace(('t', 'T', 'u', 'x', 'z'), np.nan)
        return row

    def _cadential_pitch(self, row, nr):
        '''
        Return a column of the pitch cadenced to. This is considered to be the
        note the Cantizans cadences to, or if there is no Cantizans, the note
        the Altizans cadences to.'''
        if 'C' in row.values:
            return nr.at[row.name, row.index[np.where(row == 'C')[0][0]]][:-1]
        elif 'A' in row.values:
            return nr.at[row.name, row.index[np.where(row == 'A')[0][0]]][:-1]

    def cvfs(self, keep_keys=False, offsets='last'):
        '''
        Return a dataframe of cadential voice functions in the piece. If
        `keep_keys` is set to True, the ngrams that triggered each CVF pair
        will be shown in additional columns in the table. If offsets='last'
        (default) the last offset of the cvfs will be shown. If offsets is
        set to anything else the table will be returned with a multi-index
        for First and Last offsets for the module patterns.

        Each CVF is represented with a single-character label as follows:

        Realized Cadential Voice Functions:
        "C": cantizans motion up a step (can also be ornamented e.g. Landini)
        "T": tenorizans motion down a step (can be ornamented with anticipations)
        "B": bassizans motion up a fourth or down a fifth
        "A": altizans motion, similar to cantizans, but cadences to a fifth
            above a tenorizans instead of an octave
        "L": leaping contratenor motion up an octave at the perfection
        "P": plagal bassizans motion up a fifth or down a fourth
        "Q": quintizans, like a tenorizans, but resolves down by fifth or up by
            fourth to a fourth below the goal tone of a cantizans or an octave
            below the goal tone of an altizans
        "S": sestizans, occurring in some thicker 16th century textures, this is
            where the agent against the cantizans is already the cantizans' note
            of resolution (often results in a simultaneous false relation); the
            melodic motion is down by third at the moment of perfection

        Evaded Cadential Voice Functions:
        "c": evaded cantizans when it moves to an unexpected note at the perfection
        "t": evaded tenorizans when it goes up by step at the perfection
        "b": evaded bassizans when it goes up by step at the perfection
        "u": evaded bassizans when it goes down by third at the perfection
        (there are no evaded labels for the altizans, plagal bassizans leaping
        contratenor CVFs)
        "s": evaded sestizans when it resolves down by second

        Abandoned Cadential Voice Functions:
        "x": evaded bassizans motion where the voice drops out at the perfection
        "y": evaded cantizans motion where the voice drops out at the perfection
        "z": evaded tenorizans motion where the voice drops out at the perfection

        The way these CVFs combine determines which cadence labels are assigned
        in the .cadences() method.
        '''
        if len(self._getPartNames()) < 2:
            return pd.DataFrame()
        key = ('CVF', keep_keys, offsets)
        if key in self.analyses:
            return self.analyses[key].copy()
        cadences = _getCVFTable()
        cadences['N'] = cadences.index.map(lambda i: i.count(', ') + 1)
        harmonic = self.markFourths()
        melodic = self.melodic('d', True, False)
        ngrams = {n: self.ngrams(how='modules', df=harmonic, other=melodic, n=n, offsets='both',
                  held='1', exclude=[], show_both=True).stack() for n in cadences.N.unique()}
        hits = [ser[ser.str.contains('|'.join(cadences[cadences.N == n].index), regex=True)]
                for n, ser in ngrams.items() if not ser.empty]
        hits = pd.concat(hits)
        hits.sort_index(level=1, inplace=True)
        hits = hits[~hits.index.duplicated('last')]
        if keep_keys:
            ngramKeys = hits.unstack(level=-1)
        hits.name = 'Ngram'
        df = pd.DataFrame(hits)
        df['Pattern'] = df.Ngram.replace(cadences.index, cadences.index, regex=True)
        df = df.join(cadences, on='Pattern')
        voices = [pair.split('_') for pair in df.index.get_level_values(2)]
        df[['LowerVoice', 'UpperVoice']] = voices
        df.index = df.index.droplevel(2)
        cvfs = pd.DataFrame(columns=self._getPartNames(), index=pd.MultiIndex.from_arrays([[], []], names=df.index.names))
        df.apply(func=self._cvf_helper, axis=1, args=(cvfs,))
        cvfs = cvfs.apply(self._cvf_disambiguate_h, axis=1).dropna(how='all')
        cvfs = cvfs.astype('object', copy=False)
        mel = self.melodic('c', True, True)
        for _index in cvfs.index:
            for _voice in cvfs.columns:
                if cvfs.at[_index, _voice] == 'x' and mel.at[_index[1], _voice] in ('5', '-7'):
                    cvfs.at[_index, _voice] = 'B'
                    continue
                if cvfs.at[_index, _voice] == 'y' and mel.at[_index[1], _voice] in ('1', '2'):
                    cvfs.at[_index, _voice] = 'C'
                    continue
                if cvfs.at[_index, _voice] == 'z' and mel.at[_index[1], _voice] in ('-1', '-2'):
                    cvfs.at[_index, _voice] = 'T'
        if keep_keys:
            cvfs = pd.concat([cvfs, ngramKeys], axis=1, sort=True)
        if offsets == 'last' and len(cvfs.index.levels) > 1:
            cvfs = self.condenseMultiIndex(cvfs)
        self.analyses[key] = cvfs
        return cvfs.copy()

    def condenseMultiIndex(self, df, to_drop=0):
        '''
        Take a df with a 'First' and 'Last' multi-index and return a copy condensed such that 
        the `to_drop` index is dropped.
        '''
        if isinstance(df, pd.core.series.Series):
            df = pd.DataFrame(df)
        if df.index.nlevels < 2:
            ret = df.copy()
        else:
            ret = df.droplevel(to_drop)
        dup_mask = ret.index.duplicated()
        dups = ret.index[dup_mask]
        ret = ret[~dup_mask]
        for dup in dups:
            filled = df.loc[(slice(None), dup), :].infer_objects(copy=False).ffill()
            ret.loc[dup, :] = filled.iloc[-1, :].values
        return ret

    def morleyCadences(self):
        '''
        Return a dataframe of the places where there appear to be patient-type melodies. These
        moments are labeled with "Morley Cadence" as they match Morley's definition of a cadence
        which is a one-voice melodic pattern.
        '''
        nr = self.notes(combineUnisons=True)
        mel = self.melodic(kind='d', end=True, df=nr)
        mel_ng = self.ngrams(n=2, df=mel, offsets='last')
        mel2_matches = mel_ng.map(lambda cell: cell == ('-2', '2'), na_action='ignore').replace(False, np.nan).dropna(how='all')
        bs = self.beatStrengths().reindex_like(nr)
        bs_ng = self.ngrams(n=3, df=bs, exclude=[], offsets='last')
        bs_ng = bs_ng.reindex_like(mel_ng)
        bs2_matches = bs_ng.map(lambda cell: cell[0] < cell[2] > cell[1], na_action='ignore').replace(False, np.nan).dropna(how='all')
        # C-B-A-B-C
        mel4_ng = self.ngrams(n=4, df=mel, offsets='last')
        mel4_matches = mel4_ng.map(lambda cell: cell == ('-2', '-2', '2', '2'), na_action='ignore').replace(False, np.nan).dropna(how='all')
        bs4_ng = self.ngrams(n=5, df=bs, exclude=[], offsets='last')
        bs4_ng = bs4_ng.reindex_like(mel4_ng)
        bs4_matches = bs_ng.map(lambda cell: all([cell[-1] > val for val in cell[:-1]]), na_action='ignore').replace(False, np.nan).dropna(how='all')
        
        res = pd.DataFrame().reindex_like(bs_ng).astype(object)
        res[bs2_matches & mel2_matches] = 'Morley Cadence'
        res4 = pd.DataFrame().reindex_like(bs4_ng).astype(object)
        res4[bs4_matches & mel4_matches] = 'Morley Cadence'
        res.update(res4)        
        return res.dropna(how='all')

    def morleyCloses(self):
        """
        Return "closes" according to Morley, which are normally called cadences. This
        method uses a harmonically based definition of a cadence. A close is observed
        if the harmony goes from a root position triad to another root position triad
        a fifth lower at the same time as a morelyCadence event is observed."""
        mcads = self.morleyCadences()
        mcad = pd.Series(True, index=mcads.index, name='MCad')
        sons = self.sonorities()
        low = pd.DataFrame(self.lowLine())
        lowMel = self.melodic(end=True, kind='d', df=low)
        progressions = self.ngrams(df=sons, other=lowMel, n=2, offsets='last', held='1')
        data = pd.concat([progressions, mcad], axis=1, sort=True).dropna(subset=('MCad',))
        res = data.Sonority.str.match('(7/5/3|7/3|5/3|3)_(-5|4), (3|)')
        res = res[res].astype(object)
        res.name = 'Close'
        res.iloc[:] = 'Close'
        return pd.DataFrame(res)

    def cadences(self, keep_keys=False):
        """
        Analyzes the realized, evaded, and abandoned cadences in the score and returns
        a DataFrame with the results.

        This method identifies the cadences in the score based on the contrapuntal voice
        functions (CVFs) and melodic intervals. It also includes additional contextual
        information about the cadences to facilitate filtering and further analysis.
        The information in each column is as follows (in order of their appearance):

        * Pattern: Only visible if `keep_keys` is set to True. This column shows the
        combination of cadential voice functions and chromatic intervals (of the
        Cantizans, Tenorizans, and Altizans cvfs) that triggered this cadence
        observation.

        * Key: Only visible if `keep_keys` is set to True. This column shows the
        regex string used to match the Patterns found with those in the cadenceLabels.csv
        file.

        * CadType: This column shows the type of cadence that was observed. These can
        be these can be realized, evaded, or abandoned. If fully realized, the cadence
        will have no additional descriptor, but "Evaded" and "Abandoned" are labelled
        as such. The cadence types recognized are "Authentic", "Phrygian", "Leaping
        Contratenor", "Clausula Vera", "Phrygian Clausula Vera", "Altizans Only",
        "Phrygian Altizans", "Double Leading Tone", "Quince", and "Reinterpreted".
        The "Quince" cadence is rare and typically only happens in thicker textures
        with a "Quinta pars". It is like a Clausula Vera with the Tenorizans voice
        typically above the Cantizans voice, but the Tenorizans moves up by a fourth
        or down by a fifth at the perfection such that the Cantizans and Tenorizans
        arrive a perfect fifth. The very rare "Reinterpreted" cadence initially sounds
        like it will be an authentic type because one pair of voices can be understood
        as a Cantizans-Bassizans pair. But then Tenorizans below what sounded like a
        Bassizans causes the Cantizans to be reinterpreted as an Altizans, and the
        Bassizans to be reinterpreted as a Quintizans CVF, hence the name "Reinterpreted".

        * LeadingTones: The number of leading tones (i.e. semitones) as notated in the
        score. These can be from the Cantizans, Tenorizans, or Altizans. If the CVF
        that would normally have the leading tone (usually the Cantizans) is evaded or
        abandoned, the basic melodic movement is no longer fulfilled so this measurement
        doesn't apply and a -1 is given. 0 shows that no leading tone is notated in the
        score, so these places are likely candidates for adding editorial ficta.

        * CVFs: The cadential voice functions condensed into one string, following the
        order in which they appear in the voice parts, starting with the uppermost voice.
        Thus CB means the cantizans is above the bassizans, and TC means the tenorizans
        is above the cantizans (in terms of staff positions). For an explanation of the
        symbols see cvfs documentation. Uppercase CVFs are realized, lowercase are evaded
        or abandoned. However, the presence of evaded or abandoned CVFs does not
        necessarily mean the cadence is evaded or abandoned.

        * Low: The pitch of the lowest sounding note at the perfection.

        * RelLow: The lowest pitch of each cadence shown as an interval measured against
        the final. Speaking of which, you can get the final of a piece with the .final()
        method. Looking at lowest sounding pitch of cadences relative to the final
        makes it easier to compare the modal procedure of pieces that are in different
        modes and/or transposed.

        * Tone: Similar to the "Low" column, the "Tone" is the goal tone of the cantizans
        (or altizans if there is no cantizans) respectively. This is usually the same
        pitch class as the "Low" column, but not always. This is NaN if the cadence has
        an evaded or abandoned Cantizans CVF.

        * RelTone: The cadential tone from the "Tone" column shown as an interval
        measured against the final. This is similar to the "RelLow" column, but for the
        cadential tone instead of the lowest sounding pitch. Looking at cadential tones
        relative to the final makes it easier to compare the modal procedure of pieces
        that are in different modes and/or transposed.

        * TSig: The prevailing time signature (as encoded in the score) at the
        perfection. This can be useful to look at cadences in different
        mensurations/meters, particularly comparing binary vs. ternary situations.

        * Measure: The measure number at the perfection.

        * Beat: The beat number at the perfection.

        * Sounding: How many voices are sounding at the perfection. Note that this
        count includes voices that did not have a CVF role in the cadence, and ones
        that only started or entered at the perfection.

        * Progress: The progress toward the end of the piece measured 0-1 where 0 is
        the very beginning of the piece and 1 is the time point of the last attack in
        the piece. This is particularly useful if you want to compare cadences in
        different pieces, especially if they are of different lengths. For example,
        a "Progress" value of 0.5 will always be at the halfway point of a piece, no
        matter how long or short the piece is.

        * SinceLast: The time in quarter notes since the last cadence. The first
        cadence's SinceLast time is the time since the beginning of the piece. An
        unusually high value here could suggest that the prior cadence was particularly
        conclusive, and that a less broken-up stretch of counterpoint follwed it.
        Alternatively a high value could mean that a cadence is being missed within
        the "SinceLast" number of quarter notes just prior to the cadence in question.

        * ToNext: The time in quarter notes to the next cadence. The last cadence's
        ToNext time is the time to the end of the piece. An unusually high value here
        could suggest that this cadence is particularly conclusive, and that a less
        broken-up stretch of counterpoint follows it. Alternatively a high value
        could mean that a cadence is being missed within the "ToNext" number of
        quarter notes just after the cadence in question.

        Parameters
        ----------
        keep_keys : bool, optional
            If True, the returned DataFrame includes the 'Pattern' and 'Key' columns.
            If False (default), these columns are dropped from the DataFrame.

        Returns
        -------
        pandas.DataFrame
            A DataFrame where each row represents a cadence. The columns provide details
            about the cadence, including the CVFs, melodic intervals, measure, beat,
            time signature, sounding pitch, progress, lowest pitch, and relative pitches.

        Notes
        -----
        This method caches the result in the `analyses` attribute of the `Score` object
        to avoid recomputing the cadences if the method is called again with the same parameters.
        """
        if 'Cadences' in self.analyses:
            if keep_keys:
                return self.analyses['Cadences']
            else:
                return self.analyses['Cadences'].drop(['Pattern', 'Key'], axis=1)

        cvfs = self.cvfs(offsets='last')
        mel = self.melodic('c', True, True)
        mel = mel[cvfs.notnull()].dropna(how='all')
        if len(cvfs.index):
            _cvfs = cvfs.apply(self._cvf_simplifier, axis=1)
            _cvfs.replace(['Q', 's', 'S'], np.nan, inplace=True)
        else:
            _cvfs = cvfs.copy()
        mel = mel[_cvfs.isin(list('ACTctu'))].reindex_like(_cvfs).fillna('')
        cadKeys = _cvfs + mel
        keys = cadKeys.apply(lambda row: ''.join(row.dropna().sort_values().unique()), axis=1)
        keys.name = 'Pattern'
        keys = pd.DataFrame(keys)
        cadDict = _getCadenceTable()
        keys['Key'] = keys.Pattern.replace(cadDict.index, cadDict.index, regex=True)
        labels = keys.join(cadDict, on='Key')
        labels['CVFs'] = cvfs.apply(lambda row: ''.join(row.dropna()), axis=1)
        detailed = self.detailIndex(labels, measure=True, beat=True, t_sig=True, sounding=True, progress=True, lowest=True)
        # NEW: check for Rest and remove that row in detailed and labels
        # temp reset of index for value check
        det_reset = detailed.reset_index()
        # index of "Rest" rows
        index_rest = det_reset.loc[det_reset['Lowest'] == 'Rest'].index.tolist()
        # Filter out rows where the fifth level (now a column after reset) contains 'Rest'
        det_filtered = det_reset[~det_reset['Lowest'].str.contains('Rest')]
        # set index back to what it was
        detailed = det_filtered.set_index(detailed.index.names)

        # filter out corresponding row from Labels df
        # temp reset of index
        labels_reset = labels.reset_index()
        # remove corresponding rows that have rests in the detailed DF, based on stored index_rest
        labels_filtered = labels_reset.drop(index_rest, axis=0)
        # put labels back to previous index
        labels = labels_filtered.set_index(labels.index.names)

        labels['Low'] = detailed.index.get_level_values(5).values
        final = note.Note(self.final())
        labels['RelLow'] = labels.Low.apply(lambda x: ImportedPiece._qualityDirectedCompound(interval.Interval(final, note.Note(x))))
        nr = self.notes()
        if len(labels.index):
            labels['Tone'] = cvfs.apply(self._cadential_pitch, args=(nr,), axis=1)
        else:
            labels['Tone'] = []
        labels['RelTone'] = labels.Tone.apply(lambda x: ImportedPiece._qualityDirectedSimple(interval.Interval(final, note.Note(x))))
        labels.RelTone = labels.RelTone[labels.Tone.notnull()]
        labels.Tone = labels.Tone.fillna(np.nan)
        labels['TSig'] = detailed.index.get_level_values(2).values
        labels['Measure'] = detailed.index.get_level_values(0).values
        labels['Beat'] = detailed.index.get_level_values(1).values
        labels['Sounding'] = detailed.index.get_level_values(3).values
        labels['Progress'] = detailed.index.get_level_values(4).values
        ndx = labels.index.to_series()
        labels['SinceLast'] = ndx - ndx.shift(1)
        if len(labels.index):
            labels.iat[0, -1] = labels.index[0]
        labels['ToNext'] = labels['SinceLast'].shift(-1)
        if len(labels.index):
            labels.iat[-1, -1] = self.score.highestTime - labels.index[-1]
        self.analyses['Cadences'] = labels
        if not keep_keys:
            labels = labels.drop(['Pattern', 'Key'], axis=1)
        return labels

    # cadence RADAR plots:

    def cadenceRadarPlot(self, combinedType=False, sounding=None, displayAll=True, customOrder=None, renderer="iframe"):

        '''
        Parameters Overview:

        - combinedType: if set to True, the Cadences would be classified based on both their Type and Tone. If set to False, only Tone will be used. False by default
        - sounding: specify how many voices are sounding (optional). Takes an integer input. Set to None by default
        - displayAll: if set to True, the chart will display all pitches in the Default (Fifth) or Custom order
        - customOrder: the custom order parameter. Takes in a List of Strings
        - renderer: specify what renderer to be used for the plot (options include but are not limited to "svg", "iframe", "png", "notebook" etc

        Typical use:

        cadenceRadarPlot(combinedType=False, displayAll=True, renderer="iframe")

        '''
    # defining the Default display order
        order_array = ["D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F", "C", "G"]

        # accepting a custom order
        if customOrder != None:
            order_array = customOrder

        # getting cadences
        local_cadences = self.cadences()

        # checking if empty
        if len(local_cadences) == 0:
            print("No cadences found in the piece")
            return None

        # filtering for sounding
        if sounding != None:
            local_cadences = local_cadences[local_cadences["Sounding"] == sounding]
            if len(local_cadences) == 0:
                print("No cadences with given number of voices Sounding found in the piece")
                return None

        # generating Combined Type (if combinedType)
        if combinedType:
            local_cadences["Combined_Type"] = local_cadences["Tone"] + "_" + local_cadences["CadType"]
            selected_type = "Combined_Type"
        else:
            selected_type = "Tone"

        # groupby: Selected Type
        grouped_combined = pd.DataFrame(local_cadences.groupby([selected_type]).size().reset_index(name='Count'))

        # displaying all values (if displayAll)
        if displayAll:
            if selected_type == "Tone":
                grouped_combined['Tone'] = pd.Categorical(grouped_combined.Tone, categories=order_array, ordered=True)
                grouped_combined = grouped_combined.sort_values(by='Tone')
            fig = px.line_polar(grouped_combined, r="Count", theta=selected_type, category_orders={"Tone": order_array}, line_close=True)
        else:
            fig = px.line_polar(grouped_combined, r="Count", theta=selected_type, line_close=True)

        # including the Title
        fig.update_layout(title_text=(self.metadata['composer'] + ": " + self.metadata['title']))
        if renderer == 'streamlit':
            return fig
        else:
            fig.show(renderer=renderer)

    # setting up the figure size:
    def _plot_default(self):

        """
        Set sns plot size for cadence progress tool.
        """
        if '_plot_default' not in self.analyses:
            sns.set_theme(rc={'figure.figsize':(15,9)})
            self.analyses['_plot_default'] = True


    def cadenceProgressPlot(self, includeType=False, cadTone=None, cadType=None, customOrder=None, includeLegend=True, renderer=""):

        '''
        Parameters Overview:

        - includeType: if set to True, the Cadence markers would be set based on both their Type. If set to False, a universal (round) marker will be used
        cadTone: specify the Tone of cadences to explore. Takes an String input. Set to None by default
        - cadType: specify the Type of cadences to explore. Takes an String input. Set to None by default
        - customOrder: specify a custom order to be used for the plot (a dictionary: e.g. {"A":0, "B":1 ...}
        - includeLegend: flag to display legend; Default set to True

        Typical use:

        cadenceProgressPlot(includeType=True)

        '''
        # runs sns plot layout
        self._plot_default()

        # defining markers for Cadence Types
        
        cadence_type_dict = {"Clausula Vera": "o", "Abandoned Clausula Vera": "v", "Evaded Clausula Vera": "^",
                     "Authentic" : "<", "Evaded Authentic": ">", "Abandoned Authentic": "8", "Double Leading Tone" : "s",
                     "Evaded Double Leading Tone": "p", "Abandoned Double Leading Tone": "P", "Phrygian Clausula Vera": "d",
                     "Altizans Only": "h", "Evaded Altizans Only": "H", "Leaping Contratenor": "X", "Reinterpreted": "D", 
                     "Phrygian": "d", "None": "*", "Quince": "."}

        # defining the default order list (or accepting the custom one)
        if customOrder == None:
            order_dict = {"Eb":0, "Bb":1, "F":2, "C":3, "G":4, "D":5, "A":6, "E":7, "B":8, "F#":9, "Db":10, "Ab":11}
        else:
            order_dict = customOrder

        # get cadences
        local_cadences = self.cadences()

        # check for a lookup type
        if cadType != None:
            local_cadences = local_cadences[local_cadences["CadType"] == cadType]

        # check for a lookup tone
        if cadTone != None:
            local_cadences = local_cadences[local_cadences["Tone"] == cadTone]

        # check if empty
        if len(local_cadences) < 1:
            print("No cadences found!")
            return None

        # convert Tone to a Numerical
        local_cadences["Numerical"] = local_cadences["Tone"].apply(lambda x: order_dict.get(x))

        # filtering for Types
        if includeType:
            local_cadences["CadType"] = local_cadences["CadType"].fillna("None")
            sns.scatterplot(x=local_cadences['Progress'], y=local_cadences['Numerical'], style=local_cadences["CadType"], markers=cadence_type_dict, s=140)
        else:
            sns.scatterplot(x=local_cadences['Progress'], y=local_cadences['Numerical'], s=140)

        # arranging Ticks and Tick labels
        plt.yticks(ticks=list(order_dict.values()), labels=list(order_dict.keys()))

        # producing the Type legend
        if includeType:
            type_patch_array = []
            for type_item in local_cadences["CadType"].unique().tolist():
                type_patch_array.append(mlines.Line2D([0], [0], marker=cadence_type_dict[type_item], color='black', label=type_item, markerfacecolor='black', markersize=10, linewidth=0))
                plt.legend(handles=type_patch_array)

        # Producing the chart legend
        if includeLegend:
            plt.title("Cadence Progress Graph: " + self.metadata["title"])
        plt.ylabel("Cadence Tone")
        if renderer == "streamlit":
            return plt
        else:
            plt.show()

    def markFourths(self):
        '''
        Distinguish between consonant and dissonant fourths. Returns a df of the diatonic,
        directed, and simple intervals of the piece with a "D" appended to dissonant fourths.
        Consonant fourths and all other intervals remain unchanged. A fourth is considered
        dissonant if it is against the same pitch class as the lowest sounding note.'''
        if 'AnalyzeFourths' in self.analyses:
            return self.analyses['AnalyzeFourths']
        if len(self._getPartNames()) == 1:
            self.analyses['AnalyzeFourths'] = pd.DataFrame()
            return self.analyses['AnalyzeFourths']
        har = self.harmonic('d', True, False).copy()
        nr = self.notes().ffill()
        lowLine = self.lowLine()
        label = 'D'  # the label to use for fourths against the lowest note
        for col in har.columns:
            for i in har.index:
                if har.at[i, col] == '4':
                    lowerVoice = col.split('_')[0]
                    lowerNote = nr.at[i, lowerVoice]
                    lowest = lowLine.asof(i)
                    if lowerNote[0] == lowest[0]:
                        har.at[i, col] += label
                elif har.at[i, col] == '-4':
                    upperVoice = col.split('_')[1]
                    upperNote = nr.at[i, upperVoice]
                    lowest = lowLine.asof(i)
                    if upperNote[0] == lowest[0]:
                        har.at[i, col] += label
        self.analyses['AnalyzeFourths'] = har
        return self.analyses['AnalyzeFourths']


    def supplementum(self):
        '''
        Return the portion of the piece that corresponds to the supplementum. This is defined as
        the part after the last cadence.'''
        if 'Supplementum' not in self.analyses:
            cads = self.cadences()
            if cads['Progress'].iat[-1] == 1:
                supp = None
            else:
                lastCad = cads.index[-1]
                supp = self.notes().loc[lastCad:]
            self.analyses['Supplementum'] = supp
        return self.analyses['Supplementum']

    def _alpha_only(self, value):
        """
        This helper function is used by HR classifier.  It removes non-alphanumberic characters from lyrics
        """
        if isinstance(value, str):
            return re.sub(r'[^a-zA-Z]', '', value)
        else:
            return value

    def homorhythm(self, ngram_length=4, full_hr=True):
        """
        This function predicts homorhythmic passages in a given piece.
        The method follows various stages:

        Gets durational ngrams, and finds passages in which these are the same in two or more voices at a given offsets;
        Gets syllables at every offset, and identifies passages where two or more voices are singing the same lyrics_hr;
        Checks the number of active voices (thus eliminating places where some voices have rests).

        Users can supply either of two arguments:

        'ngram_length' (which is 4 by default, and determines the number of durations and syllables that must be in common among the voices in order to be marked as HR);

        'full_hr' (which is True default).  When full_hr=True the method will find any passage where _all active voices_ share the same durational ngram and syllables; if full_hr=False the method will find any passage where even _two voices_ share the same durational ngram and the same syllables.

        Typical use:

        piece.homorhythm() or piece.homorhythm(ngram_length=4, full_hr=True)

        Also see verovioHomorhythm() for a function that prints results.


        """
        # active version with lyric ngs
        nr = self.notes()
        dur = self.durations(df=nr)

        # add ng = exclude=[] to arguments in ngrams
        # specify ngram length with arguments
        ng = self.ngrams(df=dur, n=ngram_length, exclude=[])
        dur_ngrams = []
        for index, rows in ng.iterrows():
            dur_ngrams_no_nan = [x for x in rows if pd.isnull(x) == False]
            dur_ngrams.append(dur_ngrams_no_nan)
        ng['dur_ngrams'] = dur_ngrams
        ng['active_voices'] = ng['dur_ngrams'].apply(len)
        ng['number_dur_ngrams'] = ng['dur_ngrams'].apply(lambda lyst: len(set(lyst)))

        # from JS to check full_hr or partial
        if full_hr == True:
            ng = ng[(ng['number_dur_ngrams'] < 2) & (ng['active_voices'] > 1)]
        else:
            ng = ng[ng['number_dur_ngrams'] < ng['active_voices']]

        #find involved voices

        hr_voices = []
        for index, rows in ng. iterrows():
            seen = set()
            hr_ngrams = []
            for x in rows['dur_ngrams']:
                if x in seen and not x in hr_ngrams:
                    hr_ngrams.append(x)
                else:
                    seen.add(x)
            hr_v = []
            for index, value in rows.items():
                if value in hr_ngrams:
                    hr_v.append(index)
            hr_voices.append(hr_v)

        ng['hr_voices'] = hr_voices

        # get the lyrics as ngrams to match the durations
        lyrics = self.lyrics()
        lyrics = lyrics.map(self._alpha_only)

        # specify ngram length with arguments
        lyrics_ng = self.ngrams(df=lyrics, n=ngram_length)

        # filter lyric ng's according to what we already know about durations:
        ng_list = ng.index.to_list()
        filtered_lyric_ngs = lyrics_ng.filter(items = ng_list, axis=0)

        # count the lyric_ngrams at each position
        syll_set = []
        for index, rows in filtered_lyric_ngs.iterrows():
            syll_no_nan = [z for z in rows if pd.isnull(z) == False]
            syll_set.append(syll_no_nan)
        filtered_lyric_ngs['syllable_set'] = syll_set
        filtered_lyric_ngs["count_lyr_ngrams"] = filtered_lyric_ngs["syllable_set"].apply(lambda lyst: len(set(lyst)))

        # and the number of active voices
        filtered_lyric_ngs['active_syll_voices'] = filtered_lyric_ngs['syllable_set'].apply(len)
        if full_hr == True:
            hr_sylls_mask = filtered_lyric_ngs[(filtered_lyric_ngs['active_syll_voices'] > 1) & (filtered_lyric_ngs['count_lyr_ngrams'] < 2)]
        else:
            hr_sylls_mask = filtered_lyric_ngs[filtered_lyric_ngs['active_syll_voices'] > filtered_lyric_ngs['count_lyr_ngrams']]

        # combine of both dur_ng and lyric_ng to show passages where more than 2 voices have the same syllables and durations
        ng = ng[['active_voices', 'number_dur_ngrams', 'hr_voices']]
        hr = pd.merge(ng, hr_sylls_mask, left_index=True, right_index=True)
        # the intersection of coordinated durations and coordinate lyrics
        hr['voice_match'] = hr['active_voices'] == hr['active_syll_voices']
        # retain ngram length for use with ema
        hr['ngram_length'] = int(ngram_length)
        result = self.detailIndex(hr, offset=True)
        result["Progress"] = (result.index.get_level_values(2) / self.notes().index[-1])

        if len(result) == 0:
            print ("No HR passages found in " + self.metadata['composer'] + ":" + self.metadata['title'])
        else:

        

            return result

    def _entryHelper(self, col, fermatas=True):
        """
        Return True for cells in column that correspond to notes that either
        begin a piece, or immediately preceded by a rest, double barline, or
        a fermata. For fermatas, this is included by default but can be
        switched off by passing False for the fermatas paramter.
        """
        barlines = self.barlines()[col.name]
        _fermatas = self.fermatas()[col.name].shift()
        _col = col.dropna()
        shifted = _col.shift().fillna('Rest')
        mask = ((_col != 'Rest') & ((shifted == 'Rest') | (barlines == 'double') | (_fermatas)))
        return mask

    def entryMask(self, fermatas=True):
        """
        Return a dataframe of True, False, or NaN values which can be used as
        a mask (filter). When applied to another dataframe, only the True cells
        in the mask will be kept. Usage:

        piece = importScore('path_to_piece')
        mask = piece.entryMask()
        df = piece.notes()
        df[mask].dropna(how='all')

        If fermatas is set to True (default), anything coming immediately after
        a fermata will also be counted as an entry.
        """
        key = ('EntryMask', fermatas)
        if key not in self.analyses:
            nr = self.notes()
            self.analyses[key] = nr.apply(self._entryHelper, args=(fermatas,))
        return self.analyses[key]

    def entries(self, df=None, n=None, thematic=False, anywhere=False, fermatas=True, exclude=[]):
        """
        Return a filtered copy of the passed df that only keeps the events in
        that df if they either start a piece or come after a silence. If the df
        parameter is left as None, it will be replaced with melodic interval results
        calculated after combining unisons and using diatonic intervals without
        interval quality, and with end=False since this is needed specifically
        for this use case.
        When melodic intervals are calculated with end=False the offset of each
        melodic entry is the starting offset of the first note in the melody. If you
        want melodies 4 notes long, for example, note that this would be n=3,
        because four consecutive notes are constitute 3 melodic intervals.
        If the n parameter is not None, then the default melodic interval results
        or passed df argument will be replaced with n-long ngrams of those events.
        Note that this does not currently work for dataframes where the columns
        are combinations of voices, e.g. harmonic intervals.
        If `thematic` is set to True, this method returns all instances of entries
        that happen at least twice anywhere in the piece. This means
        that a melody must happen at least once coming from a rest, and at least
        one more time, though the additional time doesn't have to be after a rest.
        If `anywhere` is set to True, the final results returned include all
        instances of entry melodies, whether they come from rests or not.
        If `fermatas` is set to True (default), any melody starting immediately
        after a fermata will also be counted as an entry.
        """
        if df is None:
            nr = self.notes(combineUnisons=True)
            df = self.melodic(df=nr, kind='d', end=False)
        if n is not None:
            df = self.ngrams(df, n, exclude=exclude)
        mask = self.entryMask(fermatas)
        num_parts = len(mask.columns)
        mask.columns = df.columns[:num_parts]
        entries = df.copy()
        entries.iloc[:, :num_parts] = entries.iloc[:, :num_parts][mask]
        source = entries.copy()
        if anywhere:
            ret = df[df.isin(entries.stack().values)].copy()
        else:
            ret = entries.copy()
        if thematic:
            stack = ret.iloc[:, :num_parts].stack()
            counts = stack.value_counts()
            recurring = counts[counts > 1].index
            # recurring_entries = recurring[recurring.isin(ret.stack())]
            ret = ret[ret.isin(recurring)]
        ret.dropna(how='all', subset=ret.columns[:num_parts], inplace=True)
        return ret

    def _find_entry_int_distance(self, coordinates):
        """
        This helper function is used as part of presentationTypes.

        This function finds the melodic intervals between the first notes of
        successive entries in a given presentation type.

        They are represented as intervals with quality and direction,
        thus P-4, m3, P5, P5, M-9, P-4, P4
        """
        all_tones = self._getM21Objs()
        notes = [all_tones.at[item] for item in coordinates]
        entry_ints = [_directed_name_from_note_strings(notes[i], notes[i + 1]) for i in range(len(notes) - 1)]
        return entry_ints

    def _split_by_threshold(seq, max_diff=70):
        """
        This helper function is used as part of presentationTypes.
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

        yield part

    # July 2022 added to check for overlap
    def _dur_ngram_helper(df, ng_durs):
        """
        This helper is used by the presentation type classifier to check
        total duration of each ngram in a given set of soggetti for a
        presentation type.

        Note that it relies on the ng_dur dataframe that appears in the
        presentation type classifier itself:

        ng_durs = self.durations(df=entries)

        These in turn are saved as a string to check for overlaps among entries.
        """
        dur_list = []
        l = list(zip(df["Offsets"], df["Voices"]))
        for pair in l:
            dur_of_ng = ng_durs.loc[pair[0], pair[1]]
            dur_list.append(dur_of_ng)
        return dur_list

    # July 2022 added to check for overlap
    def _entry_overlap_helper(_dict):
        """
        This private function is used as part of the last stage of the Presentation
        Type classifier.  It reports the overlap (in offsets) between successive entries
        in a given point of imitation.
        """
        return [_dict["Entry_Durs"][i] + _dict["Offsets"][i] - _dict["Offsets"][i+1]
                for i in range(len(_dict["Entry_Durs"]) - 1)]

    # July 2022 added to check for overlap
    def _non_overlap_count(list_overlaps):
        """
        This private function calculates the number of non-overlapping entries
        in a given point of imitation.  It is used by the Presentation Type
        classifier.
        """
        res = sum(i < 1 for i in list_overlaps)
        return res

    def _classify_by_offset(offset_diffs):
        """
        This helper function is used as part of presentationTypes.
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

    # July 2022:  This Replaces the Previous helper
    def _temp_dict_of_details(self, df, det, matches):
        """
        This helper function is used as part of presentationTypes.
        It assembles various features for the presentation types
        into a single temporary dictionary, which in turn is appended to the dataframe of 'points'

        Here we also check for parallel entries in various combinations, then remove
        the parallel entry based on preferred intervals of imitation (normally P1, P4, P5, P8), considered
        in relation to the previous (or following) non-parallel voice.

        The other parallel entry is marked and noted in a separate field.

        """
        # array = df[df.index.get_level_values(0).isin(slist)]
        short_offset_list = df['index'].to_list()
        voice_list = df['voice'].to_list()

        # check length vs set to know whether there are repeating offsets
        if len(short_offset_list) > 2 and len(short_offset_list) > len(set(short_offset_list)):
            # print(short_offset_list)
            parallel_entries = True
            # if yes, then get the offsets that repeat
            repeating_offsets = ([offset for offset, count in collections.Counter(short_offset_list).items() if count > 1])
            # find the index position of each repeating offset
            # then look ahead and back to get the next voice and the 'referring' entry
            # check that the duplicate is not the first entry!
            # if the dups are in the first position, check to make sure they are not the last too!
            # this is the last pair, then we leave, as this is not even a three-voice pattern
            for repeated_offset in repeating_offsets:
                # print(reptead)
                first_dup_index = short_offset_list.index(repeated_offset)
                second_dup_index = first_dup_index + 1

                # assuming more than two voices, then resume testing
                if first_dup_index == 0 and second_dup_index != len(short_offset_list)-1:
                    # next voice details:
                    next_real_entry_index = first_dup_index + 2
                    next_real_entry_offset = short_offset_list[next_real_entry_index]
                    next_real_entry_voice = voice_list[next_real_entry_index]
                    # first voice details
                    first_dup_voice = voice_list[first_dup_index]
                    first_dup_voices_list = [first_dup_voice, next_real_entry_voice]
                    # first pair coordinates
                    first_dup_offset_list = [repeated_offset, next_real_entry_offset]
                    first_dup_tone_coordinates =  list(zip(first_dup_offset_list, first_dup_voices_list))
                    # second voice details and coordinates
                    second_dup_voice = voice_list[second_dup_index]
                    second_dup_voices_list = [second_dup_voice, next_real_entry_voice]
                    second_dup_offset_list = [repeated_offset, next_real_entry_offset]
                    second_dup_tone_coordinates = list(zip(second_dup_offset_list, second_dup_voices_list))
                    # get the intervals
                    first_mel_ints = self._find_entry_int_distance(first_dup_tone_coordinates)
                    second_mel_ints = self._find_entry_int_distance(second_dup_tone_coordinates)
                    #  print("First Pair: ", first_mel_ints, "Second Pair:", second_mel_ints)

                # As long as the dups are not in the first position in the list:
                if first_dup_index != 0:
                    prior_entry_index = first_dup_index - 1
                    # prior voice details
                    prior_voice_offset = short_offset_list[prior_entry_index]
                    prior_entry_voice = voice_list[prior_entry_index]
                    # first voice details
                    first_dup_voice = voice_list[first_dup_index]
                    first_dup_voices_list = [prior_entry_voice, first_dup_voice]
                    # first pair coordinates
                    first_dup_offset_list = [prior_voice_offset, repeated_offset]
                    first_dup_tone_coordinates =  list(zip(first_dup_offset_list, first_dup_voices_list))
                    # second voice details and coordinates
                    second_dup_voice = voice_list[second_dup_index]
                    second_dup_voices_list = [prior_entry_voice, second_dup_voice]
                    second_dup_offset_list = [prior_voice_offset, repeated_offset]
                    second_dup_tone_coordinates = list(zip(second_dup_offset_list, second_dup_voices_list))
                    # get the intervals
                    first_mel_ints = self._find_entry_int_distance(first_dup_tone_coordinates)
                    second_mel_ints = self._find_entry_int_distance(second_dup_tone_coordinates)
                    # print("First Pair: ", first_mel_ints, "Second Pair:", second_mel_ints)

                # list of preferred intervals for selecting entry (the other will become 'parallel')
                preferred_list = ["P1", "P4", "P-4", "P5", "P-5", "P8", "P-8", "P12", "P-12"]
                # if both entries are preferred intervals, take the first (top) one
                if first_mel_ints[0] and second_mel_ints[0] in preferred_list:
                    #  print("First Pair")
                    del short_offset_list[second_dup_index]
                    time_intervals = np.diff(short_offset_list).tolist()
                    parallel_voice = voice_list[second_dup_index]
                    del voice_list[second_dup_index]
                    tone_coordinates = list(zip(short_offset_list, voice_list))
                    melodic_intervals = self._find_entry_int_distance(tone_coordinates)

                # if the first is preferred, take it
                elif first_mel_ints[0] in preferred_list:
                    # print("First Pair")
                    del short_offset_list[second_dup_index]
                    time_intervals = np.diff(short_offset_list).tolist()
                    parallel_voice = voice_list[second_dup_index]
                    del voice_list[second_dup_index]
                    tone_coordinates = list(zip(short_offset_list, voice_list))
                    melodic_intervals = self._find_entry_int_distance(tone_coordinates)

                # if the second is preferred, take it
                elif second_mel_ints[0] in preferred_list:
                    del short_offset_list[first_dup_index]
                    time_intervals = np.diff(short_offset_list).tolist()
                    parallel_voice = voice_list[first_dup_index]
                    del voice_list[first_dup_index]
                    tone_coordinates = list(zip(short_offset_list, voice_list))
                    melodic_intervals = self._find_entry_int_distance(tone_coordinates)
                    #  print("Second Pair")

                # if neither is preferred, take the first
                else:
                    del short_offset_list[second_dup_index]
                    time_intervals = np.diff(short_offset_list).tolist()
                    parallel_voice = voice_list[second_dup_index]
                    del voice_list[second_dup_index]
                    tone_coordinates = list(zip(short_offset_list, voice_list))
                    melodic_intervals = self._find_entry_int_distance(tone_coordinates)
        # if there are no parallel entries, simply find the time intervals and melodic intervals
        # between entries
        else:
            parallel_entries = False
            parallel_voice = None
            # array = df[df.index.get_level_values(0).isin(slist)]
            short_offset_list = df['index'].to_list()
            time_intervals = np.diff(df['index']).tolist()
            voice_list = df['voice'].to_list()
            tone_coordinates =  list(zip(short_offset_list, voice_list))
            melodic_intervals = self._find_entry_int_distance(tone_coordinates)

        meas_beat = det[det.index.get_level_values('Offset').isin(short_offset_list)]
        mb2 = meas_beat.reset_index()
        mb2['mb'] = mb2["Measure"].astype(str) + "/" + mb2["Beat"].astype(str)
        meas_beat_list = mb2['mb'].to_list()

        # temp results for this set
        temp = {"Composer": self.metadata["composer"],
                "Title": self.metadata["title"],
                'First_Offset': short_offset_list[0],
                'Offsets': short_offset_list,
                'Measures_Beats': meas_beat_list,
                "Soggetti": matches,
                'Voices': voice_list,
                'Time_Entry_Intervals': time_intervals,
                'Melodic_Entry_Intervals': melodic_intervals,
                "Parallel_Entries": parallel_entries,
                "Parallel_Voice": parallel_voice}
        return temp
    
    def _offset_joiner(self, a):

        '''
        This private function is used to turn the offset diffs and melodic entry intervals and melodies into strings for the network
        '''
        b = '_'.join(map(str, a))
        return b
    
    def _split_dataframe(self, df, column, threshold):

        '''
        This private helper function is used with the results of p types in ordeer to identify NIMs.
        '''
        # Sort the DataFrame based on the given column
        df = df.reset_index()
        # Calculate the absolute difference between consecutive values in the column
        diff = df[column].diff().abs()
        # Create a boolean mask where the absolute difference exceeds the threshold
        mask = diff > threshold
        # Identify the indices where the mask is True
        split_indices = mask[mask == True].index
        # Split the DataFrame into multiple frames based on the identified indices
        frames = []
        start_idx = 0
        for idx in split_indices:
            frames.append(df[start_idx:idx])
            start_idx = idx 
        # Include the remaining portion of the DataFrame as the final frame
        frames.append(df[start_idx:])
        final_frames = []
        for frame in frames:
            if len(frame) > 1:
                final_frames.append(frame)
        
        return final_frames
    
    def _parallel_voice_check(self, this_row_parallel_voice, next_row_parallel_voice):
        '''
        This private function is used with to help find NIMs as part of the final dictionary of temporary values.
        It checks whether there are "None" values in any of the p type results used to process the fugas.
        '''
        if this_row_parallel_voice is not None and next_row_parallel_voice is not None:
            parallel_voice = this_row_parallel_voice + next_row_parallel_voice
        elif this_row_parallel_voice is not None:
            parallel_voice = this_row_parallel_voice
        elif next_row_parallel_voice is not None:
            parallel_voice = next_row_parallel_voice
        else:
            parallel_voice = None
        return parallel_voice

    def presentationTypes(self, melodic_ngram_length=4, limit_to_entries=True,
                          body_flex=0, head_flex=1, include_hidden_types=False,
                          combine_unisons=False):
        """
        This function uses several other functions to classify the entries in a given piece.
        The output is a list, in order of offset, of each presentation type, including information about
        - measures/beats (of each entry)
        - starting offset (of each entry)
        - soggetti involved (depending on 'flex' settings, there could be more tha one)
        - melodic intervals of entry (the melodic distance between the first tones of successive entries)
        - time intervals of entry (the duration in offets from one entry to the next)
        - presense of flexed entries (either head or body of soggetto, depending on the settings)
        - presense of parallel entries (the parallel entry is reported separately, and is not included in the
        metadata about Time or Melodic intervals of imitation; the preferred intervals are
        ["P1", "P4", "P-4", "P5", "P-5", "P8", "P-8", "P12", "P-12"] and can be adjusted via the code
        for _temp_dict_of_details
        - how many of the entries fail to overlap with another one

        It is also possible to find PEns and IDs that are 'hidden' within
        longer Fugas. Note that this method finds both PEns and IDs that can be
        found among all combinations of voices in a longer fuga (thus between
        entries 1, 2, 4; 2, 4, 5, etc) as well as thosefound between successive entries.

        Arguments include:

        - set ngram length with 'melodic_ngram_length' (=4 by default)
        limit_to_entries (True by default) finds only soggetti that start after a rest or after a section break.
        - setting this to "False" will produce a 'moving window' of all sub-strings (and Presentation Types) created by the
        soggetto, starting on notes 1, 2, 3, 4, etc.
        - set 'combineUnisons' as True or False (False by default)set the length of the soggetti with `melodic_ngram_length`
        - set the maximum difference between the first interval in similar soggetto with 'head_flex' (=1 by default)
        - set the maximum difference between similar soggetti with `body_flex` (=0 by default)
        - for chromatic vs diatonic, compound, and directed data in soggetti, see `interval_settings`
        - to include all the hidden PENs and IDS (those found within longer Fugas),
        use `include_hidden_types == True` (set to False by default)
        - for faster (and simpler) listing of points of imitation without hidden forms, use `include_hidden_types == False` (= default)


        Sample usage:
        piece = importScore('url')
        piece.presentationTypes(head_flex=1)

        Note that the output of this function can be used with verovioPtypes to show
        each cadence in staff notation.
        """
        memo_key = ('PresentationTypes', melodic_ngram_length, limit_to_entries,
            body_flex, head_flex, include_hidden_types, combine_unisons)
        if memo_key in self.analyses:
            return self.analyses[memo_key]
        nr = self.notes(combineUnisons=combine_unisons)
        mel = self.melodic(df=nr, kind='d', end=False)
        mel_ng = self.ngrams(df=mel, exclude=['Rest'], n=melodic_ngram_length)
        if limit_to_entries:
            entries = self.entries(mel_ng)
        else:
            entries = self.ngrams(df=mel, exclude=['Rest'], n=melodic_ngram_length)
        # get ngram durs to use for overlap check as part of _temp files
        ng_durs = self.durations(df=entries)
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
        # defines column order in final df
        # others are at the end for the overlapping entries
        col_order = list(points.columns) + ['Number_Entries',
                                            'Flexed_Entries',
                                            'Parallel_Entries',
                                            'Parallel_Voice',
                                            'Count_Offsets',
                                            'Offsets_Key']

        det = self.detailIndex(nr, offset=True, progress=True)
        # ngrams of melodic entries
        mels_stacked = entries.stack().to_frame()
        mels_stacked.rename(columns =  {0:"pattern"}, inplace = True)
        # edit distance, based on side-by-side comparison of melodic ngrams
        # gets flexed and other similar soggetti
        dist = self.flexed_distance(head_flex, entries)
        dist_stack = dist.stack().to_frame()
        # # filter distances to threshold.  <2 is good
        distance_factor = body_flex + 1
        filtered_dist_stack = dist_stack[dist_stack[0] < distance_factor]
        filtered_dist = filtered_dist_stack.reset_index()
        filtered_dist.rename(columns =  {'level_0':"source", 'level_1':'match'}, inplace = True)
        # # Group the filtered distanced patterns
        full_list_of_matches = filtered_dist.groupby('source')['match'].apply(list).reset_index()

        list_temps = []
        # # classification without hidden types
        if include_hidden_types == False:
            for matches in full_list_of_matches["match"]:
                related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
                entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})
                dfs = self._split_dataframe(entry_array, "index", 70)
                # classification of the full set
                for df in dfs:
                    temp = self._temp_dict_of_details(df, det, matches)
                    # print(temp)
                    if temp in list_temps:
                        pass
                    else:
                        list_temps.append(temp)
            points = pd.DataFrame(list_temps)
            if not points.empty:
                points["Count_Offsets"] = points["Offsets"].apply(lambda lyst: len(set(lyst)))
                points = points[points["Count_Offsets"] > 1]
                points["Count_Voices"] = points["Voices"].apply(lambda lyst: len(set(lyst)))
                points = points[points["Count_Voices"] > 1]
                points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                points["Offsets_Key"] = points["Offsets"].apply(self._offset_joiner)
                points['Flexed_Entries'] = points["Soggetti"].apply(len) > 1
                points["Number_Entries"] = points["Offsets"].apply(len)
                if len(points) == 0:
                    print("No Presentation Types Found in " + self.metadata['composer'] + ":" + self.metadata['title'])
                else:
                    points = points.reindex(columns=col_order).sort_values("First_Offset")
                    # applying various private functions for overlapping entry tests.
                    # note that ng_durs must be passed to the first of these, via args
                    points["Entry_Durs"] = points[["Offsets", "Voices"]].apply(ImportedPiece._dur_ngram_helper, args=(ng_durs,), axis=1)
                    points["Overlaps"] = points[["Entry_Durs", "Offsets"]].apply(ImportedPiece._entry_overlap_helper, axis=1)
                    points["Count_Non_Overlaps"] = points["Overlaps"].apply(ImportedPiece._non_overlap_count)
                    points.drop(['Count_Offsets', 'Offsets_Key', 'Entry_Durs', 'Overlaps'], axis=1, inplace=True)
                    points["Progress"] = (points["First_Offset"] / self.notes().index[-1])        
                    points = points.sort_values("Progress")
                    points = points.reset_index(drop=True)
                    self.analyses[memo_key] = points
                    return points

        # classification with hidden types
        elif include_hidden_types == True:
            # hidden_types_list = ["PEN", "ID"]
            for matches in full_list_of_matches["match"]:
                related_entry_list = mels_stacked[mels_stacked['pattern'].isin(matches)]
                entry_array = related_entry_list.reset_index(level=1).rename(columns = {'level_1': "voice", 0: "pattern"})

                split_list = list(ImportedPiece._split_by_threshold(entry_array.index))
                for item in split_list:
                    # the initial classification of the full set
                    df = entry_array.loc[item].reset_index()
                    if len(df) > 1:
                    # df = df.reset_index()
                        temp = self._temp_dict_of_details(df, det, matches)
                        list_temps.append(temp)

                    if len(item) > 2 :
                        # make range from 2 to allow for fugas needed in NIMs
                        for r in range(3, 6):
                            list_combinations = list(combinations(item, r))
                            for slist in list_combinations:
                                df = entry_array.loc(axis=0)[slist].reset_index()
                                temp = self._temp_dict_of_details(df, det, matches)
                                list_temps.append(temp)
            # 8/24 patch for empty lists
            if len(list_temps) == 0:
                print("No Hidden Types Found in " + self.metadata['composer'] + ":" + self.metadata['title'])
            else:
                points = pd.DataFrame(list_temps)
                if not points.empty:
                    points["Count_Offsets"] = points["Offsets"].apply(lambda lyst: len(set(lyst)))
                    points = points[points["Count_Offsets"] > 1]
                    points = points[points["Voices"].apply(lambda lyst: len(set(lyst))) > 1]
                    points['Presentation_Type'] = points['Time_Entry_Intervals'].apply(ImportedPiece._classify_by_offset)
                    points["Offsets_Key"] = points["Offsets"].apply(self._offset_joiner)
                    points['Flexed_Entries'] = points["Soggetti"].apply(len) > 1
                    points["Number_Entries"] = points["Offsets"].apply(len)
                    # return points
                    if len(points) == 0:
                        print("No Presentation Types Found in " + self.metadata['composer'] + ":" + self.metadata['title'])
                    else:
                        points = points.reindex(columns=col_order).sort_values("First_Offset")
                        points.drop_duplicates(subset=["Offsets_Key"], keep='first', inplace=True)
                        # applying various private functions for overlapping entry tests.
                        # note that ng_durs must be passed to the first of these, via args
                        points["Entry_Durs"] = points[["Offsets", "Voices"]].apply(ImportedPiece._dur_ngram_helper, args=(ng_durs,), axis=1)
                        points["Overlaps"] = points[["Entry_Durs", "Offsets"]].apply(ImportedPiece._entry_overlap_helper, axis=1)
                        # points["Count_Non_Overlaps"] = points["Overlaps"].apply(ImportedPiece._non_overlap_count)
                        points.drop(['Count_Offsets', 'Offsets_Key', 'Entry_Durs', 'Overlaps'], axis=1, inplace=True)
                        points["Progress"] = (points["First_Offset"] / self.notes().index[-1])
                        # return points
                        points = points.sort_values("Progress")
                        points = points.reset_index(drop=True)
                        self.analyses[memo_key] = points
                        return points
            
    # new print methods with verovio
    def verovioCadences(self, df=None):
        """
        This function is used to display the results of the Cadence
        classifier in the Notebook with Verovio.  Each excerpt is
        two measures long:  the measure of the final tone of the cadence
        and the previous measure.

        The function also displays metadata about each excerpt, drawn from the
        cadence results dataframe:  piece ID, composer, title, measures, type of
        cadence, beat of the bar in which the final tone is heard, and evaded
        status.

        Usage:

        You will need to run cadences = piece.cadences() in order to build the
        initial set of results.

        Then pass these results to the Verovio print function:

        verovioCadences(cadences)

        It is also possible to pass a filtered list of cadences to this function 
        by specifying a df into verovioCadences() as shown below:

        cadences = piece.cadences()
        cadences_filtered = cadences[cadences['Tone'] == 'G']
        piece.verovioCadences(cadences_filtered)

        """
        if self.path.startswith('Music_Files/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        elif self.path.startswith('/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        else:
            response = httpx.get(self.path)
            fetched_mei_string = response.text
        tk = verovio.toolkit()
        tk.loadData(fetched_mei_string)
        tk.setScale(30)
        tk.setOptions({"pageHeight":  1500, # Height in pixels
                       "pageWidth":  1500    # Width in pixels
                       })
        # adding option to import filtered df of cadences
        if df is None:
            cadences = self.cadences()
        else:
            cadences = df
        for cad in cadences.index:
            c_meas = cadences.loc[cad]["Measure"]
            c_tone = cadences.loc[cad]["Tone"]
            c_type = cadences.loc[cad]["CadType"]
            c_beat = cadences.loc[cad]["Beat"]
            cvfs = cadences.loc[cad]['CVFs']
            low = int(c_meas-1)
            high = int(c_meas)
            mr = str(low) + "-" + str(high)
            mdict = {'measureRange': mr}

            # select verovio measures and redo layout
            # tk.select(str(mdict))
            tk.select(mdict)
            tk.redoLayout()

            # get the number of pages and display the music
            print("Results:")
            count = tk.getPageCount()
            for c in range(1, count + 1):
                music = tk.renderToSVG(c)
                print("File Name: ", self.file_name)
                print(self.metadata['composer'])
                print(self.metadata['title'])
                print("Cadence End Measure:", c_meas)
                print("Beat: ", c_beat)
                print("Cadence Tone: ", c_tone)
                print("Cadence Type: ", c_type)
                print("Cadential Voice Functions: ", cvfs)
                display(HTML(music))
    # January 2023 addition to print score or excerpt

    def verovioPrintExample(self, start, stop):

        """
        Pass a range of measures (as integers) to print the given range.

        For last measure you can also use '-1', thus for all measures:

        verovioPrintExample(1, -1)

        """
        if self.path.startswith('Music_Files/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        elif self.path.startswith('/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        else:
            response = httpx.get(self.path)
            fetched_mei_string = response.text
        tk = verovio.toolkit()
        tk.loadData(fetched_mei_string)
        tk.setScale(30)
        tk.setOptions({"pageHeight":  1500, # Height in pixels
                       "pageWidth":  3000    # Width in pixels
                       })

        if stop == -1:
            meas = self.measures()
            stop = meas.iloc[-1].tolist()[0]

        mr = str(start) + "-" + str(stop)
        mdict = {'measureRange': mr}

        if stop < start:
            print("Check the measure range, the stop measure must be equal to or greater than the start measure")
        else:# select verovio measures and redo layout
            # tk.select(str(mdict))
            tk.select(mdict)
            tk.redoLayout()

            # get the number of pages and display the music
            print("Score:")
            count = tk.getPageCount()
            for c in range(1, count + 1):
                music = tk.renderToSVG(c)
                print("File Name: ", self.file_name)
                print(self.metadata['composer'])
                print(self.metadata['title'])
                print("Measures: " + str(start) + "-" + str(stop))
                display(HTML(music))

    # July 2022 Addition for printing presentation types with Verovio
    def verovioPtypes(self, p_types=None):
        """
        This function is used to display the results of the presentationTypes function
        in the Notebook with Verovio.  Each excerpt begins with
        the first measure of the given presentation type and continues through four
        measures after the last entry.

        The function also displays metadata about each excerpt, drawn from the
        presentation type dataframe:  piece ID, composer, title, measure range,
        presentation type, voices in order of entry, number of entries, the soggetti
        , melodic entry intervals, time entry intervals.

        Usage:

        You must first run p_types to build the initial list of results and define
        these as a new variable name "p_types":

        p_types = piece.presentationTypes()

        Note that there are many options in the presentationTypes methods to
        determine the length of soggetti, degree of head or body flex, status
        of unisons, whether to use main entries only (or moving window of soggetti)
        and status of hidden entries.)

        After any additional filtering, pass the results of that work to verovioPtypes:

        piece.verovioPtypes(p_types)


        """
        if self.path.startswith('Music_Files/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        elif self.path.startswith('/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        else:
            response = httpx.get(self.path)
            fetched_mei_string = response.text
        tk = verovio.toolkit()
        tk.loadData(fetched_mei_string)
        tk.setScale(30)
        tk.setOptions({"pageHeight":  1500, # Height in pixels
                       "pageWidth":  3000    # Width in pixels
                       })
        print("Results:")
        # collect the metadata
        if p_types is None:
            p_types = self.presentationTypes()
        for p_type in p_types.index:
            this_p_type = p_types.loc[p_type]["Presentation_Type"]
            p_voices = p_types.loc[p_type]["Voices"]
            n_voices = p_types.loc[p_type]["Number_Entries"]
            soggetti = p_types.loc[p_type]["Soggetti"]
            mint = p_types.loc[p_type]["Melodic_Entry_Intervals"]
            tint = p_types.loc[p_type]["Time_Entry_Intervals"]
            flexed = p_types.loc[p_type]["Flexed_Entries"]
            ml = p_types.loc[p_type]["Measures_Beats"]
            parallel = p_types.loc[p_type]["Parallel_Voice"]
            non_overlaps = p_types.loc[p_type]["Count_Non_Overlaps"]

            # build the measure range dictionary
            # Find the first and last items
            first_item = ml[0]
            last_item = ml[-1]

            # Split each item at '/' and take the first part as integer
            first_part_first_item = int(float(first_item.split('/')[0]))
            first_part_last_item = int(float(last_item.split('/')[0]))  
           
            mr = str(first_part_first_item) + "-" + str(first_part_last_item)
            mdict = {'measureRange': mr}

            # select measures in verovio and redo the layout
            tk.select(mdict)
            tk.redoLayout()
            # get the number of pages
            count = tk.getPageCount()

            # print caption
            print("File Name: ", self.file_name)
            print(self.metadata['composer'])
            print(self.metadata['title'])
            print("Measures:", mr)
            print("Presentation Type: ", this_p_type)
            print("Voices: ", p_voices)
            print("Number of Entries: ", n_voices)
            print("Soggetti: ", soggetti)
            print("Melodic Entry Intervals: ", mint)
            print("Time Entry Intervals: ", tint )
            print("Flexed: ", flexed)
            print("Parallel Entries:", parallel)
            print("Number of Non-Overlapping Voices:", non_overlaps)
            # print the music
            for c in range(1, count + 1):
                music = tk.renderToSVG(c)
                # display(SVG(music))
                display(HTML(music))

    # July 2022 Addition for printing hr types with Verovio
    def verovioHomorhythm(self, df=None, ngram_length=4, full_hr=True):
        '''
        Prints HR passages for a given piece with Verovio, based on imported piece and 
        other parameters.

        Users can supply either of two arguments:

        'ngram_length' (which is 4 by default, and determines the number of durations and syllables that must be in common among the voices in order to be marked as HR);

        'full_hr' (which is True default).  When full_hr=True the method will find any passage where _all active voices_ share the same durational ngram and syllables; if full_hr=False the method will find any passage where even _two voices_ share the same durational ngram and the same syllables.

        Typical use:

        piece.verovioHomorhythm()

        OR with custom parameters

        piece.verovioHomorhythm(ngram_length=5, full_hr=False)

        It is also to run piece.homorhythm(), then filter the results in some way and pass those results to the print function:

        #run hr function and convert hr['syllable_set'] to string
        hr = piece.homorhythm(ngram_length=6, full_hr=True).fillna('')
        hr["hr_voices"] = hr["hr_voices"].apply(lambda x: ', '.join(map(str, x))).copy()

        #supply names of voices.  They must match the voice names in `piece.notes.columns()` 
        chosen_voices = ["Tenor", "Bassus"]
        #filter the results for hr passages involving chosen voices:
        hr_with_chosen_voices = hr[hr.apply(lambda x: hr['hr_voices'].str.contains('|'.join(chosen_voices)))].dropna()
        
        #render just the hr_with_chosen_voices using `piece.verovioHomorhythm()`:
        piece.verovioHomorhythm(hr_with_chosen_voices)

        '''
        if self.path.startswith('Music_Files/'):
            text_file = open(self.path, "r")
            fetched_mei_string = text_file.read()
        elif self.path.startswith('/'):
                text_file = open(self.path, "r")
                fetched_mei_string = text_file.read()
        else:
            response = httpx.get(self.path)
            fetched_mei_string = response.text
        tk = verovio.toolkit()
        tk.loadData(fetched_mei_string)
        tk.setScale(30)
        tk.setOptions({"pageHeight":  1500, # Height in pixels
                       "pageWidth":  3000    # Width in pixels
                       })

        # Now get meas ranges and number of active voices
        if df is None:
            homorhythm = self.homorhythm(ngram_length=ngram_length, full_hr=full_hr)
        else:
            homorhythm = df
        hr_list = list(homorhythm.index.get_level_values('Measure').tolist())
        #Get the groupings of consecutive items
        short_list =sorted(list(set(hr_list)))
        li = [list(item) for item in consecutive_groups(short_list)]

        # adjusts number of measures to display based on length of each span
        # of adjacent bars.
        # This matters for long 'n'
        for span in li:
            if ngram_length > 4:
                if len(span) == 1:
                    mr = str(int(span[0])) + "-" + str(int(span[0] + 3))
                else:
                    mr = str(int(span[0])) + "-" + str(int(span[-1] + 1))
            else:
                mr = str(int(span[0])) + "-" + str(int(span[-1] + 1))
            mdict = {'measureRange': mr}
            min_hr_count = 20
            max_hr_count = 0

            # for n in range(span[0], span[-1]+1):
            for n in range(int(span[0]), int(span[-1]) +  1):
                ma = 0
                mi = 20
                for item in homorhythm.loc[n]['hr_voices'].to_list():
                    if len(item) > ma:
                        ma = len(item)
                    if len(item) < mi:
                        mi = len(item)
                    if ma > max_hr_count:
                        max_hr_count = ma
                    if mi < min_hr_count:
                        min_hr_count = mi

            # select verovio measures and redo layout for each passage
            tk.select(mdict)
            tk.redoLayout()
            # get the number of pages and display the music for each passage
            print("Results:")
            count = tk.getPageCount()
            print("File Name: ", self.file_name)
            print(self.metadata['composer'])
            print(self.metadata['title'])
            print("HR Start Measure: ", span[0])
            print("HR Stop Measure: ", span[-1])
            print("Minimum Number of HR Voices: ", min_hr_count)
            print("Maximum Number of HR Voices: ", max_hr_count)

            for c in range(1, count + 1):
                music = tk.renderToSVG(c)
                display(SVG(music))


# The following are NOT part of piece or other classes
# These are used part of visualization routines
# Do not delete!

def joiner(a):
    """This is used for visualization routines."""
    b = '_'.join(map(str, a))
    return b
def clean_melody_new(c):
    """This gets used for visualization routines."""
    first_soggetto = list(c[0])
    soggetto_as_word = joiner(first_soggetto)
    return soggetto_as_word

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
        self.analyses = {'note_list': None}
        for path in paths:
            if type(path) == str:
                _score = importScore(path)
                if _score is not None:
                    self.scores.append(_score)
            else:   # path is already an ImportedPiece
                self.scores.append(path)

        if len(self.scores) == 0:
            print("Empty corpus created. Please import at least one score.")

    def batch(self, func, kwargs={}, metadata=True, number_parts=True, verbose=False):
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

        By default, .batch will replace columns that consist of part names (like .melodic() results)
        or combinations of part names (like .harmonic() results) with numbers starting with "1" for
        the highest part on the staff, "2" for the second highest, etc. This is useful when combining
        results from pieces with parts that have different names. You can override this and keep the
        original part names in the columns by setting the `number_parts` parameter to False.
        For example:

        list_of_dfs_with_numbers_for_part_names = corpus.batch(ImportedPiece.melodic)
        list_of_dfs_with_original_part_names = corpus.batch(ImportedPiece.melodic, number_parts=False)

        You can also set verbose=True if you want to print out the function that you're calling
        and the piece you're analyzing during the analysis. This can be useful to pinpoint a
        piece that is triggering a bug.
        '''
        post = []
        dfs = ('df', 'mask_df', 'other')
        _kwargs = {key: val for key, val in kwargs.items() if key not in dfs}
        list_args = {key: val for key, val in kwargs.items() if key in dfs}
        if verbose:
            print('\nRunning {} analysis on {} pieces:'.format(func.__name__, len(self.scores)))
        if number_parts and func.__name__ in ('cadences', 'presentationTypes', 'lowLine', 'highLine', 'final'):
            number_parts = False
        for i, score in enumerate(self.scores):
            if verbose:
                print('\t{}: {}'.format(i + 1, score.metadata['title']))
            largs = {key: val[i] for key, val in list_args.items()}
            df = func(score, **_kwargs, **largs)
            if number_parts:
                score.numberParts(df)
            if isinstance(df, pd.DataFrame):
                if metadata:
                    df[['Composer', 'Title', 'Date']] = score.metadata['composer'], score.metadata['title'], score.metadata['date']
            post.append(df)
        return post

    def modelFinder(self, models=None, masses=None, n=4, thematic=True, anywhere=True):
        """
        Searches for pieces that may be models of one or more masses. This method returns a
        "driving distance table" showing how likely each model was a source for each mass. This
        is represented by a score 0-1 where 0 means that this relationship was highly unlikely
        and 1 means that the the two are highly likely to be related in this way (or that a
        piece was compared to itself). Specifically, the value is the percentage of the mass's
        thematic (i.e. recurring) melodies can be found as thematic melodies from the model. The
        specific number of times they appear in the model is not considered, provided that it is
        at least two.
        You can optionally pass a CorpusBase object as the `models` and/or `masses` parameters.
        If you do, the CorpusBase object you pass will be used as that group of pieces in the
        analysis. If either or both of these parameters is omitted, the calling CorpusBase
        object's scores will be used. For clarity, the "calling" CorpusBase object is what goes
        to the left of the period in:
        calling_corpus.modelFinder(...
        Since the calling CorpusBase object's scores are used if the `models` and/or `masses`
        parameters are omitted, this means that if you omit both, i.e.

        calling_corpus.modelFinder()

        ... this will compare every score the corpus to every other score in the corpus. You
        should do this if you want to be able to consider every piece a potential model and
        a potential derivative mass.

        Typical Use:

        model_list = ['https://crimproject.org/mei/CRIM_Model_0010.mei',
              'https://crimproject.org/mei/CRIM_Model_0011.mei',
             'https://crimproject.org/mei/CRIM_Model_0014.mei']
        mass_list = ['https://crimproject.org/mei/CRIM_Mass_0008_1.mei',
             'https://crimproject.org/mei/CRIM_Mass_0008_2.mei',
              'https://crimproject.org/mei/CRIM_Mass_0008_3.mei']

        mod_corp = CorpusBase(model_list)
        mass_corp = CorpusBase(mass_list)
        cross_plot = mod_corp.modelFinder(masses=mass_corp, models=mod_corp)
        cross_plot



        """
        if models is None:
            models = self
        if masses is None:
            masses = self

        # get entries from all the models
        notes = models.batch(ImportedPiece.notes, number_parts=False, metadata=False, kwargs={'combineUnisons': True})
        mel = models.batch(ImportedPiece.melodic, number_parts=False, metadata=False, kwargs={'df': notes, 'kind': 'd', 'end': False})
        entries = models.batch(ImportedPiece.entries, number_parts=False, metadata=False,
                               kwargs={'df': mel, 'n': n, 'thematic': thematic, 'anywhere': anywhere})

        # get entries from the masses
        mass_notes = masses.batch(ImportedPiece.notes, number_parts=False, metadata=False, kwargs={'combineUnisons': True})
        mass_mel = masses.batch(ImportedPiece.melodic, number_parts=False, metadata=False, kwargs={'df': mass_notes, 'kind': 'd', 'end': False})
        mass_entries = masses.batch(ImportedPiece.entries, number_parts=False, metadata=False,
                                    kwargs={'df': mass_mel, 'n': n, 'thematic': thematic, 'anywhere': anywhere})
        res = pd.DataFrame(columns=list(model.file_name for model in models.scores), index=list(mass.file_name for mass in masses.scores))
        res.columns.name = 'Model'
        res.index.name = 'Mass'
        for i, model in enumerate(models.scores):
            mod_patterns = entries[i].stack().unique()
            for j, mass in enumerate(masses.scores):
                stack = mass_entries[j].stack()
                hits = stack[stack.isin(mod_patterns)]
                if len(stack.index):
                    percent = len(hits.index) / len(stack.index)
                    res.at[mass.file_name, model.file_name] = percent
        return res

    def derivativeAnalyzer(self, df=None, n=10):
        '''
        Find the top n masses with the highest derivation scores for each model in a table of .modelFinder results.
        The scores from the different movements in each mass are averaged together to get a single score for each
        model-mass pair. The `df` parameter should be the results from the modelFinder method. If it is left as the
        default value of None, it will be replaced with the results of the modelFinder on this corpus with the
        default settings.'''
        if df is None:
            _df = self.modelFinder()
        else:
            _df = df.copy()
        _df.dropna(inplace=True, how='all')
        _df.index = [i.rsplit('_', 1)[0].split('_', 1)[1] if 'Mass' in i else i.split('_', 1)[1] for i in _df.index]
        means = _df.groupby(level=0, sort=False).mean()
        if n > len(means.index):
            print('\nYou used an n of size {} but only passed a corpus with {} masses in it. Returning all results ranked.\n'.format(n, len(means.index)))
            n = len(means.index)
        cols = []
        for col in means.columns:
            topDerivatives = means[col].nlargest(n).round(4)
            cols.append([(i, topDerivatives[i]) for i in topDerivatives.index])
        res = pd.DataFrame(cols, columns=range(1, n+1), index=_df.columns).T
        res.index.set_names('Rank', inplace=True)
        return res

    def moduleFinder(self, models=None, masses=None, n=4, ic=False):
        """
        Like the modelFindfer, this compares a corpus of pieces, returning
        a table of percentages of shared ngrams.

        In this case the ngrams are contrapuntal modules.

        You can optionally pass a CorpusBase object as the `models` and/or `masses` parameters.
        If you do, the CorpusBase object you pass will be used as that group of pieces in the
        analysis. If either or both of these parameters is omitted, the calling CorpusBase
        object's scores will be used. For clarity, the "calling" CorpusBase object is what
        goes to the left of the period in: calling_corpus.modelFinder(...
        Since the calling CorpusBase object's scores are used if the `models` and/or `masses`
        parameters are omitted, this means that if you omit both, i.e.

        calling_corpus.modelFinder()

        ... this will compare every score the corpus to every other score in the corpus. You
        should do this if you want to be able to consider every piece a potential model and a
        potential derivative mass.

        Typical Use:

        model_list = ['https://crimproject.org/mei/CRIM_Model_0010.mei',
              'https://crimproject.org/mei/CRIM_Model_0011.mei',
             'https://crimproject.org/mei/CRIM_Model_0014.mei']
        mass_list = ['https://crimproject.org/mei/CRIM_Mass_0008_1.mei',
             'https://crimproject.org/mei/CRIM_Mass_0008_2.mei',
              'https://crimproject.org/mei/CRIM_Mass_0008_3.mei']

        mod_corp = CorpusBase(model_list)
        mass_corp = CorpusBase(mass_list)
        cross_plot = mod_corp.moduleFinder(masses=mass_corp, models=mod_corp)
        cross_plot
        """
        if models is None:
            models = self
        if masses is None:
            masses = self
        res = pd.DataFrame(columns=list(model.file_name for model in models.scores), index=list(mass.file_name for mass in masses.scores))
        res.columns.name = 'Model'
        res.index.name = 'Mass'

        if not ic:
            # get modules at entries from all the models using helper
            model_modules = models.batch(ImportedPiece._entry_ngram_helper, kwargs={'n': n}, metadata=False)
            # get modules at entries from the masses using helper
            mass_modules = masses.batch(ImportedPiece._entry_ngram_helper, kwargs={'n': n}, metadata=False)
        else:   # ic == True
            model_modules = models.batch(ImportedPiece.ngrams, kwargs={'n': n, 'held': '1', 'exclude': [], 'show_both': True}, metadata=False)
            mass_modules = masses.batch(ImportedPiece.ngrams, kwargs={'n': n, 'held': '1', 'exclude': [], 'show_both': True}, metadata=False)

        for i, model in enumerate(models.scores):
            mod_patterns = model_modules[i].stack()
            mod_patterns = mod_patterns[~mod_patterns.str.contains('Rest')].unique()
            if ic:
                copy = pd.Series(mod_patterns)
                reduced_patterns = []
                while len(copy.index):
                    reduced_patterns.append(copy.iat[0])
                    variants = model.ic(module=copy.iat[0], df=model_modules[i])
                    copy = copy[~copy.isin(variants.stack().unique())]
                mod_patterns = reduced_patterns
            for j, mass in enumerate(masses.scores):
                if ic and mass.file_name == model.file_name:
                    res.at[mass.file_name, model.file_name] = 1
                    continue
                df = mass_modules[j]
                df = df[df.map(lambda cell: 'Rest' not in cell, na_action='ignore')].dropna(how='all')
                stack = df.stack()
                if not ic:
                    hits = stack[stack.isin(mod_patterns)]
                else:   # ic == True
                    ic_targets = []
                    for patt in mod_patterns:
                        temp = mass.ic(module=patt, df=mass_modules[j])
                        ic_targets.append(temp.stack().unique())
                    unique_targets = np.unique(np.concatenate(ic_targets))
                    hits = stack[stack.isin(unique_targets)]
                if len(stack.index):
                    percent = len(hits.index) / len(stack.index)
                    res.at[mass.file_name, model.file_name] = percent

        return res

    def compareCadenceRadarPlots(self, combinedType=False, sounding=None, displayAll=True, customOrder=None, renderer=""):

        '''
        Parameters Overview:

        - combinedType: if set to True, the Cadences would be classified based on both their Type and Tone. If set to False, only Tone will be used. False by default
        - sounding: specify how many voices are sounding (optional). Takes an integer input. Set to None by default
        - displayAll: if set to True, the chart will display all pitches in the Default (Fifth) or Custom order
        - customOrder: the custom order parameter. Takes in a List of Strings
        - renderer: specify what renderer to be used for the plot (options include but are not limited to "svg", "iframe", "png", "notebook" etc

        Typical use:

        compareCadenceRadarPlots(combinedType=False, displayAll=True, renderer="iframe")

        '''

        # specifying the Default order:
        order_array = ["D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F", "C", "G"]

        # accepting a custom order (if customOrder)
        if customOrder != None:
            order_array = customOrder

        # creating an empty DataFrame
        data = pd.DataFrame()

        # iterating
        for piece_item in self.scores:

            # get Piece cadences
            loop_cadences = piece_item.cadences()

            # check if empty
            if len(loop_cadences) == 0:
                print("No cadences found in the piece: " + piece_item.metadata["title"])
                continue

            # filter for sounding (if sounding)
            if sounding != None:
                loop_cadences = loop_cadences[loop_cadences["Sounding"] == sounding]
                if len(loop_cadences) == 0:
                    print("No cadences with given number of voices Sounding found in the piece: " + piece_item.metadata["title"])
                    continue

            # create Combined Type (if combinedType)
            if combinedType:
                loop_cadences["Combined_Type"] = loop_cadences["Tone"] + "_" + loop_cadences["CadType"]
                selected_type = "Combined_Type"
            else:
                selected_type = "Tone"

            # groupby: Selected Type
            loop_group = pd.DataFrame(loop_cadences.groupby([selected_type]).size().reset_index(name='Count'))
            # assign Piece Title
            loop_group["Piece"] = piece_item.metadata["title"]

            # making sure grapher graphs in order (before displaying in order)
            if displayAll and selected_type == "Tone":
                loop_group['Tone'] = pd.Categorical(loop_group.Tone, categories=order_array, ordered=True)
                loop_group = loop_group.sort_values(by='Tone')

            # concat
            data = pd.concat([loop_group, data], ignore_index=True)

        if len(data) == 0:
            print("No cadences found in the corpus")
            return None

        # display all categories (if displayAll)
        if displayAll and selected_type == "Tone":
            fig = px.line_polar(data, r="Count", theta=selected_type, color="Piece", category_orders={"Tone": order_array}, line_close=True)
        else:
            if combinedType:
                sort_order = sorted(data["Combined_Type"].unique())
                fig = px.line_polar(data, r="Count", theta=selected_type, color="Piece", category_orders={"Combined_Type": sort_order}, line_close=True)
            else:
                fig = px.line_polar(data, r="Count", theta=selected_type, color="Piece", line_close=True)
        # chart title
        fig.update_layout(title_text=("Cadence Distribution Comparison"))
        if renderer == "streamlit":
            return fig
        else:
            fig.show()

    # setting up the figure size:
    def _plot_default(self):

        """
        Set sns plot size for cadence progress tool.
        """
        if '_plot_default' not in self.analyses:
            sns.theme(rc={'figure.figsize':(15,9)})
            self.analyses['_plot_default'] = True

    def compareCadenceProgressPlots(self, includeType=False, cadTone=None, cadType=None, includeLegend=True, customOrder=None, renderer=""):

        '''
        Parameters Overview:

        - includeType: if set to True, the Cadence markers would be set based on both their Type. If set to False, a universal (round) marker will be used
        cadTone: specify the Tone of cadences to explore. Takes an String input. Set to None by default
        - cadType: specify the Type of cadences to explore. Takes an String input. Set to None by default
        - customOrder: specify a custom order to be used for the plot (a dictionary: e.g. {"A":0, "B":1 ...}
        - includeLegend: flag to display legend; Default set to True

        Typical use:

        compareCadenceProgressPlots(includeType=True)

        '''

        # runs sns plot layout
        self._plot_default()

        # defining a palette for the pieces
        colors_array = sns.color_palette(n_colors=len(self.scores), as_cmap=True)
        color_pointer = 0
        patch_set = []
        type_patch_array = []

        # creating the piece legend
        for i in range(len(self.scores)):
            patch_set.append(mpatches.Patch(color=colors_array[i], label=self.scores[i].metadata["title"]))
        piece_legend = plt.legend(handles=patch_set, loc='upper left')

        # looking for unique Types
        unique_types_array = []

        # defining markers for Cadence Types
        cadence_type_dict = {"Clausula Vera": "o", "Abandoned Clausula Vera": "v", "Evaded Clausula Vera": "^",
                    "Authentic" : "<", "Evaded Authentic": ">", "Abandoned Authentic": "8", "Double Leading Tone" : "s",
                    "Evaded Double Leading Tone": "p", "Abandoned Double Leading Tone": "P", "Phrygian Clausula Vera": "d",
                    "Altizans Only": "h", "Evaded Altizans Only": "H", "Leaping Contratenor": "X", "Reinterpreted": "D", "Phrygian": "d", "Quince": ".", "None": "*"}

        # defining the default order or accepting the custom order
        if customOrder == None:
            order_dict = {"Eb":0, "Bb":1, "F":2, "C":3, "G":4, "D":5, "A":6, "E":7, "B":8, "F#":9, "C#":10, "Ab":11}
        else:
            order_dict = customOrder

        # piece loop
        for piece_item in self.scores:

            # get cadences
            loop_cadences = piece_item.cadences()

            # pick color
            local_color = colors_array[color_pointer]
            color_pointer += 1

            # check for a lookup type
            if cadType != None:
                loop_cadences = loop_cadences[loop_cadences["CadType"] == cadType]

            # check for a lookup tone
            if cadTone != None:
                loop_cadences = loop_cadences[loop_cadences["Tone"] == cadTone]

            # check if empty
            if len(loop_cadences) < 1:
                print("No cadences found in: " + piece_item.metadata["title"])
                continue

            # convert Tone to a Numerical
            loop_cadences["Numerical"] = loop_cadences["Tone"].apply(lambda x: order_dict.get(x))

            # include Type (if includeType)
            if includeType:
                loop_cadences["CadType"] = loop_cadences["CadType"].fillna("None")
                sns.scatterplot(x=loop_cadences['Progress'], y=loop_cadences['Numerical'], style=loop_cadences["CadType"], markers=cadence_type_dict, s=140, color=local_color)
                unique_types_array.extend(loop_cadences["CadType"].unique().tolist())
            else:
                plt.scatter(x=loop_cadences['Progress'], y=loop_cadences['Numerical'], s=140, color=local_color)

        # produce y Ticks and Labels
        plt.yticks(ticks=list(order_dict.values()), labels=list(order_dict.keys()))

        # producing the Type Legend (if includeType)
        if includeType:
            type_patches = list(set(unique_types_array))
            for type_item in type_patches:
                type_patch_array.append(mlines.Line2D([0], [0], marker=cadence_type_dict[type_item], color='black', label=type_item, markerfacecolor='black', markersize=10, linewidth=0))
                plt.legend(handles=type_patch_array)

        # producing the Legend (if includeLegend)
        if includeLegend:
            plt.title("Cadence Progress Comparison")
            plt.gca().add_artist(piece_legend)
        plt.ylabel("Cadence Tone")
        if renderer == "streamlit":
            return plt
        else:
            plt.show()

    def _patternToSeries(self, pattern):
        output_list = []
        output_list.append(0)
        output_list.append(pattern[0])
        for i in range(1, len(pattern)):
            output_list.append(sum(pattern[0:i]) + pattern[i])
        return output_list

    def _createGraphList(self, pattern_list):
        '''
        helper function for graphing interval families
        '''
        graph_list = []
        for item in pattern_list:
            if isinstance(item, tuple):
                temp_item = list(map(lambda x: int(x), item))
            elif isinstance(item, str):
                temp_item = list(map(lambda x: int(x), item.split(', ')))
            else:
                print("Intervals are not of type: String or Tuple")
                return None
            graph_list.append(self._patternToSeries(temp_item))
        return graph_list

    def compareIntervalFamilies(self, length=4, combineUnisons=True, kind="d", end=False, variableLength=False,
        suggestedPattern=None, useEntries=True, arriveAt=None, includeLegend=True, renderer=""):

        '''
        It is possible to select:

        length=4
        combineUnisons=True
        kind="d"
        end=False
        variableLength=False
        suggestedPattern=None
        useEntries=True

        Comparing the Interval Families with `length=4` and `useEntries=True` by default:

        Typical use:
        compareIntervalFamilies(length=4)

        Another useful option is `variableLength=True`, therefore including **all unique patterns up to the specified length**:

        compareIntervalFamilies(length=4, variableLength=True)

        We can narrow down patterns of interested by specifying `suggestedPattern=Tuple(Str*)`, for example looking for **all patterns that start with `-2, -2`**:

        compareIntervalFamilies(length=4, variableLength=True, suggestedPattern=("4", "2"))

        '''

        # runs sns plot layout
        self._plot_default()

        if length < 1:
            print("Please use length >= 1")
            return None

        if kind not in ["d", "z", "c"]:
            print("\n Warning: you might encounter an error due to using an uncommon interval kind. \n Currently, we have been working with \"z\", \"d\", and \"c\"")

        number_of_patterns = 0
        colors_array = sns.color_palette(n_colors=length, as_cmap=True)
        color_pointer = 0
        patch_array = []
        for piece_item in self.scores:
            local_color = colors_array[color_pointer]
            color_pointer += 1
            patch_array.append(mpatches.Patch(color=local_color, label=piece_item.metadata["title"]))
            local_ngrams = pd.DataFrame(columns=piece_item.notes().columns)

            if variableLength:
                loop_start = 1
            else:
                loop_start = length

            for i in range(loop_start, length + 1):
                loop_notes = piece_item.notes(combineUnisons=combineUnisons)
                loop_melodic = piece_item.melodic(df=loop_notes, kind=kind, end=end)
                if useEntries:
                    loop_ngrams = piece_item.entries(df=loop_melodic, n=int(i), exclude=["Rest"]).fillna('')
                else:
                    loop_ngrams = piece_item.ngrams(df=loop_melodic, n=int(i), exclude=["Rest"]).fillna('')
                # TODO: try to move this out of the loop and just concat once if possible
                local_ngrams = pd.concat([local_ngrams, loop_ngrams])

            total_unique_ngrams_list = list(filter(lambda x: x != "", list(set(local_ngrams.values.flatten().tolist()))))

            if suggestedPattern:
                matching_unique_ngrams_list = list(map(lambda x: x if ",".join(x).startswith(",".join(suggestedPattern)) else "", total_unique_ngrams_list))
                total_unique_ngrams_list = list(filter(lambda x: x != "", matching_unique_ngrams_list))
                if len(total_unique_ngrams_list) < 1:
                    print("No patterns matching the suggestedPattern found in: " + piece_item.metadata["title"])
                    continue

            graph_pattern_list = self._createGraphList(total_unique_ngrams_list)

            if arriveAt != None:
                graph_pattern_list = list(filter(lambda x: x[-1] == arriveAt, graph_pattern_list))
                if len(graph_pattern_list) < 1:
                    print("No patterns arriving at arriveAt found in: " + piece_item.metadata["title"])
                    continue

            number_of_patterns += len(graph_pattern_list)
            for single_pattern in graph_pattern_list:
                plt.plot(single_pattern, alpha=0.35, lw=6, color=local_color)

        plt.yticks(np.arange(-15, 15, 1.0))
        plt.xticks(np.arange(0, length + 1, 1.0))
        if includeLegend:
            plt.title("Total Number of Patterns: " + str(number_of_patterns))
            plt.legend(handles=patch_array)
        if renderer == "streamlit":
            return plt
        else:
            plt.show()
