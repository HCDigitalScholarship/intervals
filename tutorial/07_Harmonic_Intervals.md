# Finding the Harmonic Intervals in Pieces  

We have just seen how the `melodic()` function allows us to examine the points in the score where the pitch changes in a single voice, resulting in a melodic intervals. We are also able to examine harmonic intervals, which is the difference in pitch between two voices who sound a note simultaneously. This can be accomplished with the `harmonic()` function.  

## The `harmonic()` Function  

Harmony is one of the most important elements of music, and of musical similarity. By searching for patterns where pieces utilize certain harmonic intervals, we are able to find points of similarity within and between different pieces. In its simplest form, `harmonic()` simply produces a DataFrame of each harmonic interval present in a piece, between all possible voice pairs:  

    piece.harmonic()  

![Alt text](images/har_1.png)

The function can, however, be modified by each of its parameters:  
* `kind`, for controlling if diatonic, chromatic, or other types of intervals are reported; default is diatonic  
* `directed`, for controlling whether the report is simply a raw interval, or also reports whether it goes up or down (indicated with a '-' if down); default includes direction  
* `compound`, whether intervals larger than an octave are reported as simpler versions; default reports compounds as they actually appear  
* `againstLow`, whether harmonic intervals are produced for every combination of voices, or just between each non-lowest voice and the lowest active voice at each harmonic offset; default generates every combination of voices

## `harmonic()` Parameters  

### Differentiating Between Diatonic, Chromatic, and Other Intervals: The `kind` Parameter  

The `harmonic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive:  

**Diatonic with qualities**. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5):  

    piece.harmonic(kind = 'q')  

**Diatonic without qualities**. Provides outputs such as "8" for an octave, and "3" for a third interval:  

    piece.harmonic(kind = "d")  

![Alt text](images/har_2.png)

**Chromatic**. Simply the difference in pitch including all intermediary notes. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5):  

    piece.harmonic(kind = "c")  

**Zero-based**. Diatonic intervals, begins counting at 0 rather than 1. Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5):  

    piece.harmonic(kind = "z")  

### Up and Down vs. Aboslute: The `directed` Parameter  

By default, `directed = True`, which causes the melodic intervals to report their direction; "4" is an ascending fourth; "-4" is descending. It might be useful, however, simply to report the absolute distance without direction, such as if the aim is to know how many harmonic intervals of a sixth appear in a piece regardless of their direction.  In this case, use `directed = False`.  

    #Default value:  
    piece.harmonic(directed = True)  

[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "-4"  

    piece.harmonic(directed = False)  

[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "4"  

### Managing Intervals Greater than an Octave: The `compound` Parameter  

The `harmonic()` function contains a parameter `compound`, with a default value of `True`. This means that intervals with a span greater than an octave will always be returned as such.  The interval from C4 to E5 would be a diatonic 10, a chromatic 16, M10 using 'with quality', and 9 using 'zero-based diatonic'. 

    piece.harmonic(compound = True)

Using `piece.harmonic(compound = False)`, in contrast, analyzes all intervals as if they are within a octave (what musicians call the 'simple' intervallic distances). In this case the interval from C4 to E5 would be a diatonic 3, a chromatic 4, M3 using 'with quality', and 2 using 'zero-based with quality'. Note that an octave itself is not reduced to a unison.  

![Alt text](images/har_3.png)

### Harmonic Intervals Between All Voice Pairs, or Only Comparing to the Lowest Voice? The `againstLow` Parameter  

By default, `harmonic()` generates a DataFrame of the harmonic intervals between **ALL** voice pairs present at a given offset. This is the case when the `againstLow` parameter is set to its default, `False`. Alternatively, however, we may wish to explore each voice's harmonic relationship only to the lowest voice present at each offset, and not need other harmonic pairs creating clutter in our DataFrame output. When changed to `True`, harmonic intervals will only be shown between the lowest voice and each other voice at a given offset:  

    piece.harmonic(againstLow = True)  

![Alt text](images/har_4.png)

This means that if a piece contained a Bass, Tenor, Alto, and Soprano voice, all four voices were sounding, and `againstLow` was set to **True**, `harmonic()` will generate the interval between the Bass and the Tenor, the Bass and the Alto, and the Bass and the Soprano. It will **NOT** generate any harmonic interval between the Tenor and Alto, Tenor and Soprano, or Alto and Soprano. The same logic would also apply even if the Bass was not present, where only the harmonic intervals appearing would be between the Tenor and Alto voices, and between the Tenor and Soprano voices.  

### Dealing with Consecutive Pitch Repetition/Rests: The `combineUnisons` and `combineRests` Parameters:  

Unlike the `notes()` functions, the `harmonic()` function does not contain `combineUnisons` or `combineRests` parameters. These parameters, however, can still be used in conjunction with the `harmonic()` function as follows:  

    nr_no_unisons = piece.notes(combineUnisons = True)
    piece.harmonic(df = nr_no_unisons)  

Or (though less useful),  

    nr_separate_rests = piece.notes(combineRests = False)  
    piece.harmonic(df = nr_separate_rests)  

## `fillna()` and `dropna()` Functions  

We have previously seen the `fillna()` function which, when applied to a DataFrame, replaces all "NaN" objects with the chosen text. For example:  

    piece.harmonic().fillna('-')  

We are also able to apply the `dropna()` function, which (by default) removes all rows (beats) from the table consisting *entirely* of "NaN" values.  

    piece.harmonic().dropna()  

This would be equivalent to specifiying the function as follows:  

    piece.harmonic().dropna(how = 'all')  

Alternatively, rows could be dropped if they contian *any* "NaN" values:  

    piece.harmonic().dropna(how = 'any')  

## More About Measures, Beats, and Offsets: The `detailIndex()` Function  

By default, the `harmonic()` function returns a DataFrame which indexes by offsets: That is, events in the piece are counted by which overall beat in the piece they fall on. This is useful for measuring time distances between events, but not for a human reader to refer back to the musical score itself. It is easy to include measure and beat indexes by passing the result of the function to the `detailIndex()` function as shown:  

    har = piece.harmonic()  
    har_DI = piece.detailIndex(har)  

For more information about the `detailIndex` function, consult [the function's documentation](09_DetailIndex.md).  

-----

## Sections in this guide

  * [01_Introduction_and_Corpus](01_Introduction_and_Corpus.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_Durations.md](03_Durations.md)
  * [04_Time-Signatures](04_TimeSignatures.md)
  * [05_DetailIndex](05_DetailIndex.md)
  * [06_MelodicIntervals](06_MelodicIntervals.md)
  * [07_HarmonicIntervals](07_HarmonicIntervals.md)
  * [08_Modules](08_Modules.md)
  * [09_Ngrams_Heatmaps](09_Ngrams_Heatmaps.md)
  * [10_Lyrics_Homorhythm](10_Lyrics_Homorhythm.md)
  * [11_Cadences](11_Cadences.md)
  * [12_Presentation_Types](12_Presentation_Types.md)
  * [13_Model_Finder](13_Model_Finder.md)
  * [14_Visualizations_Summary](14_Visualizations_Summary.md)
  * [15_Network_Graphs](15_Network_Graphs.md)
  * [16_Python_Basics](16_Python_Basics.md)
  * [17_Pandas](17_Pandas_Basics.md)