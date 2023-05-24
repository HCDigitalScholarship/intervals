# Introduction

## Importing a piece

  * CRIM Intervals begins by importing one or more MEI, MusicXML, or MIDI Files. This can be done directly, as shown:  
`piece = importPiece('https://crimproject.org/mei/CRIM_Model_0008.mei')`
  * The field within the `importPiece()` function can be either a url or local file path, and must be surrounded by quotes as shown  
  * After importing a piece from a url or local path, the piece's successful import can be confirmed by printing out its metadata:   
`print(piece.metadata)`  

## Importing multiple pieces at once

  * The CRIM Interval library also allows the user to import multiple pieces at once through the `CorpusBase()` function  
  * This function operates similarly to the `importPiece()` function, but accepts a list of piece urls or paths instead of a single one  
  * Note that the function must be formatted as follows, including quotes surrounding each name, [brackets] to indicate that the input is a list, commas in between each item in the list, and a /slash at the beginning of any local path. Otherwise, the local path will be read as an online url, and the piece will not be found.  
`corpus = CorpusBase(['url_to_mei_file1.mei', 'url_to_mei_file2.mei', '/path/to/mei/file1.mei', '/path/to/mei/file2.mei'])`  
  * The CRIM Interval functions will allow the same examinations of a group of pieces as they would of a single piece  

## Operations applied to pieces
  * Once one or more pieces have been imported, they can be examined and analyzed through a wide variety of different functions. Most of these functions follows one of a few common formats:  
`pieceName.func()`  
OR  
`pieceName.func(p1)`  
OR  
`pieceName.func(param_1 = p1, param_2 = p2, ... param_X = pX)`  
  * If the function does not require any parameter inputs, or you do not wish to modify any of the function's default parameters, the parentheses may be left blank, but must still be included. Ommitting any parameter from a function will apply the function's default setting for that parameter  
  * The specific details of how to format the function will be dependent on the function. The function's documentation can be read to view the details associated with how to apply a given function.  
 
## Help and Documentation

  * The documentation associated with each function can be read with a line of the following sample format:  
`print(piece.notes.__doc__)`
  * This line would print out the documentation (`.__doc__`) associated with the function `notes()`, a function applicable to the object `piece`
  * Note that to print the documentation for a function, some object able to utilize that function must be used in the command line as shown above

# Credits and Intellectual Property Statement

CRIM Intervals contributors include:

- Andrew Janco (Haverford College)
- Freddie Gould (Haverford College)
- Trang Dang (Bryn Mawr College)
- Alexander Morgan (McGill University)
- Daniel Russo-Batterham (Melbourne University)
- Richard Freedman (Haverford College)

CRIM Intervals is made possible generous support from:

- Haverford College
- The American Council of Learned Societies

All CRIM intervals tools are available via a **Creative Commons** license (Attribution-ShareAlike 4.0 International (CC BY-SA 4.0):  https://creativecommons.org/licenses/by-sa/4.0/.

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