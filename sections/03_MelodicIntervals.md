# Melodic Intervals

  * We have previously seen how `piece.notes()` can output a table of each time a note in the piece changes. Using functions in the CRIM Intervals library, we are also able to create tables of how far the intervals between notes are themselves, rather than simply providing a list of notes.  

## The `melodic()` Function  

  * One of the most important tools for determining the similarity between pieces --the primary purpose of the CRIM Intervals library-- is the ability to determine the distance between subsequent pitches in a piece, or melodic intervals. These melodic intervals form patterns, which can be searched for either wihin a piece or across multiple different pieces to notice similarities in their melodies. The `melodic()` function is used as follows:  

`piece.melodic()`  
`piece.melodic(kind = "d")`  

## `melodic()` parameters  

### kind (str): Diatonic vs. Chromatic intervals

The `melodic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive.  
  * `kind = "q"`: Diatonic with qualities. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5).
  * `kind = "d"`: Diatonic without qualities. Provides outputs such as "8" for an octave, and "3" for a third interval.  
  * `kind = "c"`: Chromatic. Simply the difference in pitch including all intermediary notes. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5).
  * `kind = "z"`: Zero-based. Diatonic intervals, begins counting at 0 rather than 1. Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5).  

### compound (bool): Managing intervals greater than an octave ***FIXME***  

  * The `melodic()` function contains a parameter `compound`, with a default value of `True`, and can be modified as follows:  

`piece.melodic(compound = False)`

  * The default `True` value of this paramter indicates that compound intervals (intervals spanning more than an octave) should be analyzed as if the second note in the interval was its equivalent pitch within the octave of the first note. For example, by default an interval from C4 to D5 would be treated as a diatonic interval of 1, or chromatic interval of 2, since although the actual interval is greater than an octave, the pitch itself is simply C -> D. By setting this paramter to `False`, however, this same interval would instead be considerd a diatonic interval of 8, or chromatic interval of 14, reflecting the fact that the interval spans more than an octave. Note that intervals of exactly an octave will always reflect this distance regardless of how the `compound` parameter's value.

### combineUnisons (bool)  

  * Similarly to the `notes()` functions, the `melodic()` function contains an identical `combineUnisons` parameter, with a default value of `False`. By default, the `notes()` function will interpret every note individally, even if it is the same pitch as the note immediately preceeding it. Rather than treating unisons as intervals, setting this paramter to `True` will prevent the unison from being recognized as any interval at all, simply treated as if it was one longer note held for a duration equal to the sum of the invidual notes.
  * These two parameters can be controlled simultaneously as follows (as per previous examples, and general python syntax):  

`piece.melodic(compound = False, combineUnisons = True)`  

### unit (int): Modifying interval polling period  

  * The `melodic()` function contains a parameter `unit`. This parameter determines how frequently a row of the DataFrame table is printed. When the value of the `unit` parameter is unspecified, it will default to a value of 0, which indicates that the table will generate a row for every time an interval is found, regardless of how frequently or infrequently this occurs, and regardless of whether or not intervals are found at regular or irregular offsets. This is the most efficient way to display all intervals of a piece.  
  * Passing a value to this parameter, as shown in the line below, will instead enforce a regularly occuring polling period at which a line will generate the interval at a given offset. A value of 1 will generate a row for every offset, or every beat of a piece. A value of 2 will generate a row for every two offsets, or every other beat/every 2 beats of a piece.  

`piece.melodic(unit = "4")`  

  * Note that changing the value of the `unit` parameter will only change which rows of the DataFrame are displayed, but will not change the data contained in the table itself. A table generated with `unit = 4` will generate and print the intervals from beat 1 to beat 2, from beat 5 to beat 6, and so on. It will **NOT** find the interval from beat 1 to beat 4, from beat 5 to beat 8, and so on.  

### directed (bool): Toggling indicators of intervals' directions  

  * The `melodic()` function contains a parameter `directed`, with a default value of True. This parameter indicates whether or not intervals return if the movement was up or down as follows:  

`piece.melodic(directed = True)`  
> [C5 -> G5] returns diatonic interval of "4"  
> [G5 -> C5] returns diatonic interval of "-4"  

`piece.melodic(directed = False)`  
> [C5 -> G5] returns diatonic interval of "4"  
> [G5 -> C5] returns diatonic interval of "4"  

### end (bool): Placing intervals at beginning or ending timeframe  

  * The `melodic()` function contains a parameter `end`, with a default value of True. This parameter indicates if a melodic interval is associated with the first or second note in its interval.  
  * When set to `True`, intervals are associated with their second note. For example:  

`piece.melodic(end = True)` (default) with a C5 on beat 1 and a D5 on beat 2  
> returns diatonic interval of 1, or chromatic interval of 2, on **beat 2**  

`piece.melodic(end = False)` with a C5 on beat 1 and a D5 on beat 2  
> returns diatonic interval of 1, or chromatic interval of 2, on **beat 1**  

### df (DataFrame): Optional ***Clarify: after finding offset range of some harmony as a DataFrame, return a DataFrame of its melody, for example***  

  * Optionally, the `df` parameter of the `melodic()` function can be substituted with any DataFrame you wish to find the melodic interval of. The parameter's default `None` value will simply run the function on itself.  

`piece.melodic()` (Default)  
`piece.melodic(df = NameOfOtherDataFrame)` (Optional replacement)  

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