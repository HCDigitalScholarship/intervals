# Introduction

## Importing pieces
### Import a Single Piece and Check Metadata for Title and Composer
  * Importing a piece is done by combining a prefix for the location of the piece with the file name of the piece itself
  * To import from either a local folder or the CRIM website, choose between the following prefixes, respectively
`prefix = 'Music_Files/'`
`prefix = 'https://crimproject.org/mei/'`
  * Then, add the name of the file itself:
`mei_file = 'CRIM_Model_0032.mei'`
  * Finally, combine these fields, import the resulting link, and (optionally) confirm the piece's successful import by printing out its metadata:
`url = prefix + mei_file`
`piece = importScore(url)`
`print(piece.metadata)`

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