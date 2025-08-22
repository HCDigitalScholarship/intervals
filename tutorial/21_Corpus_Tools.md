# Corpus Tools

## Table of Contents
1. [Introduction](#introduction)
2. [Functions](#functions)
   - [corpus_notes](#corpus_notes)
   - [corpus_note_scaled](#corpus_note_scaled)
   - [corpus_note_durs](#corpus_note_durs)
   - [corpus_mel](#corpus_mel)
   - [corpus_har](#corpus_har)
   - [corpus_contrapuntal_ngrams](#corpus_contrapuntal_ngrams)
   - [corpus_melodic_ngrams](#corpus_melodic_ngrams)
   - [corpus_melodic_durational_ratios_ngrams](#corpus_melodic_durational_ratios_ngrams)
   - [corpus_harmonic_ngrams](#corpus_harmonic_ngrams)
   - [corpus_sonority_ngrams](#corpus_sonority_ngrams)
   - [corpus_cadences](#corpus_cadences)
   - [corpus_presentation_types](#corpus_presentation_types)

## Introduction

This module provides tools for analyzing musical corpora. It offers functionality for extracting notes, calculating durations, generating intervals, and creating n-grams from musical data.

## Importing Corpus Tools for use with CRIM Intervals

Be sure to import the corpus tools before using them in your analysis. The following code snippet shows how to import the necessary functions:

```python
import crim_intervals.corpus_tools as corpus_tools
```
## Using the Corpus Tools Functions

Since these tools are part of a specific package, you can use them directly after importing. Here’s an example of how to use the `corpus_melodic` function:

```python
corpus_tools.corpus_mel(corpus)
```

This will generate melodic intervals from the provided corpus object. You can adjust the parameters as needed to fit your analysis requirements.  For example, you can specify the kind of intervals, whether to allow compound intervals, and whether to allow directed intervals.

```python
corpus_mel(corpus, kind_choice='d', compound_choice=True, directed_choice=True)
```	


## Functions

### corpus_notes(corpus, combine_unisons_choice=True, combine_rests_choice=False)

Creates a table of notes and rests in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `combine_unisons_choice` (bool): Choice for combining unisons
- `combine_rests_choice` (bool): Choice for combining rests

Returns:
- `pd.DataFrame`: DataFrame containing processed notes

### corpus_note_scaled(corpus, combine_unisons_choice=True, combine_rests_choice=False)

Counts occurrences of notes and rests in a corpus, including scaled counts.

Parameters:
- `corpus` (object): Corpus object
- `combine_unisons_choice` (bool): Choice for combining unisons
- `combine_rests_choice` (bool): Choice for combining rests

Returns:
- `pd.DataFrame`: DataFrame containing note counts

### corpus_note_durs(corpus, pitch_class=True)

Calculates durations of notes in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `pitch_class` (bool): Whether to use pitch class instead of full note names (default: True)

Returns:
- `pd.DataFrame`: DataFrame containing note durations

### corpus_mel(corpus, kind_choice='d', compound_choice=True, directed_choice=True)

Generate melodic intervals in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `kind_choice` (str): Kind of intervals to generate
- `compound_choice` (bool): Whether to allow compound intervals
- `directed_choice` (bool): Whether to allow directed intervals

Returns:
- `pd.DataFrame`: DataFrame containing generated melodic intervals

### corpus_har(corpus, kind_choice='d', compound_choice=True, directed_choice=True)

Generate harmonic intervals in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `kind_choice` (str): Kind of intervals to generate
- `compound_choice` (bool): Whether to allow compound intervals
- `directed_choice` (bool): Whether to allow directed intervals

Returns:
- `pd.DataFrame`: DataFrame containing generated harmonic intervals

### corpus_contrapuntal_ngrams(corpus, ngram_length)

Generate n-grams in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `ngram_length` (int): Length of n-grams to generate

Returns:
- `pd.DataFrame`: DataFrame containing generated n-grams

### corpus_melodic_ngrams(corpus, ngram_length=4, kind_choice='d', end_choice=False, metadata_choice=True, include_offset=False)

Generate n-grams in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `kind_choice` (str): 'd' for diatonic (default)
- `end_choice` (bool): False to give position as of the first note of the interval
- `metadata_choice` (bool): Whether to include composer, title, and data
- `include_offset` (bool): Whether to include offset along with measure and beat

Returns:
- `pd.DataFrame`: DataFrame containing generated n-grams

### corpus_melodic_durational_ratios_ngrams(corpus, ngram_length=4, end_choice=False, kind_choice='d', metadata_choice=True, include_offset=False)

Generate n-grams in a corpus with durational ratios.

Parameters:
- `corpus` (object): Corpus object
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `end_choice` (bool): False to give position as of the first note of the interval
- `kind_choice` (str): 'd' for diatonic (default)
- `metadata_choice` (bool): Whether to include composer, title, and data
- `include_offset` (bool): Whether to include offset along with measure and beat

Returns:
- `pd.DataFrame`: DataFrame containing generated n-grams

### corpus_harmonic_ngrams(corpus, ngram_length=4, kind_choice='d', metadata_choice=True, include_offset=False)

Generate n-grams in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `kind_choice` (str): 'd' for diatonic (default)
- `metadata_choice` (bool): Whether to include composer, title, and data
- `include_offset` (bool): Whether to include offset along with measure and beat

Returns:
- `pd.DataFrame`: DataFrame containing generated n-grams

### corpus_sonority_ngrams(corpus, ngram_length=4, metadata_choice=True, include_offset=False, include_progress=True, compound=True, sort=False, minimum_beat_strength=0.0)

Generate sonority n-grams in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `ngram_length` (int): Length of n-grams to generate (default: 4)
- `metadata_choice` (bool): Whether to include composer, title, and data
- `include_offset` (bool): Whether to include offset along with measure and beat
- `include_progress` (bool): Whether to include progress column
- `compound` (bool): Whether to allow compound intervals
- `sort` (bool): If true, sorts intervals from largest to smallest; no unison
- `minimum_beat_strength` (float): Minimum value for beat strength to report

Returns:
- `pd.DataFrame`: DataFrame containing generated n-grams

### corpus_cadences(corpus)

Generate cadences in a corpus.

Parameters:
- `corpus` (object): Corpus object

Returns:
- `pd.DataFrame`: DataFrame containing cadence information

### corpus_presentation_types(corpus, limit_to_entries=True, head_flex=1, body_flex=0, include_hidden_types=False, combine_unisons=True, melodic_ngram_length=4, kind='d', end=False)

Generate presentation types in a corpus.

Parameters:
- `corpus` (object): Corpus object
- `limit_to_entries` (bool): Whether to limit entries
- `head_flex` (int): Flexibility for head
- `body_flex` (int): Flexibility for body
- `include_hidden_types` (bool): Whether to include hidden types
- `combine_unisons` (bool): Whether to combine unisons
- `melodic_ngram_length` (int): Length of melodic n-grams
- `kind` (str): Kind of intervals
- `end` (bool): Whether to give position as of the first note of the interval

Returns:
- `pd.DataFrame`: DataFrame containing presentation types