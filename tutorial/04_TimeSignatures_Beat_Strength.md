# Time Signatures, Measure Numbers, Barlines and Beat Strengths

Several of these functions called as parameters `detailIndex()`. See more at [09_DetailIndex](09_DetailIndex.md). But they can be useful on their own, too.

## View Time Signatures with `timeSignatures()`

For any piece, it is possible to return a dataframe containing each new time signature and the offset at which it appears:

```python
piece.timeSignatures()
```

There are no parameters to set with this function.  But it can be called as a parameter from `detailIndex`:

```python
nr = piece.notes()
piece.detailIndex(nr, t_sig = True)
```

![Alt text](images/tsig.png)

## View Measure Numbers with `measures()`

This method returns a dataframe with offsets as the index, and the measure number of each event (note, melodic interval, ngram) in the columns. Thus all columns will frequently be identical. 

```python
piece.measures()
```

It is not particularly useful on its own, but it might be helpful for situations in which it is important to return all the offsets that correspond to a given measure number. For example, here is a way to find all of the notes that sound at the start of each measure in a piece:

```python
#df of measures (that is, where each measure starts)
ms = piece.measures()
#index of that df as list
measure_starts = ms.index.to_list()
#df of notes and rests
nr = piece.notes()
#now filter nr to show only those offsets (=index) that are in the list just made
nr2 = nr[nr.index.isin(measure_starts)]
nr2
```

![Alt text](images/measure_starts.png)

Or another way to do this with the `loc` method of Pandas:

```python
#df of measures (that is, where each starts)
ms = piece.measures()
#index of that df as list
measure_starts = ms.index.to_list()
#df of notes and rests
nr = piece.notes()
#filter nr to show only those offsets (=index) that are in the list just made
nr2 = nr.loc[nr.index.isin(measure_starts)]
nr2
```


## View Barlines with `barlines()`

This method returns a data frame showing the offsets at which double or final barlines appear in each voice. It does not report normal (single) barlines.  As such it can be helpful in detecting section breaks in a work. Use it in conjunction with `detailIndex` to report measure numbers, too.

```python
barlines = piece.barlines()
piece.detailIndex(barlines)
```

![Alt text](images/barlines.png)

## View Beat Strengths with `beatStrengths()`

music21 has a built-in method that assigns a relative strength for each beat in a bar, depending on the prevailing time signature. The downbeat is equal to 1.0, and all other metric positions in a measure are given smaller numbers approaching zero as their metric weight decreases. To see the results in the context of measures and beats (in order to make sense of the ratings), pass the results of `beatStrengths()` to `detailIndex()`

```python
bs = piece.beatStrengths()
piece.detailIndex(bs)
```

![Alt text](images/bs.png)

The resulting dataframe could also be used to filter other results, for instance, by finding all offsets (and voices) where a certain `beatStrength` condition is met. For instance, here is a way to filter for 'strong beats', the 'strong notes', the 'strong melodic intervals', and at last the 'ngrams based on strong intervals'.  In brief, **structural tones**:

```python
#get the notes
nr = piece.notes()
#stack the voices on top of each other to make a series
nr_stacked = nr.stack()
#find the beat strengths
bs = piece.beatStrengths()
#stack and filter the beat strengths according to some threshold
strong_beats = bs.stack() > .75
#filter the stacked notes and unstack
strong_notes = nr_stacked[strong_beats].unstack()
#find the melodic intervals among those 'strong' notes
mel_strong = piece.melodic(df = strong_notes, kind = 'd')
#and at last find the ngrams for those strong notes
strong_ngrams = piece.ngrams(df = mel_strong, n = 4, exclude = ['Rest']).fillna('')
strong_ngrams
```

![Alt text](images/beat_strength_ng.png)

Results from the `beatStrengths` method should **not be sent to the `regularize` method**. Read more about `regularize` at [06_Durations](06_Durations.md).


-----
## Sections in this guide

  * [01_Introduction_and_Corpus](/tutorial/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](/tutorial//02_Notes_Rests.md)
  * [03_Durations](/tutorial//03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](/tutorial//04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](/tutorial//05_Detail_Index.md)
  * [06_Melodic_Intervals](/tutorial//06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals](/tutorial//07_Harmonic_Intervals.md)
  * [08_Contrapuntal_Modules](/tutorial//08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](/tutorial//09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](/tutorial//10_Lyrics_Homorhythm.md)
  * [11_Cadences](/tutorial//11_Cadences.md)
  * [12_Presentation_Types](/tutorial//12_Presentation_Types.md)
  * [13_Musical_Examples_Verovio](/tutorial//13_Musical_Examples_Verovio.md)
  * [14_Model_Finder](/tutorial//14_Model_Finder.md)
  * [15_Network_Graphs](/tutorial//15_Network_Graphs.md)
  * [16_Python_Basics](/tutorial//16_Python_Basics.md)
  * [17_Pandas_Basics](/tutorial//17_Pandas_Basics.md)
  * [18_Visualizations_Summary](/tutorial//18_Visualizations_Summary.md)
  * [19_Music21_Basics](/tutorial//18_Music21_Basics.md)
  * [20_Melodic_Interval_Families](/tutorial//20_Melodic_Interval_Families.md)
  * [99_Local_Installation](/tutorial//99_Local_Installation.md)