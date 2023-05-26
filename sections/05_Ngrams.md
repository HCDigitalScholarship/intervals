# N-grams  

  * An **N-Gram** is a commonly used linguistic term for a continuous string of characters or events. A series of melodic and harmonic intervals in pieces of music, specifically of some length *N*, can similarly be refered to as an **N-gram**.  

## The `ngrams()` function  

  * By gathering all N-grams of a given length, we can make a DataFrame of every instance in which a series of *N* consecutive intervals is found. Then, each of these instances, or N-grams, can be specifically searched for in different pieces of music to find common melodies or harmonies across pieces. The `ngrams()` function can be applied to the DataFrame output of either the `melodic()` or `harmonic()` functions, as follows:  

`mel = piece.melodic(kind = "c", compound = False)`  
`ngrams = mel.ngrams()`  
Or alternatively,  
`ngrams = piece.melodic(kind = "c", compound = False).ngrams()`  

## `ngrams()` parameters  

### n (int)  

  * When gathering N-grams, we can either search for N-grams of a specific length, or simply collect intervals until a rest is reached.  

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