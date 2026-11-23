# CRIM Intervals: A Concise Guide

**CRIM Intervals** is a Python library for finding melodic, harmonic and contrapuntal patterns in encoded scores, with an emphasis on Renaissance polyphony. It is built on [music21](https://web.mit.edu/music21/) and [pandas](https://pandas.pydata.org/), and was developed for [Citations: The Renaissance Imitation Mass (CRIM)](https://crimproject.org).

- **Results are tables.** Most methods return a pandas DataFrame with one column per voice. You can filter it, chain it into another method, export it, chart it, or show it as score excerpts.
- **Options are documented in each method.** For example, `print(piece.melodic.__doc__)`. The **Tutorial** column in each table below gives the number of the tutorial that explains that method in detail, with examples (for example, 08 is `08_Ngrams_Heat_Maps`).
- **No code needed?** The [CRIM Intervals web app](https://intervals-streamlit.crimproject.org/) runs the main analyses in a browser.

```python
# pip install crim_intervals
from crim_intervals import *
import crim_intervals.visualizations as viz

piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')
mel = piece.melodic(kind='d', compound=False)        # melodic intervals, one column per voice
piece.ngrams(df=mel, n=4)                            # chain: 4-interval melodic n-grams
```

## 1. Loading Pieces and Working with a Corpus

| Capability | How | Tutorial |
|---|---|---|
| Import a piece: MEI, MusicXML or MIDI, from a URL or a local file | `importScore(path)` | 01 |
| Import every score in a folder | `importScore(folder, recurse=True)` | 01 |
| Composer, title and other metadata | `piece.metadata` | 01 |
| Build a corpus from a list of pieces | `CorpusBase([url1, url2, ...])` | 01 |
| Run any method on every piece in a corpus | `corpus.batch(ImportedPiece.melodic, kwargs={...})` | 01 |
| Run standard analyses on a whole corpus, giving one combined table | `corpus.notes()`, `.mel()`, `.har()`, `.melodic_ngrams()`, `.contrapuntal_ngrams()`, `.sonority_ngrams()`, `.cadences()`, `.presentation_types()`, `.voice_ranges()`, `.melodic_species()` | 19 |
| See which settings produced a result | `get_settings(df)` | 01 |
| Export results | `df.to_csv(...)`, `df.to_excel(...)` | 01 |

## 2. Notes, Rhythm, Meter and Text

| Capability | How | Tutorial |
|---|---|---|
| Notes and rests in each voice, with options to combine repeated notes or rests | `piece.notes(combineUnisons=, combineRests=)` | 02 |
| Durations (quarter note = 1.0), including the length of each n-gram | `piece.durations(df=, n=, mask_df=)` | 03 |
| Durational ratios between successive notes | `piece.durationalRatios()` | 03 |
| Time signatures, measure numbers, barlines, beat strengths | `timeSignatures()`, `measures()`, `barlines()`, `beatStrengths()` | 04 |
| Measure and beat labels (and more) for any result | `piece.detailIndex(df, ...)` | 05 |
| Lyrics for every note, cleaned of punctuation if wanted | `piece.lyrics()` | 10 |
| Time spent on each pitch class; the range of each voice | `piece.note_weights()`, `piece.voice_ranges()` | 13 |

## 3. Intervals and Sonorities

| Capability | How | Tutorial |
|---|---|---|
| Melodic intervals: diatonic or chromatic, with or without quality, directed or not, simple or compound, sampled at a regular time unit | `piece.melodic(kind=, directed=, compound=, unit=, end=)` | 06 |
| Harmonic intervals between every pair of voices, or against the lowest voice | `piece.harmonic(kind=, directed=, compound=, againstLow=)` | 07 |
| Sonorities (all the pitches sounding together) | `piece.sonorities()` | 07 |
| Melodic interval "families": related melodies as a branching graph | `piece.graphIntervalFamilies()`, `corpus.compareIntervalFamilies()` | 14 |

## 4. N-grams and Higher-Level Patterns

| Capability | How | Tutorial |
|---|---|---|
| N-grams of any feature (melodic or harmonic intervals, durations, lyrics) or a combination | `piece.ngrams(df=, n=, other=, offsets=)` | 08 |
| Contrapuntal modules: vertical intervals combined with the lower voice's motion, the default kind of n-gram | `piece.ngrams()` | 09 |
| Entries: n-grams that start a voice after a rest or fermata, optionally only the recurring ("thematic") ones | `piece.entries(n=, thematic=, anywhere=)` | 08 |
| Sonority n-grams with the bass line | `piece.sonority_ngrams()` | 07 |
| Cadences, with type, tone and voice functions | `piece.cadences()` | 11 |
| Presentation types (fuga, periodic entry, imitative and non-imitative duos), with flexible melodic matching | `piece.presentationTypes(head_flex=, body_flex=, ...)` | 12 |
| Homorhythmic passages | `piece.homorhythm()` | 10 |
| Melodic species: octave species articulated by melodic leaps | `piece.melodic_species()` | 13 |
| Model and Mass comparison: how much melodic or modular material each Mass movement shares with possible models | `corpus.modelFinder()`, `corpus.moduleFinder()` | 16 |

## 5. Visualizations

Charts from the ready-made functions show their **settings** beneath the title, and a piece, pattern or cadence type keeps the same color in every chart.

| Chart | How | Tutorial |
|---|---|---|
| Bar charts and histograms of notes and intervals | Plotly, with the results of `notes()`, `melodic()` and `harmonic()` | 02, 06, 07 |
| N-gram heat map: where each pattern occurs in each voice. Real entries can be marked, with a greyscale option for print | `viz.plot_ngrams_heatmap(ngrams, durations, entry_mask=, entries=)` | 08, 17 |
| Paired heat maps of the patterns a model shares with each Mass movement | `viz.plot_paired_ngram_heatmaps(...)` | 08 |
| Cadence radar, progress and bar charts | `viz.cadence_radar()`, `viz.cadence_progress()`, `viz.cadence_bar_chart()` | 11, 17 |
| Pitch-class radar plot | `viz.radar_note_plot(piece.note_weights())` | 17 |
| Voice range chart, for comparing modal types | `viz.voice_range_chart(piece.voice_ranges())` | 13 |
| Melodic species, alone or alongside cadences | `viz.plot_species()`, `viz.plot_species_cadences()` | 13 |
| Sonority n-gram progress plot | `viz.sonority_ngram_progress()` | 07, 17 |
| Model-finder similarity heat maps | with the results of `modelFinder()` and `moduleFinder()` | 16 |
| Network graphs of cadences, presentation types and n-grams across a corpus | NetworkX and Pyvis, from CRIM results | 18 |

Each ready-made chart function works with the result of either a single piece or a whole corpus.

## 6. Score Excerpts

| Capability | How | Tutorial |
|---|---|---|
| Show any passage in modern notation (Verovio) | `piece.verovioPrintExample(...)` | 15 |
| Show every cadence, presentation type or homorhythmic passage found | `verovioCadences()`, `verovioPtypes()`, `verovioHomorhythm()` | 15 |
| Turn a results table into clickable links to highlighted examples | `piece.linkExamples(df)` | 15 |

## Tutorials

The tutorials are in the [tutorial folder](https://github.com/HCDigitalScholarship/intervals/tree/main/tutorial). Topics are 01–19, as numbered in the tables above. Background tutorials: **20** Python basics, **21** pandas basics, **22** music21 and MEI, **99** local installation.
