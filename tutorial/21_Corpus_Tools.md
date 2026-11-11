# Corpus Tools

## Table of Contents
1. [Introduction](#introduction)
2. [Creating a Corpus with CRIM Intervals](#creating-a-corpus-with-crim-intervals)
3. [Using the Corpus Methods](#using-the-corpus-methods)
4. [Methods](#methods)
   - [notes](#notes)
   - [note_scaled](#note_scaled)
   - [note_durs](#note_durs)
   - [note_weights](#note_weights)
   - [mel](#mel)
   - [har](#har)
   - [contrapuntal_ngrams](#contrapuntal_ngrams)
   - [melodic_ngrams](#melodic_ngrams)
   - [melodic_durational_ratios_ngrams](#melodic_durational_ratios_ngrams)
   - [harmonic_ngrams](#harmonic_ngrams)
   - [sonority_ngrams](#sonority_ngrams)
   - [cadences](#cadences)
   - [presentation_types](#presentation_types)
5. [Legacy `corpus_tools` Functions](#legacy-corpus_tools-functions)
6. [Sections in this guide](#sections-in-this-guide)

## Introduction

These tools analyze a whole corpus of pieces at once. They extract notes, calculate durations, generate intervals, and create n-grams across every piece in the corpus, and they return a single DataFrame with `Composer`, `Title`, and `Date` columns so that you can compare pieces.

Each tool is a **method of the `CorpusBase` object**. You call it directly on your corpus (for example `corpus.notes()`).

Learn about all the corpus methods in the [Documentation for CRIM Intervals](https://hcdigitalscholarship.github.io/intervals/api/main_objs/#crim_intervals.main_objs.CorpusBase).

## Creating a Corpus with CRIM Intervals

First import CRIM Intervals as usual (see [01_Introduction_and_Corpus](/tutorial/01_Introduction_and_Corpus.md)):

```python
import crim_intervals
from crim_intervals import *
import pandas as pd
```

Then build a corpus from a list of URLs or local file paths. Local file paths must begin with `/`:

```python
file_list = ['https://crimproject.org/mei/CRIM_Model_0008.mei',
             'https://crimproject.org/mei/CRIM_Mass_0005_1.mei']
corpus = CorpusBase(file_list)
```

## Using the Corpus Methods

Call each method on the corpus object and save the result as a DataFrame:

```python
corpus_notes = corpus.notes()
corpus_mel_ngrams = corpus.melodic_ngrams(ngram_length=5, kind_choice='c')
corpus_cads = corpus.cadences(include_final=True)
```

Many of the methods also take two optional parameters that help with modal and tonal studies:

- `key_sig` (bool, default `False`): adds the prevailing key signature of each piece. It uses the music21 `.sharps` convention, so `0` means no signature and `-1` means one flat.
- `include_final` (bool, default `False`; `True` for `note_durs`): adds a column with the final tone of each piece.

## Methods

### notes

Typical use: `corpus.notes(combine_unisons_choice=True, combine_rests_choice=False, key_sig=False, include_final=False)`

Creates a table of notes and rests in a corpus. The table has one row per attack or rest offset and one column per numbered voice.

Parameters:
- `combine_unisons_choice` (bool): Whether to combine consecutive attacks on the same pitch (default: True)
- `combine_rests_choice` (bool): Whether to combine consecutive rests (default: False)
- `key_sig` (bool): Whether to add a `KeySig` column (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing notes and rests for every piece

### note_scaled

Typical use: `corpus.note_scaled(combine_unisons_choice=True, combine_rests_choice=False, key_sig=False, include_final=False)`

Counts the notes and rests in a corpus and gives each count as a proportion of the piece's total (the scaled count).

Parameters:
- `combine_unisons_choice` (bool): Whether to combine consecutive attacks on the same pitch (default: True)
- `combine_rests_choice` (bool): Whether to combine consecutive rests (default: False)
- `key_sig` (bool): Whether to add a `KeySig` column (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: One row per note per piece, with `count`, `scaled_count`, `Composer`, and `Title` columns

### note_durs

Typical use: `corpus.note_durs(pitch_class=True, aggregate=False, key_sig=False, include_final=True)`

Calculates the durations of notes in a corpus.

Parameters:
- `pitch_class` (bool): Whether to use pitch classes (octave removed) instead of full note names (default: True)
- `aggregate` (bool): If False, returns one row per note. If True, returns the total duration of each pitch for each voice in each piece (default: False)
- `key_sig` (bool): Whether to add a `KeySig` column (default: False)
- `include_final` (bool): Whether to add a `Final` column, given as a pitch class (default: True)

Returns:
- `pd.DataFrame`: Columns `Composer`, `Title`, `Date`, `Voice`, `Notes`, `Durs`, plus `Final` and/or `KeySig` if you ask for them

### note_weights

Typical use: `corpus.note_weights(include_rests=True, key_sig=False, include_final=False)`

Calculates pitch-class weights by duration in a corpus. Notes are grouped by pitch class and weighted by their total duration, which gives a scaled proportion for each pitch class in each piece. Pitch classes are ordered chromatically, and flat names are standardized (for example, `D-` becomes `Db`).

Parameters:
- `include_rests` (bool): Whether to include rests in the pitch-class counts (default: True)
- `key_sig` (bool): Whether to add a `key_sig` column (default: False)
- `include_final` (bool): Whether to add a `final` column (default: False)

Returns:
- `pd.DataFrame`: Columns `pitch_class`, `count` (total duration), `scaled` (proportion of total duration), `composer`, and `title` (plus `final` and/or `key_sig` if you ask for them)

### mel

Typical use: `corpus.mel(kind_choice='d', compound_choice=True, directed_choice=True, key_sig=False, include_final=False)`

Generates melodic intervals in a corpus.

Parameters:
- `kind_choice` (str): Kind of intervals to generate, for example `'d'` for diatonic (default: `'d'`)
- `compound_choice` (bool): Whether to allow compound intervals (default: True)
- `directed_choice` (bool): Whether to show the direction of each interval (default: True)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing melodic intervals

### har

Typical use: `corpus.har(kind_choice='d', compound_choice=True, directed_choice=True, key_sig=False, include_final=False)`

Generates harmonic intervals in a corpus.

Parameters:
- `kind_choice` (str): Kind of intervals to generate (default: `'d'`)
- `compound_choice` (bool): Whether to allow compound intervals (default: True)
- `directed_choice` (bool): Whether to show the direction of each interval (default: True)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing harmonic intervals

### contrapuntal_ngrams

Typical use: `corpus.contrapuntal_ngrams(ngram_length=3, key_sig=False, include_final=False)`

Generates contrapuntal n-grams in a corpus.

Parameters:
- `ngram_length` (int): Length of n-grams to generate (default: 3)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing contrapuntal n-grams

### melodic_ngrams

Typical use: `corpus.melodic_ngrams(ngram_length=4, kind_choice='d', compound_choice=True, directed_choice=True, end_choice=False, metadata_choice=True, include_offset=False, key_sig=False, include_final=False)`

Generates melodic n-grams in a corpus.

Parameters:
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `kind_choice` (str): Kind of intervals, for example `'d'` for diatonic (default: `'d'`)
- `compound_choice` (bool): Whether to allow compound intervals (default: True)
- `directed_choice` (bool): Whether to show the direction of each interval (default: True)
- `end_choice` (bool): If False, each n-gram's position is the first note of its first interval (default: False)
- `metadata_choice` (bool): Whether to include `Composer`, `Title`, and `Date` (default: True)
- `include_offset` (bool): Whether to include the offset as well as the measure and beat (default: False)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing melodic n-grams

### melodic_durational_ratios_ngrams

Typical use: `corpus.melodic_durational_ratios_ngrams(ngram_length=4, end_choice=False, kind_choice='d', compound_choice=True, directed_choice=True, metadata_choice=True, include_offset=False, key_sig=False, include_final=False)`

Generates melodic n-grams that combine each interval with its durational ratio.

Parameters:
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `end_choice` (bool): If False, each n-gram's position is the first note of its first interval (default: False)
- `kind_choice` (str): Kind of intervals (default: `'d'`)
- `compound_choice` (bool): Whether to allow compound intervals (default: True)
- `directed_choice` (bool): Whether to show the direction of each interval (default: True)
- `metadata_choice` (bool): Whether to include `Composer`, `Title`, and `Date` (default: True)
- `include_offset` (bool): Whether to include the offset as well as the measure and beat (default: False)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing melodic and durational-ratio n-grams

### harmonic_ngrams

Typical use: `corpus.harmonic_ngrams(ngram_length=4, kind_choice='d', compound_choice=True, directed_choice=True, metadata_choice=True, againstLow_choice=False, include_offset=False, key_sig=False, include_final=False)`

Generates harmonic n-grams in a corpus.

Parameters:
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `kind_choice` (str): Kind of intervals (default: `'d'`)
- `compound_choice` (bool): Whether to allow compound intervals (default: True)
- `directed_choice` (bool): Whether to show the direction of each interval (default: True)
- `metadata_choice` (bool): Whether to include `Composer`, `Title`, and `Date` (default: True)
- `againstLow_choice` (bool): Whether to measure intervals against the lowest sounding voice (default: False)
- `include_offset` (bool): Whether to include the offset as well as the measure and beat (default: False)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing harmonic n-grams

### sonority_ngrams

Typical use: `corpus.sonority_ngrams(ngram_length=4, metadata_choice=True, include_offset=False, include_progress=True, compound=True, sort=False, minimum_beat_strength=0.0, key_sig=False, include_final=False)`

Generates sonority n-grams in a corpus. Each item pairs the sonority (all tones sounding at a moment) with the melodic interval of the lowest voice. You can leave out sonorities on weak beats with `minimum_beat_strength`. These n-grams are useful for finding repeated blocks of sonorities within and among pieces, whatever voices they are heard in.

Parameters:
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `metadata_choice` (bool): Whether to include `Composer`, `Title`, and `Date` (default: True)
- `include_offset` (bool): Whether to include the offset as well as the measure and beat (default: False)
- `include_progress` (bool): Whether to include the `Progress` column, which runs from 0 to 1 through the piece (default: True)
- `compound` (bool): Whether to allow compound intervals (default: True)
- `sort` (bool): If True, sorts intervals from largest to smallest, without unisons (default: False)
- `minimum_beat_strength` (float): Leaves out sonorities whose beat strength is not above this value (default: 0.0)
- `key_sig` (bool): Whether to add the key signature to the index (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing sonority n-grams

### cadences

Typical use: `corpus.cadences(key_sig=False, include_final=False)`

Finds the cadences in every piece in the corpus. See `ImportedPiece.cadences` and [11_Cadences](/tutorial/11_Cadences.md) for an explanation of each column. If a piece has no cadences, the method prints its title and does not raise an error.

Parameters:
- `key_sig` (bool): Whether to add a `KeySig` column with the key signature at each cadence (default: False)
- `include_final` (bool): Whether to add a `Final` column (default: False)

Returns:
- `pd.DataFrame`: DataFrame of cadences (empty, with the expected columns, if there are no cadences in the corpus)

### presentation_types

Typical use: `corpus.presentation_types(limit_to_entries=True, head_flex=1, body_flex=0, include_hidden_types=False, combine_unisons=True, melodic_ngram_length=4, kind='d', end=False)`

Finds the presentation types in every piece in the corpus. See [12_Presentation_Types](/tutorial/12_Presentation_Types.md).

Parameters:
- `limit_to_entries` (bool): Whether to limit the search to entries (soggetti that follow a rest, a long note, or a section break) (default: True)
- `head_flex` (int): How much the head of the soggetto may vary (default: 1)
- `body_flex` (int): How much the body of the soggetto may vary (default: 0)
- `include_hidden_types` (bool): Whether to include hidden types (default: False)
- `combine_unisons` (bool): Whether to combine unisons (default: True)
- `melodic_ngram_length` (int): Length of the melodic n-grams (default: 4)
- `kind` (str): Kind of intervals (default: `'d'`)
- `end` (bool): If False, each n-gram's position is the first note of its first interval (default: False)

Returns:
- `pd.DataFrame`: DataFrame containing presentation types

## Legacy `corpus_tools` Functions

Older notebooks may call these tools as functions from the `corpus_tools` module, for example `corpus_tools.corpus_notes(corpus)`. These functions still work, because each one just calls the matching `CorpusBase` method, but some of them do not support every parameter, such as `include_final`. For new work, call the methods directly on the corpus:

| Old function | `CorpusBase` method |
|---|---|
| `corpus_tools.corpus_notes(corpus, ...)` | `corpus.notes(...)` |
| `corpus_tools.corpus_note_scaled(corpus, ...)` | `corpus.note_scaled(...)` |
| `corpus_tools.corpus_note_durs(corpus, ...)` | `corpus.note_durs(...)` |
| `corpus_tools.corpus_note_weights(corpus, ...)` | `corpus.note_weights(...)` |
| `corpus_tools.corpus_mel(corpus, ...)` | `corpus.mel(...)` |
| `corpus_tools.corpus_har(corpus, ...)` | `corpus.har(...)` |
| `corpus_tools.corpus_contrapuntal_ngrams(corpus, ...)` | `corpus.contrapuntal_ngrams(...)` |
| `corpus_tools.corpus_melodic_ngrams(corpus, ...)` | `corpus.melodic_ngrams(...)` |
| `corpus_tools.corpus_melodic_durational_ratios_ngrams(corpus, ...)` | `corpus.melodic_durational_ratios_ngrams(...)` |
| `corpus_tools.corpus_harmonic_ngrams(corpus, ...)` | `corpus.harmonic_ngrams(...)` |
| `corpus_tools.corpus_sonority_ngrams(corpus, ...)` | `corpus.sonority_ngrams(...)` |
| `corpus_tools.corpus_cadences(corpus)` | `corpus.cadences(...)` |
| `corpus_tools.corpus_presentation_types(corpus, ...)` | `corpus.presentation_types(...)` |

## Sections in this guide

  * [01_Introduction_and_Corpus](/tutorial/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](/tutorial/02_Notes_Rests.md)
  * [03_Durations](/tutorial/03_Durations.md)
  * [04_TimeSignatures_Beat_Strength](/tutorial/04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](/tutorial/05_Detail_Index.md)
  * [06_Melodic_Intervals](/tutorial/06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals_Sonorities](/tutorial/07_Harmonic_Intervals_Sonorities.md)
  * [08_Ngrams_Heat_Maps](/tutorial/08_Ngrams_Heat_Maps.md)
  * [09_Contrapuntal_Modules](/tutorial/09_Contrapuntal_Modules.md)
  * [10_Lyrics_Homorhythm](/tutorial/10_Lyrics_Homorhythm.md)
  * [11_Cadences](/tutorial/11_Cadences.md)
  * [12_Presentation_Types](/tutorial/12_Presentation_Types.md)
  * [13_Musical_Examples_Verovio](/tutorial/13_Musical_Examples_Verovio.md)
  * [14_Model_Finder](/tutorial/14_Model_Finder.md)
  * [15_Network_Graphs](/tutorial/15_Network_Graphs.md)
  * [16_Python_Basics](/tutorial/16_Python_Basics.md)
  * [17_Pandas_Basics](/tutorial/17_Pandas_Basics.md)
  * [18_Visualizations_Summary](/tutorial/18_Visualizations_Summary.md)
  * [19_Music21_Basics_MEI](/tutorial/19_Music21_Basics_MEI.md)
  * [20_Melodic_Interval_Families](/tutorial/20_Melodic_Interval_Families.md)
  * [21_Corpus_Tools](/tutorial/21_Corpus_Tools.md)
  * [99_Local_Installation](/tutorial/99_Local_Installation.md)
