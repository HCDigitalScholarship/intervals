# Finding the Melodic Intervals in Pieces  

We have previously seen how `piece.notes()` can output a table of each time a note in the piece changes. Using functions in the CRIM Intervals library, we are also able to create tables of intervallic distances between notes.  

## The `melodic()` Function  

In its simplest form, `piece.melodic()` returns a DataFrame of diatonic intervals within each voice part in the piece. There is more to the story, however, since the `melodic()` function has a number of parameters that users can adjust to report intervallic distances in different ways:  

Default usage:  

```python
piece.melodic()  
```

![Alt text](images/mel_1.png)
​
The most important parameters:
* `kind`, for controlling if diatonic, chromatic, or other types of intervals are reported; default is diatonic  
* `directed`, whether the report is simply a raw interval, or also reports whether it goes up or down; default includes direction  
* `compound`, whether intervals larger than an octave are reported as simpler versions; default reports compounds as they actually appear  
​
And the more specialized parameters:
* `unit`, the possibility to measure the intervals at each new onset of a note, or to sample them at some regular time interval; default uses **actual** onsets and values
* `end`, determines the offset with which interval is associated (the first or second note of the pair): default places intervals at the offset of their **second** note
* `df`, the possibility to pass some dataframe of notes to the function in order to check the intervals of that passage or selection  
​
The details of each parameter's usage and default values are explained below. 

## `melodic()` parameters  

### Differentiating between Diatonic, Chromatic, and other intervals: the `kind` (str) parameter  

The `melodic()` function contains a parameter `kind`, which has a default value of "q". These inputs are case sensitive:  
Diatonic with quality. This refers to "P8" for a perfect octave (e.g. C4 -> C5), "M3" for a major third interval (e.g. C5 -> E5), and "m3" for minor third interval (e.g. C5 -> E-5), for example:  

```python
piece.melodic(kind = 'q')  
```

**Diatonic without quality**. Provides outputs such as "8" for an octave, and "3" for a third interval.  

```python
piece.melodic(kind = "d")
```

![Alt text](images/mel_2.png)

**Chromatic**. The difference between two pitches in semitones. Outputs "12" for an octave interval (e.g. C4 -> C5), "6" for a tritone interval (e.g. C5 -> F#5), and "0" for a unison (e.g. C5 -> C5):  

```python
piece.melodic(kind = "c")
```


**Zero-based diatonic** intervals. To musicians it makes sense that a unison is represented as one, but this can produce some odd results in computational systems, in which calculated distances are 'zero-based':  the distance between C4 and C4 is in fact 0, not 1 (as musicians would have it). Zero-Based Diatonic intervals are thus sometimes useful.  The problem does not occur in Chromatic intervals, where the system reports the absolute distance in semitones between any two tones (C4 to C#4 is 1, not 2). Outputs "7" for a perfect octave interval up (e.g. D3 -> D4), "-4" for a fifth interval down (e.g. F5 -> A5), "2" for a third interval up (e.g. G4 -> B5):  

```python
piece.melodic(kind = "z")
```

### Up and Down vs. Aboslute: The `directed` Parameter  

By default, `directed = True`, which causes the melodic intervals to report their direction; "4" is an ascending fourth; "-4" is descending. Itt might be useful, however, simply to report the absolute distance without direction, such as if the aim is to know how many leaps of a sixth appear in a piece regardless of direction.  In this case, use `directed = False`.  


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

Using `piece.melodic(compound = False)`, in contrast, analyzes all intervals as if they are within a octave (what musicians call the 'simple' intervallic distances). In this case the interval from C4 to E5 would be a diatonic 3, a chromatic 4, M3 using 'with quality', and 2 using 'zero-based with quality'. Note that an octave itself is not reduced to a unison.  

### Sampling Melodies at Regular Time Intervals: The `unit` Parameter  

In most cases, the `melodic()` function will be used to trace movement at each new onset of a note. Sometimes, however, it could be useful to 'sample' the tone being sounded at some regular time interval (for instance, if the purpose was to consider time series data). This can be accomplished with the `unit` parameter. This parameter's default value, `unit = 0`, simply means that melodic intervals will be assigned at each new onset of a note. Setting `unit = 1`, however, will force a 'sampled' reading of the intervallic distance at every quarter note (since '1.0 corresponds to that value in music21'):  

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

Normally, CRIM Intervals associates melodic intervals with the moment of change, namely the onset of the **second** note of the pair. If C5 sounds on offset 1.0 and D5 sounds on offset 2.0, a melodic interval of M2 will be associated with offset 2.0. Therefore, the default value of this parameter is `end = True`, in which the interval is associated with the 'end' of the pair. In some cases, it might be useful to associate the interval with the first note of the pair instead. In this case, `end = False`.  

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

### Dealing with Consecutive Pitch Repetition/Rests: The `combineUnisons` and `combineRests` Parameters:  

Unlike the `notes()` functions, the `melodic()` function does not contain `combineUnisons` or `combineRests` parameters. These parameters, however, can still be used in conjunction with the `melodic()` function as follows:  

```python
nr_no_unisons = piece.notes(combineUnisons = True)
piece.melodic(df = nr_no_unisons)
```

![Alt text](images/mel_5.png)

Or (though less useful),  

```python
nr_separate_rests = piece.notes(combineRests = False)  
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
mel = piece.melodic()  
mel_di = piece.detailIndex(mel)
```

For more information about the `detailIndex` function, consult [the function's documentation](09_DetailIndex.md).  

## Melodic Intervals in a Corpus


The `corpus.batch` method will help you produce a combined picture of melodic intervals across any corpus.

<br>

![alt text](images/corp_mel.png)

<br>

<Details>

<Summary>Code to Run</Summary>

```python
def corpus_mel(corpus, combine_unisons_choice, combine_rests_choice, kind_choice, directed, compound):
    func = ImportedPiece.notes  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'combineUnisons': combine_unisons_choice, 'combineRests': combine_rests_choice}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=False)
    
    func2 = ImportedPiece.melodic
    list_of_dfs = corpus.batch(func = func2,
                               kwargs = {'df' : list_of_dfs, 'kind' : kind_choice, 'directed' : directed, 'compound' : compound},
                               metadata = False)
    func3 = ImportedPiece.detailIndex
    list_of_dfs = corpus.batch(func = func3, 
                            kwargs = {'df': list_of_dfs}, 
                            metadata = True)
    mel = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    mel = mel[cols_to_move + [col for col in mel.columns if col not in cols_to_move]]
    return mel

# define the settings
combine_unisons_choice = False
combine_rests_choice = False
kind_choice = 'd'
directed = True
compound = True


# run the function
mel = corpus_mel(corpus, combine_unisons_choice, combine_rests_choice, kind_choice, directed, compound).fillna('')
mel
```

</Details>

## Charts with Melodic Intervals

As we explain the [Visualizations_Summary](/18_Visualizations_Summary.md), the **Plotly** library provides some powerful tools for displaying tabular data in various charts and plots.

### For a Single Piece

First with the voices as separate charts:

![alt text](images/bar_mel_voices.png)

<br>

<Details>

<Summary>Code to Use</Summary>

```python
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata  
chart_title = "Distribution of Melodic Intervals in " + md['composer'] + ", " + md['title']

# custom interval order
int_order = ["-P8", "-M7", "-m7", "-M6", "-m6", "-P5", "-P4", "-M3", 
                          "-m3", "-M2", "-m2", "P1", "m2", "M2", "m3", "M3",
                          "P4", "P5", "m6", "M6", "m7", "M7", "P8"]
# get the melodic intervals
mel = piece.melodic().fillna("-")  
mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()  
mel.rename(columns={'index': 'interval'}, inplace=True)  
mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)  
mel = mel.sort_values(by="interval").dropna().copy()  
voices = mel.columns.to_list()[1:]  # Exclude 'interval' column
# Create a custom color palette
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {voice: custom_palette[i % len(custom_palette)] for i, voice in enumerate(voices)}
# Melt the DataFrame to long format suitable for px.bar
melted_mel = mel.melt(id_vars='interval', var_name='voice', value_name='count')
# Plot using Plotly Express
fig = px.bar(melted_mel, 
             x='interval', 
             y='count', 
             color='voice', 
             facet_col='voice', 
             category_orders={'interval': int_order}, 
             color_discrete_map=dict(zip(voices, custom_palette)),
             height=700,
             width=1000,
             title=chart_title)
fig.show()
```

</Details>

<br>


And then combined:


![alt text](images/bar_mel_combined.png)

<br>

<Details>

<Summary>Code to Use</Summary>

```python
url = 'https://crimproject.org/mei/CRIM_Model_0001.mei'
piece = importScore(url)

# give the chart a meaningful title based on your piece:
md = piece.metadata  
chart_title = "Distribution of Melodic Intervals in " + md['composer'] + ", " + md['title']

# custom interval order
int_order = ["-P8", "-M7", "-m7", "-M6", "-m6", "-P5", "-P4", "-M3", 
                          "-m3", "-M2", "-m2", "P1", "m2", "M2", "m3", "M3",
                          "P4", "P5", "m6", "M6", "m7", "M7", "P8"]
# get the melodic intervals
mel = piece.melodic().fillna("-")  
mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()  
mel.rename(columns={'index': 'interval'}, inplace=True)  
mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)  
mel = mel.sort_values(by="interval").dropna().copy()  
voices = mel.columns.to_list()[1:]  # Exclude 'interval' column
# Create a custom color palette
custom_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
color_dict = {voice: custom_palette[i % len(custom_palette)] for i, voice in enumerate(voices)}
# Melt the DataFrame to long format suitable for px.bar
melted_mel = mel.melt(id_vars='interval', var_name='voice', value_name='count')


# Create the stacked bar chart
fig = px.bar(melted_mel, 
             x='interval', 
             y='count', 
             color='voice', 
             barmode='stack',
             height=700,
             width=1000,
            title=chart_title)

fig.show()
```

</Details>

<br>



### For a Corpus

Here is a chart for an entire corpus:

![alt text](images/mel_corpus_chart.png)


<br>

<Details>

<Summary>Code to Use</Summary>

```python
# mel corpus function for batch processing
def corpus_mel(corpus, combine_unisons_choice, combine_rests_choice, kind_choice, directed, compound):
    func = ImportedPiece.notes  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'combineUnisons': combine_unisons_choice, 'combineRests': combine_rests_choice}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=False)
    
    func2 = ImportedPiece.melodic
    list_of_dfs = corpus.batch(func = func2,
                               kwargs = {'df' : list_of_dfs, 'kind' : kind_choice, 'directed' : directed, 'compound' : compound},
                               metadata = False)
    func3 = ImportedPiece.detailIndex
    list_of_dfs = corpus.batch(func = func3, 
                            kwargs = {'df': list_of_dfs}, 
                            metadata = True)
    mel = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    mel = mel[cols_to_move + [col for col in mel.columns if col not in cols_to_move]]
    return mel

# settings
combine_unisons_choice = False
combine_rests_choice = False
kind_choice = 'd'
directed = True
compound = True
exclude_rests = True

# orderings

interval_order_quality = ["-P8", "-M7", "-m7", "-M6", "-m6", "-P5", "-P4", "-M3", 
                          "-m3", "-M2", "-m2", "P1", "m2", "M2", "m3", "M3",
                          "P4", "P5", "m6", "M6", "m7", "M7", "P8"]

# load corpus


file_list = ['https://crimproject.org/mei/CRIM_Model_0001.mei', 'https://crimproject.org/mei/CRIM_Model_0008.mei']

corpus = CorpusBase(file_list)

# run function and create plot
mel = corpus_mel(corpus, combine_unisons_choice, combine_rests_choice, kind_choice, directed, compound)
mel_no_mdata = mel.drop(['Composer', 'Title', "Date"], axis=1)
mel_no_mdata = mel_no_mdata.map(str)

mel_counts = pd.DataFrame(mel_no_mdata.apply(pd.Series.value_counts).fillna(0))

# drop row of nas:
mel_counts = mel_counts.drop('nan', axis=0)

if exclude_rests == True:
    mel_counts = mel_counts.drop('Rest', axis=0)
    
                                                                    
# apply the categorical list and sort.  
if kind_choice == 'q':
    mel_counts.index = pd.CategoricalIndex(mel_counts.index, categories=interval_order_quality, ordered=True)
    mel_counts.sort_index(inplace=True)
else:
    mel_counts.index = pd.to_numeric(mel_counts.index, errors='coerce')

    negative_df = mel_counts[mel_counts.index < 0].sort_index(ascending=True)
    non_negative_df = mel_counts[mel_counts.index >= 0].sort_index(ascending=True)
    
    # Step 2: Concatenate the two DataFrames
    mel_counts = pd.concat([negative_df, non_negative_df])
    mel_counts.index.rename('interval', inplace=True)
voices = mel_counts.columns.to_list() 
chart_title = "Distribution of Melodic Intervals in Corpus"
fig = px.bar(mel_counts, x=mel_counts.index, y=list(mel_counts.columns),
                    title=chart_title)
fig.update_layout(xaxis_title="Interval", 
                    yaxis_title="Count",
                    legend_title='Voices',
                       height=700,
                       width=1000)
fig.show()


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