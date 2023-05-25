# Melodic Intervals

  * We have previously seen how `piece.notes()` can output a table of each time a note in the piece changes. Using functions in the CRIM Intervals library, we are also able to create tables of how far the intervals between notes are themselves, rather than simply providing a list of notes.  

## The `melodic()` Function  

  * One of the most important tools for determining the similarity between pieces --the primary purpose of the CRIM Intervals library-- is the ability to determine the distance between subsequent pitches in a piece, or melodic intervals. These melodic intervals form patterns, which can be searched for either wihin a piece or across multiple different pieces to notice similarities in their melodies. The `melodic()` function is used as follows:  

`piece.melodic()` 
`piece.melodic(kind = "d")` 

  * The `melodic()` function contains a parameter `kind`, which has a default value of "q"  
    * `kind = "q"`: diatonic with qualities. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5).


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