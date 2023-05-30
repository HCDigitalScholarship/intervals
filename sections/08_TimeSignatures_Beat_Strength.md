# Time Signatures

## View Time Signatures with `timeSignatures()`

For any piece, it is possible to return a dataframe containing each new time signature and the offset at which it appears:

    piece.timeSignatures()

There are no parameters to set with this function.  But it can be called as a parameter from `detailIndex`:

    nr = piece.notes()
    piece.detailIndex(nr, t_sig=True)

See more at [09_DetailIndex](09_DetailIndex.md).



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