# Cadences

## The `piece.cadences()` Function in Brief

CRIM Intervals includes a powerful tool that identifies cadences according to the combinations of two-voice modules that describe the typical contrapuntal motion between the various cadential voice functions (CVF) heard in Renaissance polyphony: cantizans and tenorizans, cantizans and altizans, etc.

For a quick report, run:

	`piece.cadences()`  

The dataframe reported by `piece.cadences()` is quite detailed, but includes (most notably):

* **Cadence Tone** (the goal pitch, determined by the final perfect sonority)
* **Cadence Type** (authentic, phrygian, and so on, according to the CRIM Controlled Vocabulary)
* **Modifications** (evaded, incomplete, etc)
* **Contextual Information** (the place and disposition of the cadence relative to the rest of the piece)
* *Much more!* (see below for details)

The tool uses **modular ngrams** to identify conjunctions of these pairs in order to predict cadences of various kinds. But there are many combinations, especially once we consider that voices functions (or roles) can be displaced (as when the tenorizans role appears in the Superius part and the cantizans appears in the Tenor part), or through irregular motion, and even interrupted, as when a voice is suddenly silent.

It is possible to check all of the **cadential voice functions (CVFs)** for a given piece below. But this tool also conveniently labels the cadences according to type, tone, evaded and also provides information about the relative place within the piece, the adjacent cadences, and many other features, too.

Note: **Measure** and **Beat** columns are in the *body of the table*, not at the Index.

## The Column Headings for `piece.cadences()` Output in Detail:

<!-- Need sample image -->

* The **Key** column is the string used by the classifier to determine the label. "BC1" for instance, means "bassus, cantus, and one leading tone". Note that these letters appear in alphabetical order, not the order of the voices in the score.
<!-- check spelling of the types -->
* The **CadType** is a high-level label: 

  * **Clausula Vera** is for cadences involving only Cantizans and Tenorizans; 
  * **Authentic** is for Cantizans and Bassizans (and possibly the Tenorizans, too). 
  * **Phrygian Clausula Vera** is like Clausula Vera but with the half-step motion in the downward-moving (Tenorizans) part. Phrygian corresponds to Authentic, except that the Bassizans of course moves up a fifth or down a fourth, as is normally the case when the Tenorizans descends by half=step. 
  * **Altizans Only** is in cases where the Cantizans is missing and the Altizans role moves to a fifth above the lowest voice. 
  <!-- Consider writing out all the other types and their defs -->
  *See `print(piece.cvfs.__doc__)` for other labels.
  * 
* **Leading Tones** is the count of leading tones motions
* **CVFs** are the Cadential Voice Functions, and are listed in order from top to bottom as they appear in the score. See print(importedPiece.cvfs.__doc__) for details.
* The **Low** and **Tone** columns give the pitches of the lowest sounding pitch (in any voice) at the perfection, and the goal tone of the cantizans (or altizans if there is no cantizans) respectively.
* **RelLow** is the lowest pitch of each cadence shown as an interval measured against the last pitch in the Low column. 
* Likewise, **RelTone** is the cadential tone shown as an interval measured against the last pitch in the Tone column.
* The **SinceLast** and **ToNext** columns are the time in quarter notes since the last or to the next cadence.
* The **Progress** column is a relative indication of position in the piece. `0` is the beginning of the piece; `1.0` is the end of the piece.
* **Sounding** is the number of voices heard at the end of the cadence.

<!-- Check print statement  -->
Read more via the documentation: `print(piece.cadences.__doc__)` and especially `print(piece.cvfs.doc)` for the voice labels.

View the **Cadential Voice Function** and **Cadence Label** tables [here](https://github.com/HCDigitalScholarship/intervals/tree/main/intervals/data/cadences/). These can easily be updated with revised or new cadence types.

## The Cadential Voice Functions Explained

<!-- They all need examples! -->


<!-- Check to see that these are current! -->
**Realized Cadential Voice Functions:**

* "C": cantizans motion up a step (can also be ornamented e.g. Landini)
* "T": tenorizans motion down a step (can be ornamented with anticipations)
* "B": bassizans motion up a fourth or down a fifth
* "A": altizans motion, similar to cantizans, but cadences to a fifth above a tenorizans instead of an octav*e
* "L": leaping contratenor motion up an octave at the perfection
* "P": plagal bassizans motion up a fifth or down a fourth
* "Q": quintizans, like a tenorizans, but resolves down by fifth or up by fourth to a fourth below the goal tone of a cantizans or an octave below the goal tone of an altizans
* "S": sestizans, occurring in some thicker 16th century textures, this is where the agent against the cantizans is already the cantizans' note of resolution (often results in a simultaneous false relation); the melodic motion is down by third at the moment of perfection*

**Evaded Cadential Voice Functions:**

* "c": evaded cantizans when it moves to an unexpected note at the perfection
* "t": evaded tenorizans when it goes up by step at the perfection
* "b": evaded bassizans when it goes up by step at the perfection
* "u": evaded bassizans when it goes down by third at the perfection (there are no evaded labels for the altizans, plagal bassizans leaping contratenor CVFs)
* "s": evaded sestizans when it resolves down by second

**Abandoned Cadential Voice Functions:**

* "x": evaded bassizans motion where the voice drops out at the perfection
* "y": evaded cantizans motion where the voice drops out at the perfection
* "z": evaded tenorizans motion where the voice drops out at the perfection

The way these CVFs combine determines which cadence labels are assigned
in the `.cadences()` method.

## Show the Cadential Voice Function Keys:  the `keep_keys` Parameter

There is only one parameter for the `cadences()` function:  `keep_keys`. If `keep_keys` is set to True, the ngrams that triggered each CVF pair will be shown in additional columns in the table. `keep_keys` is False by default.

	`piece.cadences(keep_keys=True)`

## Cadences in a Corpus

The basic methods of building and working with a corpus are explained in [01_Introduction](01_Introduction.md).

In brief, to find cadences in a corpus and report the results as a single dataframe:

    #build corpus
    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                           'https://crimproject.org/mei/CRIM_Model_0009.mei'])
    #select function.  remember to omit "()"
    func = ImportedPiece.cadences
    #run function on each piece; be sure to include keyword arguments
    list_of_dfs = corpus.batch(func=func, kwargs={'keep_keys': True}, metadata=True)
    #concatenate the resulting dataframes into one
    corpus_cadences = pd.concat(list_of_dfs, ignore_index=False)
    # new order for columns:
    col_list = ['Composer', 'Title', 'Measure', 'Beat', 'Pattern', 'Key', 'CadType', 'Tone','CVFs',
                    'LeadingTones', 'Sounding', 'Low','RelLow','RelTone',
                    'Progress','SinceLast','ToNext']
    corpus_cadences = corpus_cadences[col_list]


## Summarizing and Grouping Cadence Results

**A quick way to reorganize the columns in the output:**

    cadences = piece.cadences(keep_keys=True)
    col_list = ['Measure', 'Beat', 'CadType', 'Pattern', 'Key', 'Tone','LeadingTones', 'CVFs', 'Low','RelLow','RelTone', 'Sounding', 'Progress','SinceLast','ToNext']
    cadences = cadences[col_list]

    cadences

** Group the Cadences by Tone and Type**

    cadences = piece.cadences()
    cadences.groupby(['Tone', 'CadType', 'CVFs']).size().reset_index(name='counts')

<!-- add content here -->

## Cadence Results in Score with `verovioprintCadences`

The simplest way to show cadences with Verovio: 

    piece.verovioCadences()

Or send a filtered list of cadences for printing. Create the cadence table, filter it in some way, and the pass those results to `verovioCadences()`:

    cadences = piece.cadences()
    cadences_filtered = cadences[cadences['Tone'] == 'G']
    piece.verovioCadences(cadences_filtered)

Note that pink warning messages in the output can be ignored!

<!-- add content here -->
[ ]  

## Cadence Radar and Progress Plots

<!-- add content here -->
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