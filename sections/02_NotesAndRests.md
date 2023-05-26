# Notes and Rests

## The `notes()` Function
  * After importing one or more pieces, the `notes()` function can be run to create a table of all of a piece's notes and rests, in order. The `notes()` function may be run in the following format:  

`piece.notes()`  
  * These notes will be printed in a table, where each new row represents the fact that any voice has changed its note. The left-most column is an index representing the offset of the change in note, where 0 represents the first note of the piece, and 1 unit of offset represents a single quarter note. Note that this index will not necessarily be regularly spaced.  
  * Each column of the `notes()` table represents a different voice of the pieces, as indicated by the headings of the table
  * By default, printing `piece.notes()` will print the first and last five rows of the table. That is, the first and last 5 points in the piece at which any voice changes in note.
  * To control how many rows are printed;  

`piece.notes().head(20)` will print only the first 20 rows of the table, while  
`piece.notes().tail(20)` will print only the last 20 rows of the table.  

## `notes()` parameters  

### combineUnisons:  

  * A unison is when a new note is sounded, but the pitch remains the same (e.g. a C5 half note followed by a C5 quarter note). the `notes()` function contains a parameter called `combineUnisons`, which defaults to `False`.  
  * When `combineUnisons` is set to `True`, any unisons will be treated as a continuation of the previous note, effectively adding a tie between those notes. As a result, the table output of the `notes()` function will not printing anything at the offset of the given note's repititon.  
  * The combineUnisons parameter may be run as follows:  

`piece.notes(combineUnisons = True)` OR `piece.notes(combineUnisons = False)` (Default)  
  * The `head()` function can be combined with `notes(combineUnisons = True/False)` as follows:  

`whole_piece = piece.notes(combineUnisons = True)`  
`whole_piece.head(20)`  
Or, more directly:  
`piece.notes(combineUnisons = True).head(20)`  

  * Beyond applications of the CRIM Intervals library, it is often more efficient in code to declare a variable, and then perform functions on that variable, rather than performing multiple functions simultaneously. This will prevent unnecessary repetitions of the same statement, saving memory as well as time.

### combineRests:  

  * The combineRests parameter operates similarly to the combineUnisons parameter, where any rests in the piece that does not preceed the first non-rest note are combined with neighboring rests (e.g. three whole rest measures in a row).
  * By default, the combineRests parameter of the `notes()` function is set to `True`. Note that this is different from the default state of the `combineUnisons` parameter. This can be controlled similarly to the `combineUnison` parameter by the following code:  

`piece.notes(combineRests = False)`  
Or, once again,  
`piece_seperate_rests = piece.notes(combineRests = False)`  
`piece_seperate_rests.head(20)`  
  
Additionally, the `combineRests()` and `combineUnisons()` parameters may be changed simultaneously as follows:  
`piece.notes(combineRests = False, combineUnisons = True).head(20)`  

### Removing "NaN"

  * If a note changes in one voice but not another, then a row will be created in the table only partially filled. This is because  the table will attempt to populate a change in note for all of the voices in the piece, but subsequent beats of a note or rest (e.g. beats 2, 3, and 4 of a whole rest) do not appear, only the first instance of the note's creation does.
  * These empty slots, which we now understand to represent a note or rest being *held* rather than ommitted are therefore printed as "NaN", which stands for "Not a Number", since the code is unable to find a value for the "missing" note.
  * To decrease the visual clutter of the table, these "NaN" outputs can be replaced with the `fillna()` function, which is used as follows:  

`piece.notes().fillna('')`

  * The `fillna()` function accepts a parameter for the text which will replace the "NaN" elements of the `notes()` output table. This field may contain empty quotes, as shown above, or another symbol such as '-':  

`piece.notes().fillna('-')`  

  * Note that the parameter of the `fillna()` function is not necessarily a text, as any valid data could be provided, such as an integer value in place of the text field. Later, we will see how it can be useful to perform the function as written below, but in many cases, it is simply most optimal to pass either an empty quote string, a dash, or some other discrete symbol to the `fillna()` function for the benefit of a human reader.  

`piece.notes().fillna(0)`  

  * Once again, the amount of rows shown by this function can be modified by adding a `.head()` function to the line, which may be placed either before or after the `fillna('')` function. For example, both of the following lines will each output the first 20 lines of the give piece, with all "NaN" elements replace by a dash:  

`piece.notes().fillna('-').head(20)`  
`piece.notes.head(20).fillna('-')`  

  * Note that this property is not true of all functions depending on their properties, so take care to order functions correctly when applying multiple functions to an object simultaneously. In general, it is good form to include the `head()` function as the last function in the line.  

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