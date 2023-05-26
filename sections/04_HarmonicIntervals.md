# Harmonic Intervals

  * We have just seen how the `melodic()` function allows us to examine the points in the score where the pitch changes in a single voice, resulting in a melodic intervals. We are also able to examine harmonic intervals, which is the difference in pitch between two voices who sound a note simultaneously. This can be accomplished with the `harmonic()` function.  

## The `harmonic()` Function  

  * Harmony is one of the most important elements of music, and of musical similarity. By searching for patterns where pieces utilize certain harmonic intervals, we are able to find points of similarity within and between different pieces. The `harmonic()` function is used as follows:  

`piece.harmonic()`  
`piece.harmonic(kind = "d")`  

## `harmonic()` parameters  

### kind (str)

***These parameters are identical to those used in [the `melodic()` function](03_MelodicIntervals.md#kind-str):***  
The `harmonic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive.  
  * `kind = "q"`: Diatonic with qualities. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5).
  * `kind = "d"`: Diatonic without qualities. Provides outputs such as "8" for an octave, and "3" for a third interval.  
  * `kind = "c"`: Chromatic. Simply the difference in pitch including all intermediary notes. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5).
  * `kind = "z"`: Zero-based. Diatonic intervals, begins counting at 0 rather than 1. Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5).  

### compound (bool): Managing intervals greater than an octave  

  * The `melodic()` function contains a parameter `compound`, with a default value of `True`, and can be modified as follows:  

`piece.melodic(compound = False)`

  * The default `True` value of this paramter indicates that compound intervals (intervals spanning more than an octave) should be analyzed as if the second note in the interval was its equivalent pitch within the octave of the first note. For example, by default an interval from C4 to D5 would be treated as a diatonic interval of 1, or chromatic interval of 2, since although the actual interval is greater than an octave, the pitch itself is simply C -> D. By setting this paramter to `False`, however, this same interval would instead be considerd a diatonic interval of 8, or chromatic interval of 14, reflecting the fact that the interval spans more than an octave.  
  * Note that intervals of exactly an octave will always reflect this distance regardless of how the `compound` parameter's value, rather than becoming an interval of distance 0.  

## `fillna()` and `dropna()` Functions  

  * We have previously seen the `fillna()` function which, when applied to a DataFrame, replaces all "NaN" objects with the chosen text. For example:  

`piece.harmonic().fillna('-')`  

  * We are also able to apply the `dropna()` function, which simply removes all rows (beats) from the table where no voices sound  

`piece.harmonic().dropna()`  

## Measures and beats  

  * To display DataFrames relative to measures, and beats within measures, rather than offsets across the entire piece, we can use the `detailIndex()` function, which is [documented here](09_DetailIndex.md).  

-----

## Sections in this guide

  * [01_Introduction](01_Introduction.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_MelodicIntervals](03_MelodicIntervals.md)
  * [04_HarmonicIntervals](04_HarmonicIntervals.md)
  * [05_Ngrams](05_Ngrams.md)
  * [06_Durations](06_Durations.md)
  * [07_Lyrics](07_Lyrics.md)
  * [08_Time-Signatures](08_TimeSignatures.md)
  * [09_DetailIndex](09_DetailIndex.md)
  * [10_Cadences](10_Cadences.md)
  * [11_Pandas](11_Pandas.md)