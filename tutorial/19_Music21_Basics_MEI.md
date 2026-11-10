# Music21 Basics

## Table of Contents
1. [Build Metadata and Show Parts and Notes](#build-metadata-and-show-parts-and-notes)
2. [List of Voice Parts](#list-of-voice-parts)
3. [Measures](#measures)
4. ["Notes" are Pitch Classes](#notes-are-pitch-classes)
5. [Now the Specific Notes as Pitch Class plus Octave Number](#now-the-specific-notes-as-pitch-class-plus-octave-number)
6. [Which Notes in the First Measure?](#which-notes-in-the-first-measure)
7. [Durations](#durations)
8. [Rests are not the Same as Notes!](#rests-are-not-the-same-as-notes)
9. [Key Attributes of a Music21 Note Object](#key-attributes-of-a-music21-note-object)
10. [Melodic Interval Attributes](#melodic-interval-attributes)
11. [Harmonic Intervals](#harmonic-intervals)
12. [Lyrics](#lyrics)
13. [Sections in this guide](#sections-in-this-guide)

Mike Cuthbert's Music21 library is a key resource for digital musicology.  It takes care of all the difficult work of finding notes, intervals and other important data about musical patterns.

In this notebook we work with **MEI** files, starting with Bach's Invention No. 1 in C major (BWV 772) loaded directly from the [Duos repository on GitHub](https://github.com/RichardFreedman/Duos/tree/main/MEI).

- Get score
- Show the score with Verovio
- Check metadata
- Find all voices, all notes
- Find particular notes (all of pitch class X, etc)

# Load Music 21
- Load libraries and namespaces

```python
from music21 import *
import music21 as m21
import xml.etree.ElementTree as ET
import requests
# import a counter
from collections import Counter
from itertools import combinations
import pandas as pd

ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
```

# Load an MEI File from GitHub

We fetch the raw MEI text with `requests`. Note that the URL points to `raw.githubusercontent.com`, not the regular GitHub page, so that we get the MEI file itself rather than the web page that displays it.

```python
path = 'https://raw.githubusercontent.com/RichardFreedman/Duos/main/MEI/Bach_BWV_0772.mei'
mei_text = requests.get(path).text
path
```

```
'https://raw.githubusercontent.com/RichardFreedman/Duos/main/MEI/Bach_BWV_0772.mei'
```

# Show the Score with Verovio

[Verovio](https://www.verovio.org) is an engraving library that reads MEI directly and renders it as SVG, so we can see the score right in the notebook.

```python
import verovio
from IPython.display import SVG, display

tk = verovio.toolkit()
tk.setOptions({"pageWidth": 2100, "scale": 35, "adjustPageHeight": True})
tk.loadData(mei_text)

# render each page of the score as SVG
for page in range(1, tk.getPageCount() + 1):
    display(SVG(tk.renderToSVG(page)))
```

![Bach, Invention No. 1 (BWV 772), rendered with Verovio](images/music21_basics_bwv772_p1.svg)

## Build Metadata and Show Parts and Notes

Music21 does not always read the metdata correctly, so we will find that information via the root of the XML tree, then add it to the Music21 `score` object.

```python
# deal with metadata directly from MEI file
root = ET.fromstring(mei_text)

ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
title = root.findtext('.//mei:titleStmt/mei:title', namespaces=ns)
composer = root.find('.//mei:respStmt/mei:persName[@role="composer"]', namespaces=ns)

score = m21.converter.parse(mei_text)
# assign the metadata to the score object
score.metadata.title = title.strip() if title else "Unknown Title"
score.metadata.composer = composer.text.strip() if composer is not None else "Unknown Composer"

# print details
print(score.metadata.composer)
print(score.metadata.title)
```

```
Bach, Johann Sebastian
Invention No. 1 in C major,  BWV 772
```

## List of Voice Parts

To list all the parts, we use `score.getElementsByClass(m21.stream.Part)`:

```python
voice_parts = score.getElementsByClass(m21.stream.Part)
# now iterate over them and get the name of each one
for part in voice_parts:
  print(part.partName)
```

```
Piano
Piano
```

## Measures

- How many measures are in the score?

```python
num_measures = len(score.parts[0].getElementsByClass(m21.stream.Measure))
print(f"Measures: {num_measures}")
```

```
Measures: 22
```

All parts should have the same count in a well-formed score, so checking `parts[0]` is sufficient. If you want to verify they match across parts:

```python
for part in score.parts:
    count = len(part.getElementsByClass(m21.stream.Measure))
    print(f"{part.partName or part.id}: {count} measures")
```

```
Piano: 22 measures
Piano: 22 measures
```

Just the first part, first 2 measures

```python
score.parts[0].measures(1, 2).show('text')
```

```
{0.0} <music21.instrument.Piano '1: Piano'>
{0.0} <music21.stream.Measure 1 offset=0.0>
    {0.0} <music21.clef.TrebleClef>
    {0.0} <music21.stream.Voice 1>
        {0.0} <music21.note.Rest 16th>
        {0.25} <music21.note.Note C>
        {0.5} <music21.note.Note D>
        {0.75} <music21.note.Note E>
        {1.0} <music21.note.Note F>
        {1.25} <music21.note.Note D>
        {1.5} <music21.note.Note E>
        {1.75} <music21.note.Note C>
        {2.0} <music21.note.Note G>
        {2.5} <music21.note.Note C>
        {3.0} <music21.note.Note B>
        {3.5} <music21.note.Note C>
{4.0} <music21.stream.Measure 2 offset=4.0>
    {0.0} <music21.stream.Voice 1>
        {0.0} <music21.note.Note D>
        {0.25} <music21.note.Note G>
        {0.5} <music21.note.Note A>
        {0.75} <music21.note.Note B>
        {1.0} <music21.note.Note C>
        {1.25} <music21.note.Note A>
        {1.5} <music21.note.Note B>
        {1.75} <music21.note.Note G>
        {2.0} <music21.note.Note D>
        {2.5} <music21.note.Note G>
        {3.0} <music21.note.Note F>
        {3.5} <music21.note.Note G>
```

# Notes from One Voice Part
- Define the variable `parts` and then showing where to obtain these with m21
- Define the variable for your staff by index number (`[0]` is the top voice, `[2]` is the third from the top, etc.

```python
# all the staves:
voice_parts = score.getElementsByClass(m21.stream.Part)

# specify the part; the top part is index 0, the second from the top is index 1, etc
selected_part = voice_parts[0]
# now the notes from that selected part
notes_selected_part = selected_part.flatten().getElementsByClass(['Note'])
# and now we can iterate over those notes and print them--in this case just the first 10 notes to save space
for note in notes_selected_part[:10]:
  print(note)
```

```
<music21.note.Note C>
<music21.note.Note D>
<music21.note.Note E>
<music21.note.Note F>
<music21.note.Note D>
<music21.note.Note E>
<music21.note.Note C>
<music21.note.Note G>
<music21.note.Note C>
<music21.note.Note B>
```

## "Notes" are Pitch Classes
- looking for all the notes in a given part
- `[X]` is index of the given part
- must include "flatten()" to get all the notes, not just the ones in the first measure
- iterate over those notes and print them

```python
# all the staves:
voice_parts = score.getElementsByClass(m21.stream.Part)

# specify the part; the top part is index 0, the second from the top is index 1, etc
selected_part = voice_parts[0]
notes_selected_part = selected_part.flatten().getElementsByClass(['Note'])
# create a list where we can store the list of notes
selected_notes_list = []

# now we iterate of the note objects and return the `name` attribute of each note, which is JUST the pitch class (no octave number)
for each_note in notes_selected_part:
    # here we get the `name` attribute of the note, which is JUST the pitch class
    selected_notes_list.append(each_note.name)

print(selected_notes_list)
```

```
['C', 'D', 'E', 'F', 'D', 'E', 'C', 'G', 'C', 'B', 'C', 'D', 'G', 'A', 'B', 'C', 'A', 'B', 'G', 'D', 'G', 'F', 'G', 'E', 'A', 'G', 'F', 'E', 'G', 'F', 'A', 'G', 'F', 'E', 'D', 'C', 'E', 'D', 'F', 'E', 'D', 'C', 'B', 'A', 'C', 'B', 'D', 'C', 'B', 'A', 'G', 'F#', 'A', 'G', 'B', 'A', 'D', 'C', 'D', 'B', 'A', 'G', 'F#', 'E', 'G', 'F#', 'A', 'G', 'B', 'A', 'C', 'B', 'D', 'C', 'E', 'D', 'B', 'C', 'D', 'G', 'B', 'A', 'G', 'G', 'G', 'A', 'B', 'C', 'A', 'B', 'G', 'F#', 'A', 'B', 'C', 'D', 'B', 'C', 'A', 'B', 'D', 'C', 'B', 'A', 'C', 'B', 'D', 'C', 'E', 'D', 'C', 'B', 'D', 'C#', 'E', 'D', 'C#', 'D', 'E', 'F', 'A', 'B', 'C#', 'D', 'F#', 'G#', 'A', 'B', 'C', 'D', 'D', 'E', 'F#', 'G#', 'A', 'F#', 'G#', 'E', 'E', 'D', 'C', 'E', 'D', 'C', 'B', 'D', 'C', 'A', 'G#', 'B', 'A', 'E', 'F', 'D', 'G#', 'F', 'E', 'D', 'C', 'B', 'A', 'A', 'A', 'G', 'F', 'E', 'G', 'F', 'A', 'G', 'G', 'E', 'F', 'G', 'A', 'F', 'G', 'E', 'F', 'F', 'G', 'F', 'E', 'D', 'F', 'E', 'G', 'F', 'F', 'D', 'E', 'F', 'G', 'E', 'F', 'D', 'E', 'E', 'C', 'D', 'E', 'F', 'D', 'E', 'C', 'D', 'E', 'F', 'G', 'A', 'F', 'G', 'E', 'F', 'G', 'A', 'B', 'C', 'A', 'B', 'G', 'C', 'G', 'E', 'D', 'C', 'C', 'B-', 'A', 'G', 'F', 'A', 'G', 'B-', 'A', 'B', 'C', 'E', 'D', 'C', 'F', 'B']
```

## Now the Specific Notes as Pitch Class plus Octave Number
- specify the part; the top part is index 0, the second from the top is index 1, etc
- now the notes from that selected part
- and now we can iterate over those notes and print them

```python
# all the staves:
voice_parts = score.getElementsByClass(m21.stream.Part)

# specify the part; the top part is index 0, the second from the top is index 1, etc
selected_part = voice_parts[0]
selected_part = voice_parts[0]
# the notes in that part
notes_selected_part = selected_part.flatten().getElementsByClass(['Note'])
# create a list where we can store the list of notes
selected_notes_list = []
for each_note in notes_selected_part:
    # here we get the `nameWithOctave` attribute of the note, which is the pitch class plus the octave number
    selected_notes_list.append(each_note.nameWithOctave)

print(selected_notes_list)
```

```
['C4', 'D4', 'E4', 'F4', 'D4', 'E4', 'C4', 'G4', 'C5', 'B4', 'C5', 'D5', 'G4', 'A4', 'B4', 'C5', 'A4', 'B4', 'G4', 'D5', 'G5', 'F5', 'G5', 'E5', 'A5', 'G5', 'F5', 'E5', 'G5', 'F5', 'A5', 'G5', 'F5', 'E5', 'D5', 'C5', 'E5', 'D5', 'F5', 'E5', 'D5', 'C5', 'B4', 'A4', 'C5', 'B4', 'D5', 'C5', 'B4', 'A4', 'G4', 'F#4', 'A4', 'G4', 'B4', 'A4', 'D4', 'C5', 'D5', 'B4', 'A4', 'G4', 'F#4', 'E4', 'G4', 'F#4', 'A4', 'G4', 'B4', 'A4', 'C5', 'B4', 'D5', 'C5', 'E5', 'D5', 'B4', 'C5', 'D5', 'G5', 'B4', 'A4', 'G4', 'G4', 'G4', 'A4', 'B4', 'C5', 'A4', 'B4', 'G4', 'F#4', 'A4', 'B4', 'C5', 'D5', 'B4', 'C5', 'A4', 'B4', 'D5', 'C5', 'B4', 'A4', 'C5', 'B4', 'D5', 'C5', 'E5', 'D5', 'C5', 'B4', 'D5', 'C#5', 'E5', 'D5', 'C#5', 'D5', 'E5', 'F5', 'A4', 'B4', 'C#5', 'D5', 'F#4', 'G#4', 'A4', 'B4', 'C5', 'D5', 'D5', 'E4', 'F#4', 'G#4', 'A4', 'F#4', 'G#4', 'E4', 'E5', 'D5', 'C5', 'E5', 'D5', 'C5', 'B4', 'D5', 'C5', 'A5', 'G#5', 'B5', 'A5', 'E5', 'F5', 'D5', 'G#4', 'F5', 'E5', 'D5', 'C5', 'B4', 'A4', 'A4', 'A5', 'G5', 'F5', 'E5', 'G5', 'F5', 'A5', 'G5', 'G5', 'E5', 'F5', 'G5', 'A5', 'F5', 'G5', 'E5', 'F5', 'F5', 'G5', 'F5', 'E5', 'D5', 'F5', 'E5', 'G5', 'F5', 'F5', 'D5', 'E5', 'F5', 'G5', 'E5', 'F5', 'D5', 'E5', 'E5', 'C5', 'D5', 'E5', 'F5', 'D5', 'E5', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'F5', 'G5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6', 'A5', 'B5', 'G5', 'C6', 'G5', 'E5', 'D5', 'C5', 'C5', 'B-4', 'A4', 'G4', 'F4', 'A4', 'G4', 'B-4', 'A4', 'B4', 'C5', 'E4', 'D4', 'C5', 'F4', 'B4']
```

## Which Notes in the First Measure?

```python
# specify measure range; this is the first measure only; change to (1, 2) for the first two measures, etc.
measure_range = (1, 1) 
# now get all the notes in one line fof code; we specify the part, then the measure range, then we get all the notes in that measure range
notes_in_given_measure_range = score.parts[0].measures(measure_range[0], measure_range[1]).flatten().getElementsByClass(['Note'])

# empty list to store the notes in the measure range
notes_in_measure = []
for each_note in notes_in_given_measure_range:
    # here we get the `nameWithOctave` attribute of the note, which is the pitch class plus the octave number
    notes_in_measure.append(each_note.nameWithOctave)

print(notes_in_measure)
```

```
['C4', 'D4', 'E4', 'F4', 'D4', 'E4', 'C4', 'G4', 'C5', 'B4', 'C5']
```

## Durations

Durations are recorded in terms of quarter notes, so a whole note is `4.0`, a half note is `2.0`, a quarter note is `1.0`, an eighth note is `0.5`, etc.

```python
# here we get all the notes (as before)

notes_in_part = score.parts[0].flatten().getElementsByClass(m21.note.Note)

# iterate over the notes and print their name with octave and their duration in quarter notes--also just the first ten to save space
for note in notes_in_part[:10]:
    duration = note.quarterLength
    print(f"{note.nameWithOctave}: {duration}")
```

```
C4: 0.25
D4: 0.25
E4: 0.25
F4: 0.25
D4: 0.25
E4: 0.25
C4: 0.25
G4: 0.5
C5: 0.5
B4: 0.5
```

```python
# test for note durations with specific duration (half notes)

notes_in_part = score.parts[0].flatten().getElementsByClass(m21.note.Note)

half_note_names = [n.name for n in notes_in_part if n.quarterLength == 2.0]
print(half_note_names)
```

```
['G', 'F', 'F', 'E']
```

```python
# finding the measure numbers in which those half notes occur
notes_in_part = score.parts[0].flatten().getElementsByClass(m21.note.Note)

for n in notes_in_part:
    if n.quarterLength == 2.0:
        print(f"m.{n.measureNumber}  {n.nameWithOctave}")
```

```
m.15  G5
m.16  F5
m.17  F5
m.18  E5
```

## Rests are not the Same as Notes!

- `note` objects are from the class `m21.note.Note`
- `rest` objects are from the class `m21.note.Rest` 


If you just ask for "all the notes", you will get only the note objects, and not the rest objects. So if you want to find all the notes, you need to specify that class!

```python
# get all the rests in the entire score
rests_in_part = score.flatten().getElementsByClass(m21.note.Rest)
# create a list to store the durations of the rests
rest_list = []
# iterate over the rests and get their durations in quarter notes
for rest in rests_in_part:
    rest_list.append(rest.duration.quarterLength)

print(rest_list)
print(len(rest_list))
#print(rest_list[0])
```

```
[0.25, 2.0, 0.25, 1.0, 0.25, 0.25, 0.5, 1.0, 0.25, 0.5, 1.0, 0.25, 0.5, 1.0, 0.25, 0.5, 1.0, 0.25, 1.0, 0.25, 4.0]
21
```

## Key Attributes of a Music21 Note Object

### Discover All Attributes

Run this to see all the attributes of the note object. The attributes are grouped into categories below, but this will show you everything that is available to you for a note object.
```python
n = score.parts[0].flatten().getElementsByClass(m21.note.Note)[0]
print([attr for attr in dir(n) if not attr.startswith('_')])
```

### Pitch
| Attribute | Description | Example |
|---|---|---|
| `n.name` | Pitch name without octave | `"C"`, `"D#"` |
| `n.nameWithOctave` | Pitch name with octave | `"C4"` |
| `n.pitch` | Full Pitch object | `<music21.pitch.Pitch C4>` |
| `n.octave` | Octave number | `4` |
| `n.midi` | MIDI pitch number | `60` |
| `n.ps` | Pitch space as float | `60.0` |
| `n.step` | Diatonic letter only | `"C"`, `"D"` |
| `n.accidental` | Accidental object or None | `<music21.pitch.Accidental sharp>` |

### Duration
| Attribute | Description | Example |
|---|---|---|
| `n.quarterLength` | Duration in quarter notes | `2.0` (half note) |
| `n.duration.type` | Duration name | `"whole"`, `"half"`, `"quarter"` |
| `n.duration.dots` | Augmentation dots | `1` (dotted), `0` (plain) |

### Position
| Attribute | Description | Example |
|---|---|---|
| `n.offset` | Beat offset from container start | `4.0` |
| `n.measureNumber` | Measure number | `3` |
| `n.beat` | Beat within the measure | `1.0` |
| `n.beatStrength` | Metric weight | `1.0` (downbeat), `0.25` (weak) |

### Articulation & Expression
| Attribute | Description |
|---|---|
| `n.articulations` | List of Articulation objects (staccato, accent, etc.) |
| `n.expressions` | List of Expression objects (trill, fermata, etc.) |
| `n.tie` | Tie object or None |
| `n.lyric` / `n.lyrics` | Text underlay (single string or list) |

### Miscellaneous
| Attribute | Description |
|---|---|
| `n.stemDirection` | `"up"`, `"down"`, `"noStem"` |
| `n.notehead` | Notehead shape string |
| `n.id` | Unique element ID |

# Pitch (Note in a particular Octave)
- here we look for notes in specific octaves, like `4`.

```python
notes_in_octave = [n for n in score.parts[0].flatten().getElementsByClass(m21.note.Note)
                   if n.octave == 4]

# just the first ten notes in octave 4 to save space
for n in notes_in_octave[:10]:
    print(f"m.{n.measureNumber}  {n.nameWithOctave}")
```

```
m.1  C4
m.1  D4
m.1  E4
m.1  F4
m.1  D4
m.1  E4
m.1  C4
m.1  G4
m.1  B4
m.2  G4
```

```python
# count the notes in a given octave

# specify the octave we want to look at
selected_octave = 4
# get the notes that match the condition, using list comprehension
selected_octave_tones = [n.name for n in score.parts[0].flatten().getElementsByClass(m21.note.Note) if n.octave == selected_octave]

# pass these to the counter function
octave_counts = Counter(selected_octave_tones)

octave_counts_df = pd.DataFrame.from_dict(octave_counts, orient='index', columns=['Count'])
octave_counts_df.index.name = 'Pitch Class'
octave_counts_df.reset_index(inplace=True)
octave_counts_df
```

| Pitch Class | Count |
|---|---|
| C | 2 |
| D | 4 |
| E | 6 |
| F | 3 |
| G | 14 |
| B | 26 |
| A | 23 |
| F# | 7 |
| G# | 4 |
| B- | 2 |

# Intervals
-`pitch` is the module (a collection of methods and classes); `Pitch` is the class (data structure)
- `interval` is part of the `pitch` module (it's a submodule), and has the method `notesToInterval`.  
- Here `Interval` is another class (data structure), and `interval` is another module


## Melodic Interval Attributes

| Attribute | Example | Description |
|---|---|---|
| `directedName` | `"-M2"` | Direction + quality + size |
| `name` | `"M2"` | Quality + size, no direction |
| `semitones` | `-2` | Raw half-steps (signed) |
| `generic.directed` | `-2` | Diatonic steps (signed) |

### Directed Name Format
`[direction][quality][size]`

| Part | Values | Example |
|---|---|---|
| Direction | `-` (down), none (up) | `-` |
| Quality | `P` perfect, `M` major, `m` minor, `A` augmented, `d` diminished | `M` |
| Size | Diatonic interval number | `2` |

So `-M2` = descending major second, `P5` = ascending perfect fifth.

```python
# the notes

a = m21.pitch.Pitch('C4')
b = m21.pitch.Pitch('G4')

# the interval between those two notes in as interval + quality
ivl = interval.Interval(a, b)
print(ivl.semitones)      # 7
print(ivl.directedName)   # P5
```

```
7
P5
```

```python
# count all the intervals between adjacent notes in all parts

parts = score.getElementsByClass(m21.stream.Part)

# empty list to store the intervals
list_intervals = []

# iterate over the parts, get the notes in each part, and then get the intervals between adjacent notes
for part in parts:
    notes = list(part.flatten().getElementsByClass(m21.note.Note))

    intervals = [interval.Interval(notes[i], notes[i+1]).directedName
                for i in range(len(notes) - 1)]
    # add the intervals from this part to the overall list of intervals
    list_intervals.extend(intervals)
# count them
melodic_intervals_df = pd.DataFrame.from_dict(Counter(list_intervals), orient='index', columns=['Count'])
melodic_intervals_df.index.name = 'Interval'
melodic_intervals_df.reset_index(inplace=True)
melodic_intervals_df
```

| Interval | Count |
|---|---|
| M2 | 90 |
| m2 | 47 |
| m-3 | 34 |
| M-3 | 16 |
| P5 | 6 |
| P4 | 13 |
| m-2 | 53 |
| P-5 | 8 |
| M-2 | 94 |
| m3 | 40 |
| M3 | 13 |
| m7 | 3 |
| m-6 | 6 |
| P1 | 13 |
| m-7 | 2 |
| P8 | 4 |
| M6 | 2 |
| P-4 | 5 |
| d-5 | 1 |
| d7 | 1 |
| A4 | 1 |
| P-8 | 5 |
| M-6 | 1 |
| P12 | 1 |
| m6 | 1 |
| M-9 | 1 |

## Harmonic Intervals

For harmonic intervals between two simultaneous voices, chordify() is the standard approach — it collapses all parts into chords at each offset:

```python
chords = score.chordify()

harmonic_intervals = []
for chord in chords.flatten().getElementsByClass(m21.chord.Chord):
    # compare adjacent pitches within each chord (bottom to top)
    pitches = chord.pitches  # sorted low to high
    for i in range(len(pitches) - 1):
        ivl = interval.Interval(pitches[i], pitches[i+1]).directedName
        harmonic_intervals.append(ivl)

counts = Counter(harmonic_intervals)
harmonic_intervals_df = pd.DataFrame.from_dict(counts, orient='index', columns=['Count'])
harmonic_intervals_df.index.name = 'Interval'
harmonic_intervals_df.reset_index(inplace=True)
harmonic_intervals_df
```

| Interval | Count |
|---|---|
| P12 | 25 |
| m14 | 5 |
| m13 | 23 |
| A11 | 6 |
| M13 | 20 |
| P15 | 8 |
| P8 | 7 |
| M16 | 2 |
| M17 | 2 |
| P11 | 27 |
| M10 | 21 |
| d12 | 18 |
| m10 | 32 |
| m9 | 3 |
| M9 | 11 |
| m7 | 6 |
| m6 | 6 |
| A4 | 8 |
| M6 | 19 |
| P5 | 8 |
| M7 | 4 |
| m17 | 3 |
| m16 | 1 |
| P19 | 2 |
| P18 | 1 |
| M3 | 9 |
| m3 | 1 |
| P4 | 4 |
| m21 | 2 |
| m20 | 1 |
| M14 | 1 |

##  Lyrics

Let's get a score with lyrics:

```python
path = "https://raw.githubusercontent.com/RichardFreedman/Duos/main/MEI/Morley_1595_01_Go_ye_my_canzonettes.mei"
mei_text = requests.get(path).text
# deal with metadata directly from MEI file
root = ET.fromstring(mei_text)

ns = {'mei': 'http://www.music-encoding.org/ns/mei'}
title = root.findtext('.//mei:titleStmt/mei:title', namespaces=ns)
composer = root.find('.//mei:respStmt/mei:persName[@role="composer"]', namespaces=ns)

score = m21.converter.parse(mei_text)
# assign the metadata to the score object
score.metadata.title = title.strip() if title else "Unknown Title"
score.metadata.composer = composer.text.strip() if composer is not None else "Unknown Composer"

# print details
print(score.metadata.composer)
print(score.metadata.title)

for part in score.parts:
    print(f"\n--- {part.partName or part.id} ---")
    lyrics = [n.lyric.replace("\n", "").replace("-", "").strip()
              for n in part.flatten().getElementsByClass(m21.note.Note)
              if n.lyric and n.lyric.strip()]
    print(" ".join(lyrics))
```

```
Thomas Morley
Go ye my canzonettes

--- Soprano 1 ---
Goe yee my Can zo nets to my deer dar ling, goe yee my Can zo nets to my deer dar ling, goe yee my Can zo nets to my deer dar ling, to my deer dar ling, and with your gen tlr dain tie sweet ac cen tings, de sire hir to vouch safe these my la men tings, de sire hir to vouch safe these my la men tings, and with a crow net, of hir rayes su per nall, t'a dorne your locks and make your name e ter nal, t'a dorne your locks and make yout name e ter nall, and with a crow net of hir rayes su per nall, t'a dorne your locks and make your name e ter nal, t'a dorne yout locks and make your name e ter nall.

--- Soprano 2 ---
Goe yee my Can zo nets to my deer dar ling, deer dar ling, goe yee my Can zo nets to my deer dar ling, to my deer dar ling, and with your gen tle dain tie sweet ac cen tings, de sire hir to vouch safe these my la men tings, de sire hir to vouch safe these my la men tings, and with a crow net, of hir rayes sper nall, t'a dorne your locks and make your name e ter nall t'a dorne your looks and make your name e ter nall, and with a crow net, of hir rayes su per nall, ta dorne your locks and make your name e tar nall, t'a dorne your locks and make your name e ter nall.
```

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
