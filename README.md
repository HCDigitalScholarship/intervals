# An interval-analysis based music similarity engine


### Find the project on Github 
#### Current Version: 0.3.3
- [Github](https://github.com/HCDigitalScholarship/intervals)


## About CRIM Intervals

Based on **Python** and **Pandas**, and Mike Cuthbert's excellent **music21** (https://web.mit.edu/music21/), **CRIM Intervals** is a pattern finding engine for musical scores, with an emphasis on the kinds of melodic and harmonic patterns found in Renaissance polyphony. It has been developed as a primary data analysis tool for **Citations:  The Renaissance Imitation Mass** (http://crimproject.org and https://sites.google.com/haverford.edu/crim-project/home), but can be applied and adapted to a wide range of styles.

Results are reported in **Pandas** dataframes (and thus exportable in a variey of standard formats for further analysis), and also via several visualizations methods.

Some methods in **CRIM Intervals** also work with **CRIM Project** data created by human observers.

## Getting Started with CRIM Intervals

CRIM intervals is now available in a series of interactive **Jupyter** notebooks:  [https://github.com/RichardFreedman/CRIM_Public_Notebooks](https://github.com/RichardFreedman/CRIM_JHUB).  These can in turn be downloaded and adapted for your own use.

## Key Methods in CRIM Intervals  

* `notes()`
* `melodic()`
* `harmonic()`
* `ngrams()`
* `durations()`
* `lyrics()`
* `timeSignatures()`
* `detailIndex()`  

## Credits and Intellectual Property Statement

CRIM Intervals contributors include:

- Andrew Janco (Haverford College)
- Freddie Gould (Haverford College)
- Trang Dang (Bryn Mawr College)
- Alexander Morgan (McGill University)
- Daniel Russo-Batterham (Melbourne University)
- Richard Freedman (Haverford College)
- Oleh Shostak (Haverford College)
- Edgar Leon (Haverford College)
- Harrison West (Haverford College)

CRIM Intervals is made possible generous support from:

- Haverford College
- The American Council of Learned Societies

All CRIM intervals tools are available via a **Creative Commons** license (Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)):  https://creativecommons.org/licenses/by-sa/4.0/.

## Sections in this Guide

  * [01_Introduction](tutorial/01_Introduction.md)
  * [02_NotesAndRests](tutorial/02_NotesAndRests.md)
  * [03_MelodicIntervals](tutorial/03_MelodicIntervals.md)
  * [04_HarmonicIntervals](tutorial/04_HarmonicIntervals.md)
  * [05_Ngrams](tutorial/05_Ngrams.md)
  * [06_Durations](tutorial/06_Durations.md)
  * [07_Lyrics](tutorial/07_Lyrics_Homorhythm.md)
  * [08_TimeSignatures_BeatStrength](tutorial/08_TimeSignatures_BeatStrength.md)
  * [09_DetailIndex](tutorial/09_DetailIndex.md)
  * [10_Cadences](tutorial/10_Cadences.md)
  * [11_Pandas](tutorial/15_Pandas_Basics.md)
  * [12_Modules](tutorial/12_Modules.md)