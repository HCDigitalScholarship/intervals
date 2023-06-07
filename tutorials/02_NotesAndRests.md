# Finding the Notes and Rests in Pieces

## The `notes()` Function  

After importing one or more pieces, the `notes()` function can be run to create a table of all of a piece's notes and rests, in order:  

    piece.notes()  

These notes will be printed in a table, where each new row contains some new note in any voice. The left-most column is an index representing the offset of the change in note, where 0 represents the first note of the piece, and 1 unit of offset represents a quarter note. Note that this index will not necessarily be regularly spaced. Each column of the `notes()` table represents a different voice of the pieces, as indicated by the headings of these columns. By default, printing `piece.notes()` will print the first and last five rows of the table. That is, the first and last 5 points in the piece at which any voice changes in note. To control how many rows are printed:  

To print only the first 20 rows of the table:  

    piece.notes().head(20)  

To print only the last 20 rows of the table:  

    piece.notes().tail(20)  

While in its simplest form, the `notes()` function simply produces a DataFrame of each note or group of rests, it can be modified through its parameters:  

* `combineUnisons`, which controls how consecutive pitch repetitions are treated; default treats unisons as separate notes  
* `combineRests`, which controls how consecutive rests are treated; default sums consecutive rests into a single extended rest  

## `notes()` Parameters  

### Dealing with Consecutive Pitch Repetition: The `combineUnisons` Parameter:  

A unison is when a new note is sounded, but the pitch remains the same (e.g. a C5 half note followed by a C5 quarter note). the `notes()` function contains a parameter called `combineUnisons`, which defaults to `False`. When `combineUnisons` is set to `True`, any unisons will be treated as a continuation of the previous note, effectively adding a tie between those notes. As a result, the table output of the `notes()` function will not printing anything at the offset of the given note's repetiton. The `combineUnisons` parameter may be run as follows:  

    piece.notes(combineUnisons = True)  
    #Or, the default value:  
    piece.notes(combineUnisons = False)   

The `head()` function can be combined with `notes(combineUnisons = True)` as shown in the following examples:  

    whole_piece = piece.notes(combineUnisons = True)
    whole_piece.head(20)  

Or, more directly:  

    piece.notes(combineUnisons = True).head(20)  

The first example demonstrates declaring a variable, and then performing functions on it, while the second demonstrates performing multiple functions simultaneously. Beyond applications of the CRIM Intervals library, the first option is often more efficient when coding in general. This is because it avoids unnecessary repetitions of the same statement, saving system memory as well as time.

### Dealing with Consecutive Rests: The `combineRests` Parameter:  

The `combineRests` parameter operates similarly to the `combineUnisons` parameter, where any rests in the piece that does not preceed the first non-rest note are combined with neighboring rests (e.g. three whole rest measures in a row will be treated as a single 3 measure-long rest). By default, the `combineRests` parameter of the `notes()` function is set to `True`. Note that this is different from the default state of the `combineUnisons` parameter. This can be controlled similarly to the `combineUnison` parameter by the following code:  

    piece.notes(combineRests = False)  
    #Or, the default value:  
    piece.notes(combineRests = True)  

Or, once again, incorporated with the `head()` function;  

    piece_separate_rests = piece.notes(combineRests = False)  
    piece_separate_rests.head(20)  
  
Additionally, the `combineRests()` and `combineUnisons()` parameters may be changed simultaneously as follows:  

    piece.notes(combineRests = False, combineUnisons = True).head(20)  

### Dealing with "NaN" Outputs: The `fillna()` Function  

It is important to realize that in code, '0' is not the same as Nothing. Where the former is an integer value, the latter is the lack of any value. These 'absent values' are often called 'Nulls' or, in Python and Pandas, 'NaN' values. Inevitably, appling the CRIM Intervals functions to a piece will result in some 'NaN' values. This is because the `notes()` function, for example, indicates any point where a pitch or rest *begins*, but does not indicate when it is *held*. As a result of this, any offset of the piece where a note is held in any voice will produce a 'NaN' value in that frame. To decrease the visual clutter of the table, these "NaN" outputs can be replaced with the `fillna()` function, which is used as follows; The `fillna()` function accepts a parameter of any data to replace the "NaN" elements of the `notes()` output table. This field may contain empty quotes, as shown above, or another symbol such as '-'. Any of the following are valid ways to replace "NaN" values with a more discrete symbol (though `fillna(0)` is somewhat more specialized):  

    piece.notes().fillna('')  
    piece.notes().fillna('-')  
    piece.notes().fillna(0)  

Note that the parameter of the `fillna()` function is not necessarily a text string, as any valid data could be provided, such as an integer value in place of the text field. Later, we will examples of cases where replacing 'NaN' values with 0 rather than a text string is optimal, but in many cases, it is simply beneficial to pass some discrete symbol to the `fillna()` function for the benefit of a human reader.  

Once again, this function can be modified by adding a `.head()` function to the line:  

    piece.notes().fillna('-').head(20)  

## More About Measures, Beats, and Offsets: The `detailIndex()` Function  

By default, the `notes()` function returns a DataFrame which indexes by offsets: That is, events in the piece are counted by which overall beat in the piece they fall on. This is useful for measuring time distances between events, but not for a human reader to refer back to the musical score itself. It is easy to include measure and beat indexes by passing the result of the function to the `detailIndex()` function as shown:  

    notes_rests = piece.notes()  
    notes_rest_DI = piece.detailIndex(notes_rests)  

For more information about the `detailIndex` function, consult [the function's documentation](09_DetailIndex.md).  

-----

## Sections in this Guide

  * [01_Introduction](01_Introduction.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_MelodicIntervals](03_MelodicIntervals.md)
  * [04_HarmonicIntervals](04_HarmonicIntervals.md)
  * [05_Ngrams](05_Ngrams.md)
  * [06_Durations](06_Durations.md)
  * [07_Lyrics](07_Lyrics_Homorhythm.md)
  * [08_TimeSignatures_BeatStrength](08_TimeSignatures_BeatStrength.md)
  * [09_DetailIndex](09_DetailIndex.md)
  * [10_Cadences](10_Cadences.md)
  * [11_Pandas](11_Pandas.md)
  * [12_Modules](12_Modules.md)