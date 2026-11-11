# Harmonic Intervals and Sonorities  

## Table of Contents
1. [The `harmonic()` Function in Brief](#the-harmonic-function-in-brief)
2. [`harmonic()` Parameters](#harmonic-parameters)
3. [The `sonorities` Function in Brief](#the-sonorities-function-in-brief)
4. [Ngrams of Sonorities](#ngrams-of-sonorities)
5. [More About Measures, Beats, and Offsets: The `detailIndex()` Function](#more-about-measures-beats-and-offsets-the-detailindex-function)
6. [Harmonic Intervals in a Corpus](#harmonic-intervals-in-a-corpus)
7. [Charts with Harmonic Intervals](#charts-with-harmonic-intervals)
8. [Harmonic Intervals in a Corpus](#harmonic-intervals-in-a-corpus-1)
9. [Sections in this guide](#sections-in-this-guide)

We have just seen how the `melodic()` function allows us to examine the points in the score where the pitch changes in a single voice, resulting in a melodic intervals. We are also able to examine harmonic intervals, which is the difference in pitch between two voices who sound a note simultaneously. 

Here we show two different approaches:

* The `harmonic()`, which reports intervals between all possible **pairs** of voices
* The `sonority()` function, which reports all the intervals above the lowest sounding part at once.  


## The `harmonic()` Function in Brief

```python
harmonic(kind='q', directed=True, compound=True, againstLow=False, df=None)
```

In its simplest form, `harmonic()` simply produces a DataFrame of each harmonic interval present in a piece, between all possible voice pairs:  

```python
path = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(path)
harmonic_intervals = piece.harmonic()
```

![Alt text](images/har_1.png)

The function can, however, be modified by each of its parameters:  
* `kind`, for controlling if diatonic, chromatic, or other types of intervals are reported; default is diatonic  
* `directed`, for controlling whether the report is simply a raw interval, or also reports whether it goes up or down (indicated with a '-' if down); default includes direction  
* `compound`, whether intervals larger than an octave are reported as simpler versions; default reports compounds as they actually appear  
* `againstLow`, whether harmonic intervals are produced for every combination of voices, or just between each non-lowest voice and the lowest active voice at each harmonic offset; default generates every combination of voices

## `harmonic()` Parameters  

### Differentiating Between Diatonic, Chromatic, and Other Intervals with the `kind` Parameter  

The `harmonic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive:  

**Diatonic with Quality**. These qualities are outputs such as "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5):  

```python
piece.harmonic(kind = 'q')
```

**Diatonic without Quality**. Provides outputs such as "8" for an octave, and "3" for a third interval:  

```python
piece.harmonic(kind = "d")
```  

![Alt text](images/har_2.png)

**Chromatic**. Simply the difference in pitch including all intermediary notes. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5):  

```python
piece.harmonic(kind = "c")
```  

**Zero-based**. Diatonic intervals, begins counting at 0 rather than 1. Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5):  

```python
piece.harmonic(kind = "z")
```

### Up and Down vs. Aboslute: The `directed` Parameter  

By default, `directed = True`, which causes the melodic intervals to report their direction; "4" is an ascending fourth; "-4" is descending. It might be useful, however, simply to report the absolute distance without direction, such as if the aim is to know how many harmonic intervals of a sixth appear in a piece regardless of their direction.  In this case, use `directed = False`.  

```python
#Default value:  
piece.harmonic(directed = True)
``` 

[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "-4"  

```python
piece.harmonic(directed = False)
```


[C5 -> G5] will return a diatonic interval of "4"  
[G5 -> C5] will return a diatonic interval of "4"  

### Managing Intervals Greater than an Octave: The `compound` Parameter  

The `harmonic()` function contains a parameter `compound`, with a default value of `True`. This means that intervals with a span greater than an octave will always be returned as such.  The interval from C4 to E5 would be a diatonic 10, a chromatic 16, M10 using 'with quality', and 9 using 'zero-based diatonic'. 

```python
piece.harmonic(compound = True)
```

Using `piece.harmonic(compound = False)`, in contrast, analyzes all intervals as if they are within a octave (what musicians call the 'simple' intervallic distances). In this case the interval from C4 to E5 would be a diatonic 3, a chromatic 4, M3 using 'with quality', and 2 using 'zero-based with quality'. Note that an octave itself is not reduced to a unison.  

![Alt text](images/har_3.png)

Note that with `compound = False` an octave itself is not reduced to a unison*. You could map the octave to a unison by using the `replace()` function, for instance:  

```python
piece.harmonic(kind = 'd', compound = False).replace('8', '1')
```

### The `againstLow` Parameter  

By default, `harmonic()` generates a DataFrame of the harmonic intervals between **all pairs** of voice parts present at a given offset. But it is also possible to report the interval *between each voice and the lowest voice present at each offset*. When changed to `True`, harmonic intervals will only be shown between the lowest voice and each other voice at a given offset:  

```python
piece.harmonic(againstLow = True)
```

![Alt text](images/har_4.png)

This means that if a piece contained a Bass, Tenor, Alto, and Soprano voice, all four voices were sounding, and `againstLow` was set to **True**, `harmonic()` will generate the interval between the Bass and the Tenor, the Bass and the Alto, and the Bass and the Soprano. It will **NOT** generate any harmonic interval between the Tenor and Alto, Tenor and Soprano, or Alto and Soprano. The same logic would also apply even if the Bass was not present, where only the harmonic intervals appearing would be between the Tenor and Alto voices, and between the Tenor and Soprano voices.  

## The `sonorities` Function in Brief

There is also a separate `sonorities` function, which in turn uses the results from harmonic to produce a single column representing all of the vertical intervals heard at each 'onset' of any note throughout the piece.  The result is something like a figured bass representation of the harmonies at each moment.

In its simplest form, we call this on piece as follows:

```python
piece.sonorities(kind='d', directed=True, compound='simple', sort=True)
```

There are also several parameters. The first three are simply those used with `harmonic`, as described above.  One additional parameter, `sort`, determines the *order* of the intervals.  If `sort=True` (which is the default), then the intervals will be sorted from largest to smallest.  Duplicates and unisons will be removed.  


```python
piece.sonorities(sort=True)
```

![Alt text](images/sonoroties_t.png)

But if `sort=False`, then *all* intervals will be reported (unisons and duplicates included), and they will appear in order from top staff to bottom.

```python
piece.sonorities(sort=False)
```

![Alt text](images/sonorities_f.png)

## Ngrams of Sonorities

We could also use the `ngrams()` function to find the **sequences of sonorities** in a piece, or across a corpus.  Here is an example of how to do this for a single piece:


```python
son = piece.sonorities(sort=False)
piece.ngrams(df = son, n=3)
```

![Alt text](images/sonoritie_ngrams.png)



### Dealing with Consecutive Pitch Repetition/Rests: The `combineUnisons` and `combineRests` Parameters:  

Unlike the `notes()` functions, the `harmonic()` function does not contain `combineUnisons` or `combineRests` parameters. These parameters, however, can still be used in conjunction with the `harmonic()` function as follows:  

```python
nr_no_unisons = piece.notes(combineUnisons = True)
piece.harmonic(df = nr_no_unisons)
```

Or (though less useful),  

```python
nr_separate_rests = piece.notes(combineRests = False)  
piece.harmonic(df = nr_separate_rests)
```  


### `fillna()` and `dropna()` Functions  

We have previously seen the `fillna()` function which, when applied to a DataFrame, replaces all "NaN" objects with the chosen text. For example:  

```python
piece.harmonic().fillna('-')
``` 

We are also able to apply the `dropna()` function, which (by default) removes all rows (beats) from the table consisting *entirely* of "NaN" values.  

```python
piece.harmonic().dropna()
```

This would be equivalent to specifiying the function as follows:  

```python
piece.harmonic().dropna(how = 'all')
```


Alternatively, rows could be dropped if they contian *any* "NaN" values:  

```python
piece.harmonic().dropna(how = 'any')
``` 

## More About Measures, Beats, and Offsets: The `detailIndex()` Function  

By default, the `harmonic()` function returns a DataFrame which indexes by offsets: That is, events in the piece are counted by which overall beat in the piece they fall on. This is useful for measuring time distances between events, but not for a human reader to refer back to the musical score itself. It is easy to include measure and beat indexes by passing the result of the function to the `detailIndex()` function as shown:  

```python
har = piece.harmonic()  
har_DI = piece.detailIndex(har)
``` 

For more information about the `detailIndex` function, consult [the function's documentation](09_DetailIndex.md).  


## Harmonic Intervals in a Corpus

Our Corpus Tools includes a method for working with harmonic intervals in a set of pieces.  Here we show how to do this.  See more in the [Corpus Tools](/tutorial/21_Corpus_Tools.md) section of this guide.

<br>

![alt text](images/corp_har.png)

<br>

<Details>

<Summary>Code to Run</Summary>


```python
# make the corpus
remote_file_list  = ['https://crimproject.org/mei/CRIM_Model_0001.mei',
       'https://crimproject.org/mei/CRIM_Mass_0002_1.mei']
corpus = CorpusBase(remote_file_list)

# set parameters for melodic interval extraction
kind_choice = 'd'        # 'd' for diatonic, 'q' for quality
compound_choice = True   # True for compound intervals, False for simple intervals
directed_choice = True   # True for directed intervals, False for undirected intervals


# now run the corpus function
corpus_har_ints = corpus.har(kind_choice='d', compound_choice=True, directed_choice=True, key_sig=False, include_final=False)

corpus_har_ints                   
```


</Details>

## Charts with Harmonic Intervals

As we explain the [Visualizations_Summary](/18_Visualizations_Summary.md), the **Plotly** library provides some powerful tools for displaying tabular data in various charts and plots.

### For a Single Piece

#### Voice Pairs as Separate "facets":


![alt text](images/har_chart_facets.png)


<br>

<Details>

<Summary>Code to Use</Summary>

```python
import re

# import the piece
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata
chart_title = "Distribution of Harmonic Intervals in " + md['composer'] + ", " + md['title']

# set parameters for harmonic interval extraction
kind_choice = 'q'        # 'd' for diatonic, 'q' for quality
compound_choice = True   # True for compound intervals, False for simple intervals
directed_choice = True   # True for directed intervals, False for undirected intervals
exclude_rests = True     # True to exclude rests, False to include rests

# get the harmonic intervals
har = piece.harmonic(kind=kind_choice, compound=compound_choice, directed=directed_choice)
har = piece.numberParts(har)  # add part numbers to the column names
voice_pairs = har.columns.to_list()

# melt: the offset (index) stays fixed, every voice-pair column becomes rows
har_long = (har.rename_axis('Offset')
               .reset_index()
               .melt(id_vars='Offset',
                     value_vars=voice_pairs,
                     var_name='Voice_Pair',
                     value_name='Interval'))

# drop empty cells (and rests, if requested)
har_long = har_long.dropna(subset=['Interval'])
har_long['Interval'] = har_long['Interval'].astype(str)
if exclude_rests:
    har_long = har_long[har_long['Interval'] != 'Rest']

# order intervals: largest negative (voice crossing) ... unison ... largest positive
# works for both diatonic ('-2', '8') and quality ('-m3', 'P5', 'M10') labels
def interval_sort_key(label):
    m = re.match(r'(-?)([A-Za-z]*)(\d+)', label)
    if not m:                       # 'Rest' or anything unexpected goes at the end
        return (float('inf'), 0)
    sign, quality, size = m.groups()
    q_rank = {'d': 0, 'm': 1, 'P': 2, 'M': 3, 'A': 4}.get(quality[:1], 2)
    size = int(size)
    return (-size, -q_rank) if sign else (size, q_rank)

interval_order = sorted(har_long['Interval'].unique(), key=interval_sort_key)

# count intervals per voice pair
har_counts = (har_long.groupby(['Interval', 'Voice_Pair'])
                      .size()
                      .reset_index(name='Count'))


# colors: one per voice pair
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {vp: custom_palette[i % len(custom_palette)] for i, vp in enumerate(voice_pairs)}

# each pair as a 'facet' with its own small chart
fig_facet = px.bar(har_counts,
             x='Interval',
             y='Count',
             color='Voice_Pair',
             facet_col='Voice_Pair',
             facet_col_wrap=3,    
             category_orders={'Interval': interval_order, 'Voice_Pair': voice_pairs},
             color_discrete_map=color_dict,
             height=600,
             width=1000,
             title=chart_title)
fig_facet.show()

```

</Details>

<br>


#### Voice Pairs Stacked in a Single Chart:

Here we stack the pairs single stacked bar chart, with each voice pair as a separate color:


![alt text](images/har_chart_combined.png)


<br>

<Details>

<Summary>Code to Use</Summary>

```python
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata  
chart_title = "Distribution of Harmonic Intervals in " + md['composer'] + ", " + md['title']

# custom interval order
int_order = ["-P8", "-M7", "-m7", "-M6", "-m6", "-P5", "-P4", "-M3", 
                          "-m3", "-M2", "-m2", "P1", "m2", "M2", "m3", "M3",
                          "P4", "P5", "m6", "M6", "m7", "M7", "P8"]
# get the harmonic intervals
har = piece.harmonic().fillna("-")  
har = har.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()  
har.rename(columns={'index': 'interval'}, inplace=True)  
har['interval'] = pd.Categorical(har["interval"], categories=int_order)  
har = har.sort_values(by="interval").dropna().copy()  
voices = har.columns.to_list()[1:]  # Exclude 'interval' column
# Create a custom color palette
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {voice: custom_palette[i % len(custom_palette)] for i, voice in enumerate(voices)}
# Melt the DataFrame to long format suitable for px.bar
melted_har = har.melt(id_vars='interval', var_name='voice', value_name='count')


# Create the stacked bar chart
fig = px.bar(melted_har, 
             x='interval', 
             y='count', 
             color='voice', 
             barmode='stack',
             height=700,
             width=1200,
            title=chart_title)

fig.show()
```

</Details>

<br>



## Harmonic Intervals in a Corpus

Here is a chart for an entire corpus:


![alt text](images/har_corpus_ints_chart.png)

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
corpus_har_ints = corpus.har(kind_choice='d', compound_choice=True, directed_choice=True, key_sig=False, include_final=False)


# melt: metadata/position columns stay fixed, every voice column becomes rows
id_cols = ['Composer', 'Title', 'Date', 'Measure', 'Beat', 'Progress']
voice_pair_cols = [c for c in corpus_har_ints.columns if c not in id_cols]

har_long = corpus_har_ints.melt(id_vars=id_cols,
                                    value_vars=voice_pair_cols,
                                    var_name='Voice',
                                    value_name='Interval')

# drop empty cells (and rests, if requested)
har_long = har_long.dropna(subset=['Interval'])
if exclude_rests:
    har_long = har_long[har_long['Interval'] != 'Rest']
har_long['Interval'] = har_long['Interval'].astype(str)

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

interval_order = sorted(har_long['Interval'].unique(), key=interval_sort_key)

# count intervals per voice
har_counts = (har_long.groupby(['Interval', 'Voice'])
                      .size()
                      .reset_index(name='Count'))

# chart
chart_title = "Distribution of Harmonic Intervals in Corpus"
fig = px.bar(har_counts, 
             x='Interval', 
             y='Count', 
             color='Voice',
             title=chart_title,
             category_orders={'Interval': interval_order, 'Voice Pair': voice_cols})
fig.update_layout(xaxis_title="Interval",
                  yaxis_title="Count",
                  legend_title='Voice Pairs',
                  height=700,
                  width=1000)
fig.show()
```


</Details>

<br>



-----

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
