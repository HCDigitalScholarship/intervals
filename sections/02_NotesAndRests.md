# Notes and Rests

## The `notes()` Function
  * After importing one or more pieces, the `notes()` function can be run to create a table of all of a piece's notes and rests, in order. The `notes()` function may be run in the following format:  
`piece.notes()`  
  * These notes will be printed in a table, where each new row represents the fact that any voice has changed its note. The left-most column is an index representing the offset of the change in note, where 0 represents the first note of the piece, and 1 unit of offset represents a single quarter note. Note that this index will not necessarily be regularly spaced.  
  * Each column of the `notes()` table represents a different voice of the pieces, as indicatd by the headings of the table
  * By default, printing `piece.notes()` will print the first and last five rows of the table. That is, the first and last 5 points in the piece at which any voice changes in note.
  * To control how many rows are printed;  
`piece.notes.head(20)` will print only the first 20 rows of the table, while  
`piece.notes.tail(20)` will print only the last 20 rows of the table.

## combineUnisons

  * A unison is when a new note is sounded, but the pitch remains the same (e.g. a half note C5 followed by a quarter note C5). the `notes()` function contains a parameter called combineUnisons, which defaults to False.  
  * When combineUnisons is set to true, any uinsons pitches will be treated as a continuation of the previous note, effectively adding a tie to those notes of the piece, and resulting in the table output of the `notes()` function not printing anything at the given offset of the given repition in pitch.  
  * The combineUnisons parameter may be run as follows:  
`piece.notes(combineUnisons = True)` OR `piece.notes(combineUnisons = False)`  
  * The `head()` function can be combined with `notes(combineUnisons = True/False)` as follows:  
`whole_piece = piece.notes(combineUnisons = False)`  
`whole_piece.head(20)`  
Or, more directly:  
`piece.notes(combineUnisons = False).head(20)`
  * Sometimes, declaring variables, such as in the first example, may be more useful, since it allows you to reference a specific condition of the piece more easily than adding `combineUnisons = True/False` to the function every time you want to reference that piece with those paremters. This type of variable declaration with specific parameters is useful in many instances not limited to applications of the CRIM Intervals library to increase your code's efficiency and prevent unnecessariily repeatedly declaring the same statement.

## combineRests

  * The combineRests parameter operates similarly to the combineUnisons parameter, 

-----

## Sections in this guide
  * [01_Introduction](01_Introduction.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_MelodicIntervals](03_MelodicIntervals.md)
  * [04_HarmonicIntervals](04_HarmonicIntervals.md)
  * [05_Lyrics](05_Lyrics.md)
  * [06_Durations](06_Durations.md)
  * [07_N-grams](07_Ngrams.md)
  * [08_Time-Signatures](08_TimeSignatures.md)
  * [09_DetailIndex](09_DetailIndex.md)
  * [10_Cadences](10_Cadences.md)
  * [11_Item](link.to.item)