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

  * When gathering N-grams, we can either search for N-grams of a specific length, or simply collect intervals until a rest is reached. By default, `n` is set to 3, so to find N-grams of 3 consecutive intervals, simply leave this parameter unspecificed and do not include it in the command line. Below is an example of a command line which will find all N-grams containing five consecutive intervals in the imported piece:  

`mel = piece.melodic(kind = "c", compound = False)`
`ngrams = mel.ngrams(n = 5)`  

  * Additionally, to find N-grams of the maximum length until a rest is found, set `n = -1`. 

### entries(): All N-grams or entries only?  

  * By default, the `ngrams()` function will find every single series of intervals of its given length, creating a moving window that will find not only the N-grams representing the beginnings of melody lines, but also those same N-grams starting from the second interval, and from the third, and so on. We can include only the N-grams beginning after a rest, section break, or fermata with the `entries()` function.  

`mel = piece.melodic(kind = "c", compound = False)`  
`ngrams = mel.ngrams(n = -1)`  
`entries = ngrams.entries()`  
Additionally, we can clean up the resulting DataFrame by removing empty rows, such as those which would have previously contained submelodies of the entry melodies:  
`cleaned_entries = entries.dropna(how = "all").fillna(' ')`  
`cleaned_entries`  

### combineUnisons (bool)  

  * 


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