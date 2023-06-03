# Cadences

CRIM Intervals includes a powerful tool that identifies cadences according to the combinations of two-voice modules that describe the typical contrapuntal motion between the various cadential voice functions (CVF) heard in Renaissance polyphony: cantizans and tenorizans, cantizans and altizans, etc.

The dataframe reported by `piece.cadences()` is quite detailed, but includes (most notably):

* Cadence Tone (the goal pitch, determined by the final perfect sonority)
* Cadence Type (authentic, phrygian, and so on, according to the CRIM Controlled Vocabulary)
* Modifications (evaded, incomplete, etc)
* Contextual information (the place and disposition of the cadence relative to the rest of the piece)
* *Much more!* (see below for details)

The tool uses **modular ngrams** to identify conjunctions of these pairs in order to predict cadences of various kinds. But there are many combinations, especially once we consider that voices functions (or roles) can be displaced (as when the tenorizans role appears in the Superius part and the cantizans appears in the Tenor part), or through irregular motion, and even interrupted, as when a voice is suddenly silent.

It is possible to check all of the cadential voice functions (CVFs) for a given piece below. But this tool also conveniently labels the cadences according to type, tone, evaded and also provides information about the relative place within the piece, the adjacent cadences, and many other features, too.

Note: **Measure** and **Beat** columns are in the *body of the table*, not at the Index.

#### The Column Headings for `piece.cadences()` in Detail:

<!-- Need sample image -->

* The **Key** column is the string used by the classifier to determine the label. "BC1" for instance, means "bassus, cantus, and one leading tone". Note that these letters appear in alphabetical order, not the order of the voices in the score.
<!-- check spelling of the types -->
* The **CadType** is a high-level label. 

* * Clausula Vera is for cadences involving only Cantizans and Tenorizans; Authentic is for Cantizans and Bassizans (and possibly the Tenorizans, too). Phrygian Clausula Vera is like Clausula Vera but with the half-step motion in the downward-moving (Tenorizans) part. Phrygian corresponds to Authentic, except that the Bassizans of course moves up a fifth or down a fourth, as is normally the case when the Tenorizans descends by half=step. Altizans Only is in cases where the Cantizans is missing and the Altizans role moves to a fifth above the lowest voice. See print(piece.cvfs.__doc__) for other labels.
Leading Tones is the count of leading tones motions
CVFs are the Cadential Voice Functions, and are listed in order from top to bottom as they appear in the score. See print(importedPiece.cvfs.__doc__) for details.
The Low and Tone columns give the pitches of the lowest sounding pitch (in any voice) at the perfection, and the goal tone of the cantizans (or altizans if there is no cantizans) respectively.
RelLow is the lowest pitch of each cadence shown as an interval measured against the last pitch in the Low column. Likewise, RelTone is the cadential tone shown as an interval measured against the last pitch in the Tone column.
The SinceLast and ToNext columns are the time in quarter notes since the last or to the next cadence.
The Progress column is a relative indication of position in the piece. 0 is the beginning of the piece; 1.0 is the end of the piece.
Sounding is the number of voices heard at the end of the cadence.
Read more via the documentation: print(ImportedPiece.cadences.__doc__) and especially print(ImportedPiece.cvfs.doc) for the voice labels

View the Cadential Voice Function and Cadence Label tables here: https://github.com/HCDigitalScholarship/intervals/tree/main/intervals/data/cadences/. These can easily be updated with revised or new cadence types.

[ ]  

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