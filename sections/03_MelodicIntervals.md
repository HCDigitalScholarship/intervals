# Melodic Intervals

  * We have previously seen how `piece.notes()` can output a table of each time a note in the piece changes. Using functions in the CRIM Intervals library, we are also able to create tables of how far the intervals between notes are themselves, rather than simply providing a list of notes.  

## The `melodic()` Function  

  * One of the most important tools for determining the similarity between pieces --the primary purpose of the CRIM Intervals library-- is the ability to determine the distance between subsequent pitches in a piece, or melodic intervals. These melodic intervals form patterns, which can be searched for either wihin a piece or across multiple different pieces to notice similarities in their melodies. The `melodic()` function is used as follows:  

`piece.melodic()` 
`piece.melodic(kind = "d")`  

## `melodic()` parameters  

### kind (str)

The `melodic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive.  
  * `kind = "q"`: Diatonic with qualities. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5).
  * `kind = "d"`: Diatonic without qualities. Provides outputs such as "8" for an octave, and "3" for a third interval.  
  * `kind = "c"`: Chromatic. Simply the difference in pitch including all intermediary notes. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5).
  * `kind = "z"`: Zero-based. Diatonic intervals, begins counting at 0 rather than 1. Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5).  

### compound (bool)  

  * The `melodic()` function contains a parameter `compound`, with a default value of `True`, and can be modified as follows:  

`piece.melodic(compound = False)`

  * The default `True` value of this paramter indicates that compound intervals (intervals spanning more than an octave) should be analyzed without this consideration. For example an interval from C4 to D5 would be treated as a diatonic interval of 1, or chromatic interval of 2. By setting this paramter to `False`, this same interval would instead be considerd a diatonic interval of 8, or chromatic interval of 14.

### combineUnisons (bool)  

  * Similarly to the `notes()` functions, the `melodic()` function contains an identical `combineUnisons` parameter, with a default value of `False`. Rather than treating unisons as diatonic intervals of 1, or zero-based intervals of 0, setting this paramter to `True` will prevent the unison from being recognized as any interval at all, simply treated as if it was one longer note held for a duration equal to the sum of each invidual note or notes.
  * These parameters can be controlled simultaneously as follows (as per previous examples, and general python syntax):  

`piece.melodic(compound = False, combineUnisons = True)`  

### unit (int)  

  * The `melodic()` function contains a parameter `unit`, with a default value of 0. This parameter determines the offset interval in  the leftmost column of the table. With a value of either 0 (the default value) or 4, the table will print the melodic interval of every fourth beat in the piece (regularized to whole note). Note that changing this value does not change the time over which an interval is found, which will always be from one beat of the piece to the next, even if the table skips the intermediary beats. For example, printing a table in which there are three intervals of "1" in a row, but ommitting the middle interval, will still provide intervals of 1, rather than finding the melodic interval from the beat to the third, even though the interval between the rows of the table would now actually be "2."  
  * The following line of code would print a table such that a line is printed for the melodic intervals found every other beat (every two quarter notes):  

`piece.melodic(unit = "2")`  

### directed (bool)  

  * The `melodic()` function contains a parameter `directed`, with a default value of True. This parameter indicates whether or not intervals return if the movement was up or down as follows:  

`piece.melodic(directed = True)`  
> [C5 -> G5] returns diatonic interval of "4"  
> [G5 -> C5] returns diatonic interval of "-4"  

`piece.melodic(directed = False)`  
> [C5 -> G5] returns diatonic interval of "4"  
> [G5 -> C5] returns diatonic interval of "4"  

### end (bool)  

  * The `melodic()` function contains a parameter `end`, with a default value of True. This parameter indicates if a melodic interval is associated with the first or second note in its interval.  
  * When set to `True`, intervals are associated with their second note. For example:  

`piece.melodic(end = True)` (default) with a C5 on beat 1 and a D5 on beat 2  
> returns diatonic interval of 1, or chromatic interval of 2, on **beat 2**  

`piece.melodic(end = False)` with a C5 on beat 1 and a D5 on beat 2  
> returns diatonic interval of 1, or chromatic interval of 2, on **beat 1**  

### df (DataFrame)  

  * Optionally, the `df` parameter of the `melodic()` function can be substituted with any DataFrame you wish to find the melodic interval of. The parameter's default `None` value will simply run the function on itself.  

`piece.melodic()`: Default  
`piece.meldoci(df = NameOfOtherDataFrame)`: Optional replacement  

## Counting and Sorting Intervals  

  * These operations utilize the same functions as counting and sorting notes, since both cases simply require manipulating pandas DataFrame objects. A cheat sheet of pandas DataFrame operations can be [found here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf). For these examples, we can define a variable as our melodic interval data frame:  

`mel = piece.melodic()`  

### Count the number of rows/find the size of the DataFrame  

  * This value will be equal to the number of beats in the piece  

> mel.count()  

### Rename columns in the DataFrame  

> mel.rename(columns = {'[Superious]':'Cantus'})  

### Stack all the columns on top of each other to get one list of all the notes  

> mel.stack()  

### Stack and count the number of unique values (which will tell us how many different intervals appear in this piece)  

> mel.stack().nunique()  

### Count the number of times each interval appears in each part  

> mel.apply(pd.Series.value_counts).fillna(0).astype(int)  

### Count and sort the intervals in a single voice part: 

> mel.apply(pd.Series.value_counts).fillna(0).astype(int).sort_values("[Superious]", ascending=False)  

  * Similarly to the note order created when [sorting pitches of notes](02_NotesAndRests.md#sorting-pitches), we can define an order of intervals as follows:  

`int_order = ["P1", "m2", "M2", "m3", "M3", "P4", "P5", "m6", "M6", "m7", "M7", "P8", "-m2", "-M2", "-m3", "-M3", "-P4", "-P5", "-m6", "-M6", "-m7", "-M7", "-P8"]`  

  * This `int_order` can now be used to sort the intervals from smallest to largest, ascending to descending:  

`mel = piece.melodic().fillna("-")`  
`mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()`  
`mel.rename(columns = {'index':'interval'}, inplace = True)`  
`mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)`
`mel = mel.sort_values(by = "interval").dropna().copy()`
`mel.reset_index()`  

## Charting intervals  

  * Similarly to how we created a histogram of frequency of pitch usage per voice, we can use the Matplot library to create a chart of the frequence of interval usage:  

> %matplotlib inline  
> int_order = ["P1", "m2", "-m2", "M2", "-M2", "m3", "-m3", "M3", "-M3", "P4", "-P4", "P5", "-P5", "m6", "-m6", "M6", "-M6", "m7", "-m7", "M7", "-M7", "P8", "-P8"]  
> mel = piece.melodic()  
> mel = mel.fillna("-")  
> mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()  
> mel.rename(columns = {'index':'interval'}, inplace = True)  
> mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)  
> mel = mel.sort_values(by = "interval").dropna().copy()  
> voices = mel.columns.to_list()  
> md = piece.metadata  
> for key, value in md.items():  
>    print(key, ':', value)  

Graph options:  
> palette = sns.husl_palette(len(voices), l=.4)  
> sns.set(rc={'figure.figsize':(15,9)})  
> mel.set_index('interval').plot(kind='bar', stacked=True)


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
  * [11_Item](link.to.item)