# All work below thanks to Alex Morgan
from music21 import converter, stream, note, interval
import pandas as pd
from itertools import combinations
import pdb

Interval = interval.Interval
class CorpusBasePd(object):
  def __init__(self):
    self.importedPieces = {}

  def _import_piece(self, pathname: str):
    if pathname not in self.importedPieces: # only import a piece if it hasn't been imported this session
      # piece = converter.Converter()
      # piece.parseFile(pathname, forceSource=True, storePickle=False)
      self.importedPieces[pathname] = ImportedPiece(pathname)
    return self.importedPieces[pathname]

class ImportedPiece():
  def __init__(self, pathname):
    self.pathname = pathname
    piece = converter.Converter()
    piece.parseFile(pathname, forceSource=True, storePickle=False)
    self.piece = piece.stream
    self.analyses = {}

  def getPartSeries(self):
    if 'PartSeries' not in self.analyses:
      parts = self.piece.getElementsByClass(stream.Part)
      part_series = []
      for i, part in enumerate(parts):
        notesAndRests = part.flat.getElementsByClass(['Note', 'Rest'])
        part_name = part.partName or 'Part_' + str(i + 1)
        ser = pd.Series(notesAndRests, name=part_name)
        ser.index = ser.apply(lambda noteOrRest: noteOrRest.offset)
        ser = ser[~ser.index.duplicated()] # remove multiple events at the same offset in a given part
        part_series.append(ser)
      self.analyses['PartSeries'] = part_series
    return self.analyses['PartSeries']

  def getM21Objs(self):
    if 'M21Objs' not in self.analyses:
      self.analyses['M21Objs'] = pd.concat(self.getPartSeries(), axis=1)
    return self.analyses['M21Objs']

  def _remove_tied(self, noteOrRest):
    if hasattr(noteOrRest, 'tie') and noteOrRest.tie is not None and noteOrRest.tie.type != 'start':
      return None
    return noteOrRest

  def getM21ObjsNoTies(self):
    if 'M21ObjsNoTies' not in self.analyses:
      df = self.getM21Objs().applymap(self._remove_tied).dropna(how='all')
      self.analyses['M21ObjsNoTies'] = df
    return self.analyses['M21ObjsNoTies']

  def getDuration(self):
    if 'Duration' not in self.analyses:
      df = self.getM21ObjsNoTies()
      highestTimes = [part.highestTime for part in self.piece.getElementsByClass(stream.Part)]
      newCols = []
      for i, x in enumerate(highestTimes):
        ser = df.iloc[:, i]
        ser.dropna(inplace=True)
        ser.at[x] = 0  # placeholder value
        vals = ser.index[1:] - ser.index[:-1]
        ser.drop(x, inplace=True)
        ser[:] = vals
        newCols.append(ser)
      return pd.concat(newCols, axis=1)

  def _notesAndRestsHelper(self, noteOrRest):
    if not hasattr(noteOrRest, 'isRest'):
      return noteOrRest
    if noteOrRest.isRest:
      return 'Rest'
    return noteOrRest.nameWithOctave

  def getNotesAndRests(self):
    if 'NotesAndRests' not in self.analyses:
      df = self.getM21ObjsNoTies().applymap(self._notesAndRestsHelper)
      self.analyses['NotesAndRests'] = df
    return self.analyses['NotesAndRests']

  def _beatStrengthHelper(self, noteOrRest):
    if hasattr(noteOrRest, 'beatStrength'):
      return noteOrRest.beatStrength
    return noteOrRest

  def getBeatStrength(self):
    if 'BeatStrength' not in self.analyses:
      df = self.getM21ObjsNoTies().applymap(self._beatStrengthHelper)
      self.analyses['BeatStrength'] = df
    return self.anlayses['BeatStrength']

  def _intervalHelper(row):
    if hasattr(row[0], 'isNote') and row[0].isNote and hasattr(row[1], 'isNote') and row[1].isNote:
      return Interval(row[0], row[1])
    return None

  def _melodifyPart(ser):
    ser.dropna(inplace=True)
    shifted = ser.shift(-1)
    partDF = pd.concat([ser, shifted], axis=1)
    #pdb.set_trace()
    res = partDF.apply(ImportedPiece._intervalHelper, axis=1).dropna()
    return res

  def _getM21MelodicIntervals(self):
    if 'M21MelodicIntervals' not in self.analyses:
      m21Objs = self.getM21ObjsNoTies()
      df = m21Objs.apply(ImportedPiece._melodifyPart)
      self.analyses['M21MelodicIntervals'] = df
    return self.analyses['M21MelodicIntervals']

  def _directedDiatonicHelper(cell):
    if hasattr(cell, 'directedName'):
      return cell.directedName
    return cell

  def getDirectedMelodicIntervals(self):
    if 'DirectedMelodicIntervals' not in self.analyses:
      df = self._getM21MelodicIntervals()
      df = df.applymap(ImportedPiece._directedDiatonicHelper)
      self.analyses['DirectedMelodicIntervals'] = df
    return self.analyses['DirectedMelodicIntervals']

  def _semitonalHelper(cell):
    if hasattr(cell, 'semitones'):
      return cell.semitones
    return cell

  def getSemitonalMelodicIntervals(self):
    if 'SemitonalMelodicIntervals' not in self.analyses:
      df = self._getM21MelodicIntervals()
      df = df.applymap(ImportedPiece._semitonalHelper)
      self.analyses['SemitonalMelodicIntervals'] = df
    return self.analyses['SemitonalMelodicIntervals']

  def _getM21HarmonicIntervals(self):
    if 'M21HarmonicIntervals' not in self.analyses:
      m21Objs = self.getM21ObjsNoTies()
      pairs = []
      combos = combinations(range(len(m21Objs.columns) - 1, -1, -1), 2)
      for combo in combos:
        df = m21Objs.iloc[:, list(combo)].ffill()
        mask = df.applymap(lambda cell: (hasattr(cell, 'isNote') and cell.isNote))
        df = df[mask].dropna()
        ser = df.apply(ImportedPiece._intervalHelper, axis=1)
        # name each column according to the voice names that make up the intervals, e.g. 'Bassus_Altus'
        ser.name = '_'.join((m21Objs.columns[combo[0]], m21Objs.columns[combo[1]]))
        pairs.append(ser)
      ret = pd.concat(pairs, axis=1)
      self.analyses['M21HarmonicIntervals'] = ret
    return self.analyses['M21HarmonicIntervals']

  def getDirectedHarmonicIntervals(self):
    if 'DirectedHarmonicIntervals' not in self.analyses:
      df = self._getM21HarmonicIntervals()
      df = df.applymap(ImportedPiece._directedDiatonicHelper)
      self.analyses['DirectedHarmonicIntervals'] = df
    return self.analyses['DirectedHarmonicIntervals']

  def getSemitonalHarmonicIntervals(self):
    if 'SemitonalHarmonicIntervals' not in self.analyses:
      df = self._getM21HarmonicIntervals()
      df = df.applymap(ImportedPiece._semitonalHelper)
      self.analyses['SemitonalHarmonicIntervals'] = df
    return self.analyses['SemitonalHarmonicIntervals']
