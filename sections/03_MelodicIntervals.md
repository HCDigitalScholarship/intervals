# Melodic Intervals

  * We have previously seen how `piece.notes()` can output a table of each time a note in the piece changes. Using functions in the CRIM Intervals library, we are also able to create tables of how far the intervals between notes are themselves, rather than simply providing a list of notes.  

## The `melodic()` Function  

  * One of the most important tools for determining the similarity between pieces --the primary purpose of the CRIM Intervals library-- is the ability to determine the distance between subsequent notes. These distances form patterns, which can be searched for either wihin a piece, or accross multiple different pieces to notice similarities in their melodies. The `melodic()` function is used as follows:  

`piece.melodic()`  

  * The `melodic()` function contains a parameter `kind`, which has a default value of "q"  
    * 


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