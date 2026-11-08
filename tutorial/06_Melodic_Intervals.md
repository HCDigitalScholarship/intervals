# Finding the Melodic Intervals in Pieces  

In its simplest form, `piece.melodic()` returns a DataFrame of  intervals within each voice part in the piece. There is more to the story, however, since the `melodic()` function has a number of parameters that users can adjust to report intervallic distances in different ways.  Here is the complete list of parameters, with their default values:

```python
piece.melodic(kind='q', directed=True, compound=True, unit=0, end=True, df=None)
```


A simple default call of the function will return a DataFrame of melodic intervals for each voice in the piece, with the offsets as the index:

```python
piece.melodic()  
```

![Alt text](images/mel_1.png)
​
The parameters in detail:

* `kind`, for controlling if diatonic, chromatic, or other types of intervals are reported; default is diatonic (or simply 'd')
* `directed`, whether the report is simply a raw interval, or also reports whether it goes up or down; default is `True`  
* `compound`, whether intervals larger than an octave are reported as simpler versions; default is `True`    
* `unit`, the possibility to measure the intervals at each new onset of a note, or to sample them at some regular time interval; default uses **actual** onsets and values
* `end`, determines the offset with which interval is associated (the first or second note of the pair): default places intervals at the offset of their **second** note--that is, when the motion actually occurs
* `df`, the possibility to pass some dataframe of notes to the function in order to check the intervals of that passage or selection  
​

## The `melodic()` Parameters in Detail

### Differentiating between Diatonic, Chromatic, and other intervals with `kind`

The `melodic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive:  

**"Diatonic with Quality"**. That is: "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5). For example:  

```python
piece.melodic(kind = 'q')  
```

**Diatonic without Quality**. Provides outputs such as "8" for an octave, and "3" for a third interval.  Major and minor third (for instance) are *not* differentiated.  For example:

```python
piece.melodic(kind = "d")
```

![Alt text](images/mel_2.png)

**Chromatic**. The difference between two pitches in semitones. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5):  

```python
piece.melodic(kind = "c")
```

**Zero-based Diatonic**. To musicians it makes sense that a unison is represented as one, but this can produce some odd results in computational systems, in which calculated distances are 'zero-based':  the distance between C4 and C4 is in fact 0, not 1 (as musicians would have it). Zero-Based Diatonic intervals are thus sometimes useful.  The problem does not occur in Chromatic intervals, where the system reports the absolute distance in semitones between any two tones (C4 to C#4 is 1, not 2). Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5):  

```python
piece.melodic(kind = "z")
```

### Up and Down vs. Absolute: The `directed` Parameter  

By default, `directed = True`: "4" is an ascending fourth; "-4" is descending. It might be useful, however, simply to report the absolute distance without direction, such as if the aim is to know how many leaps of a sixth appear in a piece regardless of direction.  In this case, use `directed = False`.  


```python
#Default value:  
piece.melodic(directed = True) 
``` 

[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "-4"  

```python
piece.melodic(directed = False)
```


[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "4"  

### Managing Intervals Greater than an Octave: The `compound` Parameter  

The `melodic()` function contains a parameter `compound`, with a default value of `True`. This means that intervals with a span greater than an octave will always be returned as such.  The interval from C4 to E5 would be a diatonic 10, a chromatic 16, M10 using 'with quality', and 9 using 'zero-based diatonic'. 

```python
piece.melodic(compound = True)
```

Using `piece.melodic(compound = False)`, in contrast, analyzes all intervals as if they are *within a octave* (what musicians call the 'simple' intervallic distances). For example, with `kind='d'` and `compound=False` the interval from C4 to E5 would be a diatonic 3, a chromatic 4, M3 using 'with quality', and 2 using 'zero-based with quality'. 

*Note that with `compound = False` an octave itself is not reduced to a unison*. You could map the octave to a unison by using the `replace()` function, for instance:  

```python
piece.melodic(kind = 'd', compound = False).replace('8', '1')

### Sampling Melodies at Regular Time Intervals: The `unit` Parameter  

In most cases, the `melodic()` function will be used to trace movement at each new onset of a note. Sometimes, however, it could be useful to 'sample' the tone being sounded at some regular time interval (for instance, if the purpose was to consider time series data). This can be accomplished with the `unit` parameter. The default value of this parameter (`unit = 0`), simply means that *melodic intervals will be assigned at each new onset of a note*. Setting `unit = 1`, however, will force a 'sampled' reading of the intervallic distance at every quarter note (since '1.0 corresponds to that value in music21'):  

```python
#default value [redundant to include in code]:  
piece.melodic(unit = 0)  

#possible replacement values:  
piece.melodic(unit = 1)  
piece.melodic(unit = 4) 
``` 

![Alt text](images/mel_3.png)
​
Setting `unit` to a small value might be helpful in comparing the degree of movement in several voices.
​
Setting `unit` to larger number could be used to ignore ornamental tones (2.0, for instance, corresponds to the half-note [minim], a common basic unit of motion in Renaissance melodies).
​
Note that `beatStrength` provides another way of sampling melodic motion to highlight accented tones. For more information about beat strength, see the section of this guide dedicated to [time signatures and beat strength](08_TimeSignatures_BeatStrength.md).  

### Where Does the Interval Actually Occur? The `end` Parameter  

Normally, CRIM Intervals associates melodic intervals with the moment of change, namely the onset of the **second** note of the pair. For example, if C5 sounds on offset 1.0 and D5 sounds on offset 2.0, a melodic interval of M2 will be associated with offset 2.0. Therefore, the default value of this parameter is `end = True`, in which the interval is associated with the 'end' of the pair. In some cases, it might be useful to associate the interval with the first note of the pair instead. In this case, `end = False`.  

Assuming a C5 sounds on offset 1.0, and a D5 sounds on offset 2.0:  

Default value, which would return an interval on **beat 2**:  

```python
piece.melodic(end = True)
``` 
 

Alternate value, which would return an interval on **beat 1**:  

```python
piece.melodic(end = False)
```  

![Alt text](images/mel_4.png)

### Applying `melodic()` to a Custom Set of Notes: The `df` Parameter  

Normally `melodic()` will be used with a complete piece, as in `piece.melodic()`, along with any special parameters needed. Sometimes, however, it might be useful to provide a special set of notes to melodic. For example, to run `melodic()` on the piece with combined unisons, it will first be necessary to create a DataFrame of the piece with combined unisons, and in turn pass that DataFrame to the `melodic()` function via the `df` parameter:  

```python
nr_combined_unisons = piece.notes(combineUnisons = True)
piece.melodic(df = nr_combined_unisons)
```

Compare the results of this with `piece.melodic()` to see the difference!

Of course there might be other situations in which a special DataFrame of notes and rests would be passed to the `melodic()` function.  For example, if 'structural tones' are derived from `beatStrengths()`, then passing that dataframe to the `melodic()` function would produce a kind of 'Ur' melody devoid of non-structural tones:  

```python
beat_strength_notes = piece.beatStrengths()  
piece.melodic(df = beat_strength_notes)
```  

### Combining Consecutive Pitch Repetition/Rests

The `melodic()` function does not contain `combineUnisons` or `combineRests` parameters. If you want to combine these, start with the `notes()` function and pass this result to `melodic()` as follows:


```python
# notes with combined unisons
nr_no_unisons = piece.notes(combineUnisons = True)

# now pass this to melodic
piece.melodic(df = nr_no_unisons)
```

![Alt text](images/mel_5.png)

Or (though less useful),  

```python
# notes with separate rests 
nr_separate_rests = piece.notes(combineRests = False)  

# now pass this to melodic
piece.melodic(df = nr_separate_rests) 
``` 

## `fillna()` and `dropna()` Functions  

We have previously seen the `fillna()` function which, when applied to a DataFrame, replaces all "NaN" objects with the chosen text. For example:  

```python
piece.melodic().fillna('-')  
```

We are also able to apply the `dropna()` function, which (by default) removes all rows (beats) from the table consisting *entirely* of "NaN" values.  

```python
piece.melodic().dropna()
```

This would be equivalent to specifiying the function as follows:  

```python
piece.melodic().dropna(how = 'all')
```

Alternatively, rows could be dropped if they contian *any* "NaN" values:  

```python
piece.melodic().dropna(how = 'any')
```


## More About Measures, Beats, and Offsets: The `detailIndex()` Function  

By default, the `melodic()` function returns a DataFrame which indexes by offsets: That is, events in the piece are counted by which overall beat in the piece they fall on. This is useful for measuring absolute time distances between events, but not as useful for a human reader who wants to refer back to the musical score itself. It is easy to include measure and beat indexes, where each event will be shown in reference to which measure (and beat of that measure) in which it appears by passing the result of the function to the `detailIndex()` function as shown. Note the capitalization of the `detailIndex()` function:  

```python
# melodic intervals
mel = piece.melodic()  

# now pass this to detailIndex
mel_di = piece.detailIndex(mel)
```

For more information about the `detailIndex` function, consult [the documentation](09_DetailIndex.md).  

## Melodic Intervals in a Corpus

We can also use the `melodic()` function to analyze an entire corpus of pieces. A function for this is available when you import the `corpus_tools` module.  Here is how to do use it:

### Build your corpus:

```python
# build the file lists and corpus
local_file_list = ['MEI/Bach_BWV_0772.mei', 'MEI/Bach_BWV_0773.mei']
corpus = CorpusBase(local_file_list)
# or 
remote_file_list  = ['https://crimproject.org/mei/CRIM_Model_0001.mei',
       'https://crimproject.org/mei/CRIM_Mass_0002_1.mei']
corpus = CorpusBase(local_file_list)  
```

### Now pass that corpus to the chosen function:


```python
corpus_mel(corpus, kind_choice='d', compound_choice=True, directed_choice=True)
```
<br>

![alt text](images/corp_mel.png)

<br>


## Charts with Melodic Intervals

As we explain the [Visualizations_Summary](/18_Visualizations_Summary.md), the **Plotly** library provides some powerful tools for displaying tabular data in various charts and plots.

### For a Single Piece

First with the voices as separate charts:

![alt text](images/bar_mel_voices.png)

<br>

<Details>

<Summary>Code to Use</Summary>

```python
# import the piece
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata
chart_title = "Distribution of Melodic Intervals in " + md['composer'] + ", " + md['title']

# set parameters for melodic interval extraction
kind_choice = 'q'        # 'd' for diatonic, 'q' for quality
compound_choice = True   # True for compound intervals, False for simple intervals
directed_choice = True   # True for directed intervals, False for undirected intervals
exclude_rests = True     # True to exclude rests, False to include rests

# get the melodic intervals
mel = piece.melodic(kind=kind_choice, compound=compound_choice, directed=directed_choice)
mel = piece.numberParts(mel)  # add part numbers to the column names
voices = mel.columns.to_list()

# melt: the offset (index) stays fixed, every voice column becomes rows
mel_long = (mel.rename_axis('Offset')
               .reset_index()
               .melt(id_vars='Offset',
                     value_vars=voices,
                     var_name='Voice',
                     value_name='Interval'))

# drop empty cells (and rests, if requested)
mel_long = mel_long.dropna(subset=['Interval'])
if exclude_rests:
    mel_long = mel_long[mel_long['Interval'] != 'Rest']
mel_long['Interval'] = mel_long['Interval'].astype(str)

# order intervals: largest descending ... unison ... largest ascending
# works for both diatonic ('-2', '3') and quality ('-m3', 'P5', 'M9') labels
import re
def interval_sort_key(label):
    if label == 'Rest':
        return (float('inf'), 0)
    descending = label.startswith('-')
    quality, size = re.match(r'([A-Za-z]*)(\d+)', label.lstrip('-')).groups()
    q_rank = {'d': 0, 'm': 1, 'P': 2, 'M': 3, 'A': 4}.get(quality[:1], 2)
    size = int(size)
    return (-size, -q_rank) if descending else (size, q_rank)

interval_order = sorted(mel_long['Interval'].unique(), key=interval_sort_key)

# count intervals per voice
mel_counts = (mel_long.groupby(['Interval', 'Voice'])
                      .size()
                      .reset_index(name='Count'))

# colors: one per voice
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {voice: custom_palette[i % len(custom_palette)] for i, voice in enumerate(voices)}

# chart with each voice as a facet, intervals on the x-axis, counts on the y-axis
fig = px.bar(mel_counts,
             x='Interval',
             y='Count',
             color='Voice',
             facet_col='Voice',
             category_orders={'Interval': interval_order, 'Voice': voices},
             color_discrete_map=color_dict,
             height=700,
             width=1000,
             title=chart_title)
fig.show()

# or, if you prefer a single stacked bar chart with all voices combined:

# all voices combined on a single chart
fig = px.bar(mel_counts,
             x='Interval',
             y='Count',
             color='Voice',
             category_orders={'Interval': interval_order, 'Voice': voices},
             color_discrete_map=color_dict,
             height=700,
             width=1000,
             title=chart_title)
fig.show()

```

</Details>

<br>


Or a combined chart with all voices stacked:


![alt text](images/bar_mel_combined.png)

<br>

<Details>

<Summary>Code to Use</Summary>

```python
# import the piece
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata
chart_title = "Distribution of Melodic Intervals in " + md['composer'] + ", " + md['title']

# set parameters for melodic interval extraction
kind_choice = 'q'        # 'd' for diatonic, 'q' for quality
compound_choice = True   # True for compound intervals, False for simple intervals
directed_choice = True   # True for directed intervals, False for undirected intervals
exclude_rests = True     # True to exclude rests, False to include rests

# get the melodic intervals
mel = piece.melodic(kind=kind_choice, compound=compound_choice, directed=directed_choice)
mel = piece.numberParts(mel)  # add part numbers to the column names
voices = mel.columns.to_list()

# melt: the offset (index) stays fixed, every voice column becomes rows
mel_long = (mel.rename_axis('Offset')
               .reset_index()
               .melt(id_vars='Offset',
                     value_vars=voices,
                     var_name='Voice',
                     value_name='Interval'))

# drop empty cells (and rests, if requested)
mel_long = mel_long.dropna(subset=['Interval'])
if exclude_rests:
    mel_long = mel_long[mel_long['Interval'] != 'Rest']
mel_long['Interval'] = mel_long['Interval'].astype(str)

# order intervals: largest descending ... unison ... largest ascending
# works for both diatonic ('-2', '3') and quality ('-m3', 'P5', 'M9') labels
import re
def interval_sort_key(label):
    if label == 'Rest':
        return (float('inf'), 0)
    descending = label.startswith('-')
    quality, size = re.match(r'([A-Za-z]*)(\d+)', label.lstrip('-')).groups()
    q_rank = {'d': 0, 'm': 1, 'P': 2, 'M': 3, 'A': 4}.get(quality[:1], 2)
    size = int(size)
    return (-size, -q_rank) if descending else (size, q_rank)

interval_order = sorted(mel_long['Interval'].unique(), key=interval_sort_key)

# count intervals per voice
mel_counts = (mel_long.groupby(['Interval', 'Voice'])
                      .size()
                      .reset_index(name='Count'))

# colors: one per voice
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {voice: custom_palette[i % len(custom_palette)] for i, voice in enumerate(voices)}



# all voices combined on a single chart
fig = px.bar(mel_counts,
             x='Interval',
             y='Count',
             color='Voice',
             category_orders={'Interval': interval_order, 'Voice': voices},
             color_discrete_map=color_dict,
             height=700,
             width=1000,
             title=chart_title)
fig.show()

```

</Details>

<br>



### For a Corpus

A chart for a complete corpus:

![alt text](images/mel_corpus_chart.png)

Here is how to do it:


<br>

<Details>

<Summary>Code to Use</Summary>

```python

remote_file_list  = ['https://crimproject.org/mei/CRIM_Model_0001.mei',
       'https://crimproject.org/mei/CRIM_Mass_0002_1.mei']
corpus = CorpusBase(remote_file_list)

# set parameters for melodic interval extraction
kind_choice = 'd'        # 'd' for diatonic, 'q' for quality
compound_choice = True   # True for compound intervals, False for simple intervals
directed_choice = True   # True for directed intervals, False for undirected intervals
exclude_rests = True     # True to exclude rests, False to include rests

# the corpus function
corpus_melodic_ints = corpus_mel(corpus, kind_choice=kind_choice,
                                 compound_choice=compound_choice,
                                 directed_choice=directed_choice)

# melt: metadata/position columns stay fixed, every voice column becomes rows
id_cols = ['Composer', 'Title', 'Date', 'Measure', 'Beat', 'Progress']
voice_cols = [c for c in corpus_melodic_ints.columns if c not in id_cols]

mel_long = corpus_melodic_ints.melt(id_vars=id_cols,
                                    value_vars=voice_cols,
                                    var_name='Voice',
                                    value_name='Interval')

# drop empty cells (and rests, if requested)
mel_long = mel_long.dropna(subset=['Interval'])
if exclude_rests:
    mel_long = mel_long[mel_long['Interval'] != 'Rest']
mel_long['Interval'] = mel_long['Interval'].astype(str)

# order intervals: largest descending ... unison ... largest ascending
# works for both diatonic ('-2', '3') and quality ('-m3', 'P5', 'M9') labels
import re
def interval_sort_key(label):
    if label == 'Rest':
        return (float('inf'), 0)
    descending = label.startswith('-')
    quality, size = re.match(r'([A-Za-z]*)(\d+)', label.lstrip('-')).groups()
    q_rank = {'d': 0, 'm': 1, 'P': 2, 'M': 3, 'A': 4}.get(quality[:1], 2)
    size = int(size)
    return (-size, -q_rank) if descending else (size, q_rank)

interval_order = sorted(mel_long['Interval'].unique(), key=interval_sort_key)

# count intervals per voice
mel_counts = (mel_long.groupby(['Interval', 'Voice'])
                      .size()
                      .reset_index(name='Count'))

# chart
chart_title = "Distribution of Melodic Intervals in Corpus"
fig = px.bar(mel_counts, 
              x='Interval', 
              y='Count', 
              color='Voice',
              title=chart_title,
              category_orders={'Interval': interval_order, 'Voice': voice_cols})
fig.update_layout(xaxis_title="Interval",
                  yaxis_title="Count",
                  legend_title='Voices',
                  height=700,
                  width=1000)
fig.show()
```

</Details>

<br>
---

## Sections in this guide

  * [01_Introduction_and_Corpus](/tutorial/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](/tutorial//02_Notes_Rests.md)
  * [03_Durations](/tutorial//03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](/tutorial//04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](/tutorial//05_Detail_Index.md)
  * [06_Melodic_Intervals](/tutorial//06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals](/tutorial//07_Harmonic_Intervals.md)
  * [08_Contrapuntal_Modules](/tutorial//08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](/tutorial//09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](/tutorial//10_Lyrics_Homorhythm.md)
  * [11_Cadences](/tutorial//11_Cadences.md)
  * [12_Presentation_Types](/tutorial//12_Presentation_Types.md)
  * [13_Musical_Examples_Verovio](/tutorial//13_Musical_Examples_Verovio.md)
  * [14_Model_Finder](/tutorial//14_Model_Finder.md)
  * [15_Network_Graphs](/tutorial//15_Network_Graphs.md)
  * [16_Python_Basics](/tutorial//16_Python_Basics.md)
  * [17_Pandas_Basics](/tutorial//17_Pandas_Basics.md)
  * [18_Visualizations_Summary](/tutorial//18_Visualizations_Summary.md)
  * [19_Music21_Basics](/tutorial//18_Music21_Basics.md)
  * [20_Melodic_Interval_Families](/tutorial//20_Melodic_Interval_Families.md)
  * [99_Local_Installation](/tutorial//99_Local_Installation.md)