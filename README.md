# CRIM Intervals:  Python Tools for the Analysis of Encoded Music Scores

### Current Version: 2.0.49

[CRIM Intervals on github](https://github.com/HCDigitalScholarship/intervals/tree/main)

## Install CRIM Intervals and its Dependencies

Install with pypi package manager:  `pip install crim_intervals`

## About CRIM Intervals

Based on [**Python**](https://www.python.org/) and [**Pandas**](https://pandas.pydata.org/), and Mike Cuthbert's excellent **music21** (https://web.mit.edu/music21/), **CRIM Intervals** is a pattern finding engine for musical scores, with an emphasis on the kinds of melodic, harmonic, and contrapuntal patterns found in Renaissance polyphony. It has been developed as a primary data analysis tool for **Citations:  The Renaissance Imitation Mass** (http://crimproject.org and https://sites.google.com/haverford.edu/crim-project/home), directed by Professor Richard Freedman (Haverford College, USA), in partnership with dozens of researchers and students around the world. Contact rfreedma at haverford.edu to learn more about the project, and how you can take part.

**File Formats**: CRIM Intervals will analyze scores encoded in several widely-used formats:  MEI, MusicXML, and MIDI.  Results will vary according to the editorial practices used in the underlying transcriptions and editions.  

**The CRIM Intervals Web Application**:  Get started quickly with the [CRIM Intervals Streamlit Application](https://crimintervals.streamlit.app/), which requires no coding sklls.  You can work with the CRIM Corpus, or import your own pieces, producing analytic tables, visualizations, and other results that you can download for use in publications and teaching.  The web app is free and requires no special account or software installation.  Tutorials are available on the site itself, with pointers back to the code and tutorials here on CRIM Intervals itself.

**Learn How Others are Using CRIM Intervals** via [CRIM Essays and Experiments](https://crimproject.org/about/essays_experiments/), which assembles recent work by over two-dozen scholars and students from around the world. Find out what is possible, what others are thinking about, and how you might use their work to advance your teaching and research.

## Getting Started with CRIM Intervals

This respository contains the CRIM Intervals library itself, along with tutorials that explain the various methods, and Jupyter Notebooks make them easy to use for your research and teaching.  There are various ways to get started:

- The [CRIM Intervals Streamlit Application](https://crimintervals.streamlit.app/), which requires no coding sklls.  You can work with the CRIM Corpus, or import your own pieces, producing analytic tables, visualizations, and other results that you can download for use in publications and teaching.

- Install and run CRIM Intervals (along with the Notebooks) locally with **Anaconda Navigator, VS-Code, and Jupyter**.  See Richard Freedman's [Encoding Music course page](https://github.com/RichardFreedman/Encoding_Music/blob/main/01_Tutorials/02_Anaconda_VS_Code_Jupyter.md) to learn how.

- Install the latest version of CRIM Intervals library via [pypi.org](https://pypi.org/project/crim-intervals/).

- Run CRIM Intervals via a free **Jupyter-hub maintained by Haverford College** (contact rfreedma at haverford.edu) to obtain an account. 

## The Basics
CRIM Intervals begins by importing one (or more) MEI, MusicXML, and MIDI files, for example: `piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')` Once imported this piece object can be explored in various ways. piece.notes(), for instance, produces a dataframe in which each staff (voice part) is represented as a column of events--notes, rests, durations, lyrics, etc. Other methods (see the list below) in turn present these basic events in many different ways: as melodic intervals, harmonic intervals, n-grams, contrapuntal "modules", and so on.

There are many ways to configure these basic methods. For instance intervals can be diatonic, or chromatic, or with (and without) 'quality' (such as M3 vs m3). They can also be simple or compound (a tenth in the latter would be a third in the former).Unisons can be combined (something helpful for comparing similar melodies), or events can be taken at actual durations or 'sampled' at some regular durational span.

Complete documentation of each method capacities is available via doc.strings via this command `print(model.YourMethod.__doc__)`, where you will replace 'YourMethod' with the name of the individual method, for example `print(piece.melodic.__doc__)`.

Results are reported in **Pandas** dataframes (and thus exportable in a variey of standard formats for further analysis), and also via several visualizations methods.

Some methods in **CRIM Intervals** also work with [**CRIM Project**](http://crimproject.org) data created by human observers.


## Key Methods in CRIM Intervals

### Melody, Harmony, Rhythm, Lyrics and NGrams

- **piece.notes()**, which finds all the notes and rests in a score, with a tabular score-like representation of the pitches, pitch classes, and durations (expressed in music21 "offsets", in which each quarter note corresponds to the value of 1.0). It can also derminte the location of any note as a measure+beat reference with detailIndex
- **piece.melodic()**, which finds melodic intervals in any voice part, with various options for diatonic, chromatic and zero-based distances. Intervals can be compound (distinguishing between tenths and thirds, for instance), or simple, and can include quality (distinguishing major and minor thirds, for instance), or not.
- **piece.harmonic()**, which finds harmonic intervals between every combination of two voices in a piece, with various options for diatonic and chromatic. These intervals can also be directed (as when a tenor voice sounds above the altus), or not.
- **piece.lyrics()** (for every note)
- **piece.durations()**, with quarter-note = 1.0, as per music21.
- **piece.ngrams()**, which finds n-grams of any length in each voice part. n-grams are frequently used in linguistic analysis (), and can help us find repeating patterns within and among works. The ngram tool can be used for any of the methods above: melodic, harmonic, durations, lyrics. By default it finds contrapuntal modules, which represent in numerical values a combination of the vertical intervals made between any two voices with the melodic intervals heard in the motion of the lower voice. A module of `7_Held 6_-2, 8` for instance, represents vertical intervals of `7, 6, 8` between two voices and in the lower voice a tied note followed by a descending second. Together these five events represent a typical cadence formula. Repeating modules are a key part of Renaissance contrapuntal style.

It is also possible to apply various **edit distance tools** to many of these patterns, thus allowing users to find **exact** and **close matches**.

### Classification of Contrapuntal Types
CRIM Intervals also include advanced methods that use combinations of the methods detailed above to predict "contrapuntal types" commonly found in Renaissance polyphony.

- **Cadences** are one such type: `piece.cadences()` can find them with a high degree of accuracy.
- We have also developed a method that predict various **imitative textures, including Fugas, Imitative Duos, Non-Imitative Duoes, and Periodic Entries** (as Peter Schubert has named them): `piece.presentationTypes()`.
- It is also possible to accurately identify **homorhythmic passages** (where sets of voices move in the same durations and declaim the same lyrics): `piece.homorhythm()`.

In each case we there are various options users can select to refine the searches, including various tools that allow for **similar no less than exact matches**. Melodic and rhythmic 'flexing' are key parts of Renaissance counterpoint. These methods are too complex to summarize in a short space. But they are powerful tools for machine prospecting of musical works.

### Heatmaps, Graphs, and Networks
CRIM Intervals also features tools that help us visualize musical events in different ways, including:

- **bar charts and histograms** of events (such as notes, or intervals), which are useful for understand ranges, distributions, and other large-scale distribution of categorical data
- **heatmaps**, showing where in a piece patterns (such as repeating n-grams) occur
- **radar plots**, used to show cadences in a radial plot that reveals the tonal profile of a composition (or a corpus of works)
- **progress charts**, showing a cadences in a series (from start to finish)
- **network diagrams**, showing related patterns or pieces

### One Piece, or a Corpus

CRIM Intervals methods can also be applied to a corpus of pieces. We first define a corpus: `corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0006_1.mei', 'https://crimproject.org/mei/CRIM_Mass_0006_2.mei', 'https://crimproject.org/mei/CRIM_Mass_0006_3.mei'])`, then specify a method to run against each piece in the corpus: `corpus.batch(func=ImportedPiece.cadences)`. The results are reported as a combined dataframe.

### Render Scores (or Excertps) with Verovio

- CRIM Intervals also has the capacity to render results as modern score with Laurent Pugin's [Verovio](https://www.verovio.org/index.xhtml) (for example `piece.verovioCadences()`), as well as reporting them as data frames and visualizations.

## Credits and Intellectual Property Statement

### CRIM Intervals is the Work of Many Hands:

- Andrew Janco (Haverford College/Universit of Pennsylvania)
- Freddie Gould (Haverford College/Audible)
- Trang Dang (Bryn Mawr College)
- Alexander Morgan (EcoRate)
- Daniel Russo-Batterham (Melbourne University)
- Richard Freedman (Haverford College)
- Oleh Shostak (Haverford College)
- Edgar Leon (Haverford College)
- Harrison West (Haverford College)
- Patty Guardiola (Haverford College)
- Anna Lacy (Haverford College)

### CRIM Intervals is made possible generous support from:

- Haverford College
- The American Council of Learned Societies

All CRIM intervals tools are available via a **Creative Commons** license (Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)):  https://creativecommons.org/licenses/by-sa/4.0/.

## Sections in this guide

  * [01_Introduction_and_Corpus](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/02_Notes_Rests.md)
  * [03_Durations](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/05_Detail_Index.md)
  * [06_Melodic_Intervals](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/07_Harmonic_Intervals.md)
  * [08_Contrapuntal_Modules](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/10_Lyrics_Homorhythm.md)
  * [11_Cadences](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/11_Cadences.md)
  * [12_Presentation_Types](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/12_Presentation_Types.md)
  * [13_Musical_Examples_Verovio](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/13_Musical_Examples_Verovio.md)
  * [14_Model_Finder](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/14_Model_Finder.md)
  * [15_Network_Graphs](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/15_Network_Graphs.md)
  * [16_Python_Basics](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/16_Python_Basics.md)
  * [17_Pandas_Basics](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/17_Pandas_Basics.md)
  * [18_Visualizations_Summary](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/18_Visualizations_Summary.md)
  * [19_Music21_Basics](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/19_Music21_Basics.md)
  * [99_Local_Installation](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/99_Local_Installation.md)
