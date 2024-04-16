# Classifying Presentation Types:  Fuga, ID, and PEN

One of the key features of CRIM Intervals is its ability to predict complex contrapuntal patterns.  One 

This function uses several other functions to classify the entries in a given piece.


## Key Features

The output is a list, in order of offset, of each presentation type, including information about:

* The **measure and beat** of each entry in each pattern
* The **starting offset** of each entry in each pattern
* A **list of all the soggetti** involved. By default `melodic_ngram_length = 4`, and uses diatonic intervals. If *flexed entries* are permitted then there could be two or more soggetti in the cell (see below)
* The **melodic intervals between successive entries** (expressed as directed intervals, such as "P-5, P-8")
* The **time intervals *between successive entries** (expressed as offsets, like "8.0, 4.0, 8.0")
* The **predicted "presentation type"**:   Fuga, PEn, and ID according to time intervals between entries. NIm not yet supported.
* The **voice names of the entries**, in order of their appearance

**Singletons, Long Gaps, and Parallel Entries**

* **Singleton soggetti** (just one entry of a given motive in isolation, and not involved in a nearby presentation type) are not reported
* **Long gaps between entries**:  If two entries are separated by more than about 9 bars (70 offsets), the tool resets to a new pattern (otherwise the tool would classify impossibly long fugas over the course of a piece)
* **Parallel entries** in any passage. If two voices enter at the *same offset* (normally in parallel thirds or tenths), the function will attempt to identify the voice that follows (or preceeds) other, non-parallel voices at the interval P1, P4, P5, P8, or P12 (which are more typical). If neither of the parallel voices aligns with other parts in this way, the tool takes the upper-most voice as the real entry. The parallel voice is removed from the pattern data, but the name of the voice is stored in another column (Parallel Voice).
* **Total number of Non-Overlapping Entries** (in which the time interval between entries is in fact greater than the length of the entries themselves) and reports the count in a separate column.  Such 'medium' gaps, after all, are important to the extent that the successive entries do no produce any harmonic intervals with each other.

Settings:  Handling of **Unisons**, **Flexes**, and **Hidden Patterns**



* **Length of Ngram** will depend on the character and genre of your piece.  By default:  `melodic_ngram_length = 4`.
* **Combine unisons** in the melodies under comparison, or not (default is `combine_unisons = False`). This can be especially helpful when comparing different compositions based on the same model, since combining unisons can reveal commonalities that might otherwise be disguised by repetitions required for text declamation.
* **Limiting to Entries** (default is `limit_to_entries = True`) will produce a report of the most important points of imitation, since at least one entry in each of these will begin after a rest, fermata or section break.  Setting this to false will instead produce a great many Presentation Types, as what is essential the same Fuga (or other pattern) is detected not only from notes 1-5 of the melodies, but also 2-6, 3-7, and so on.  See the documentation in the ngrams tutorial.
* Allow **melodic flexes** among the matching soggetti included in any particular event. The flexing can be focused on the first interval with **head_flex** (default is `head_flex=1`), or permitted in any position with **body_flex** (default is `body_flex = 0`). The latter are determined via a side-by-side comparison of all soggetti: the threshold determines the cumulative difference among all successive intervals in each pair. The *presence of flexed entries* is reported in a separate column, and *all matching soggetti* (as determined by the threshold of flexing permitted) are reported in the soggetti column as a list.
* Option to find **hidden PENs and IDs among longer Fugas**. If the default (`include_hidden_types=False`) is changed to `True`, the method will instead report every possible PEN or ID that is 'hidden' within a longer Fuga.  Doing so can considerably extent the time it takes to produce the results, so use this feature carefully.

Typical Settings:

```python
piece.presentationTypes(limit_to_entries = True,
                        head_flex=1,
                        body_flex = 0,
                        include_hidden_types = False,
                        combine_unisons = True,
                        melodic_ngram_length = 4)
```
--- 

## Render Presentation Types as Score with Verovio

It is also possible to display the results of the Presentation Type classifier in the Notebook with Verovio. Each excerpt lasts from the first bar of the first entry through four bars after the start of the last entry.
The function also displays metadata about each excerpt, drawn from the presentation type results dataframe: piece ID, composer, title, measures, presentation type, beat of the bar in which the final tone is heard, and evaded status.


To use the function, pass the piece, cadence data frame, url of the piece, and mei_file name (all loaded in the first part of this notebook) as follows:
For a very simple displayt of presentation types using default settings:

```python
piece.verovioPtypes()
```

Otherwise you might want to filter the p_types or use custom settings. In this case first you will need to create the p_types list, either with custom settings (see the possibilities above) or filter them.

```python
p_types = piece.presentationTypes()
```


Then filter the results, and pass these to verovioPtypes():

```python
piece.verovioPtypes(p_types)
```

---

## How to Filter Results

Pandas offers many ways to filter any dataframe. One of the simplest involves checking a single column for exact or partial matches..

**Exact Match the Full Contents of a Cell**. For this we use the Python method `isin(['My_Exact_Pattern'])`, which returns True for any row in which the given columns is an exact match of the given string. If you run the following in a cell, you will see a long Series of True or False values:

```python
p_types["Presentation_Type"].isin(['PEN'])
```


We can in turn use this **Boolean Series to "mask" the entire dataframe** to show either all the rows for which the condition is True or False (and so we could show all the PEN's, or everything except the PEN's).


NOT the PENs includes the "~" to reverse the True and False values:

```python
p_types[~p_types["Presentation_Type"].isin(['PEN'])]
```


You can in fact pass several possible values in this way. But whether you are searching for one or more strings, they must be presented in the form of a Python list: ['My_Exact_Pattern_1', 'My_Exact_Pattern_2']. For instance, we could look for either PEN or ID:

```python
p_types[p_types["Presentation_Type"].isin(['PEN', 'ID'])]
```

    
Finally, note that a partial match would return no results:

```python
p_types[p_types["Presentation_Type"].isin(['P'])]
```

**Partial Match of Characters** is possible with `str.contains` method. This returns True for any row in which our search pattern is contained anywhere in the given cell. We could find any row in which the column "Presentation Type" contains "P" anywhere, and not just a complete exact match:

```python
p_types[p_types["Presentation_Type"].str.contains("P")]
```


In practice it's useful to give such searches a name of their own, and to make a .copy() of the dataframe so that you don't disturb the original results:

```python
pens_only = p_types[p_types["Presentation_Type"].str.contains("P")].copy()
```


Of course it would be more interesting to search for substrings in something like the Melodic Intervals column (which have various sets of values where we might want to know which patterns contain a M3 in the midst of some other series of entries). But for this we need to manage the data types (see below).

Comparisons: < or > can be useful for Fuga, as when you might want to find all the Fugas longer (or shorter) than a certain size. This code, for instance, will return a Boolean Series (True/False) of the column for Number_Entries:

```python
p_types['Number_Entries'] < 4
```


We can in turn use this to 'mask' the p_types dataframe itself (notice the two sets of brackets):

```python
p_types[p_types['Number_Entries'] < 4]
```

---

## More Filters:  Different Data Types Require Different Methods

Some fields (like composer or title) are simply strings of characters. But the data in Melodic_Entry_Intervals (for instance) are lists, and as such we need to convert these to strings before we can search within them.

This is done by applying a function to all items in the column. Here we map each item in the list to a 'string', then join those strings together as a single string, and update the column accordingly:

```python
p_types["Melodic_Entry_Intervals"] = p_types["Melodic_Entry_Intervals"].apply(lambda x: ', '.join(map(str, x))).copy()
```

Now we can use `str.contains()` to find subpatterns within the Melodic Entry Intervals:

```python
patterns_with_5 = p_types[p_types["Melodic_Entry_Intervals"].str.contains("5")].copy()
```


And now it is also possible to count the values of the sets of entries as strings:

```python
p_types["Melodic_Entry_Intervals"].value_counts().to_frame()
```


---
## Grouping Results to See the Big Picture

Groupby functions are a useful way to find sets of related items.

```python
pd.set_option('display.max_rows', None)
p_types["Mel_Ent"] = p_types['Melodic_Entry_Intervals'].apply(joiner)
p_types["Soggetti_Joined"] = p_types['Soggetti'].apply(joiner)
p_types.groupby(['Presentation_Type', 'Number_Entries', 'Soggetti_Joined']).size().reset_index(name='counts')
```

## Presentation Types with a Corpus

It is also possible to work with a corpus using the Presentation Type tool.  First build your corpus:

```python
corpus_list = []

prefix = 'https://crimproject.org/mei/'

piece_list = ['CRIM_Model_0019', 'CRIM_Mass_0019_1']
suffix = '.mei'
for piece in piece_list:
    url = prefix + piece + suffix
    corpus_list.append(url)
corpus_list
```

And then run the corpus using the Presentation Type method:

```python
# indicate the function
func = ImportedPiece.presentationTypes  # <- NB there are no parentheses here

#provide the kwargs
kwargs = {'limit_to_entries': True, 'head_flex' : 1,
                                    'body_flex' : 0,
                                    'include_hidden_types' : False,
                                    'combine_unisons' : True,
                                    'melodic_ngram_length' :  4}

#build a list of dataframes, one for each piece in the corpus
list_of_dfs = corpus.batch(func, kwargs)

#concatenate the list to a single dataframe
output = pd.concat(list_of_dfs)
```

Or more than one function, for instance in order to use chromatic melodic ngrams:

```python
func1 = ImportedPiece.Melodic
kwargs1 = {'kind' : 'c'}
#build a list of dataframes, one for each piece in the corpus
list_of_dfs = corpus.batch(func = func1, kwargs = kwargs1, metadata = False)

func2 = ImportedPiece.presentationTypes  # <- NB there are no parentheses here
#provide the kwargs
kwargs2 = {'limit_to_entries': True, 'head_flex' : 1, 'body_flex' : 0, 'include_hidden_types' : False, 'combine_unisons' : True,'melodic_ngram_length' : 4}

#build a list of dataframes, one for each piece in the corpus
list_of_dfs = corpus.batch(func = func1, kwargs = kwargs2, metadata = True)

#concatenate the list to a single dataframe
output = pd.concat(list_of_dfs)
```

See [01_Introduction](01_Introduction.md) for more detail on ways to **track errors during import of a corpus** or how to **replace staff names with staff numbers**.


---

## Sections in this guide

  * [01_Introduction_and_Corpus](/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](/02_Notes_Rests.md)
  * [03_Durations](/03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](/04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](/05_Detail_Index.md)
  * [06_Melodic_Intervals](/06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals](/07_Harmonic_Intervals.md)
  * [08_Contrapuntal_Modules](/08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](/09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](/10_Lyrics_Homorhythm.md)
  * [11_Cadences](/11_Cadences.md)
  * [12_Presentation_Types](/12_Presentation_Types.md)
  * [13_Musical_Examples_Verovio](/13_Musical_Examples_Verovio.md)
  * [14_Model_Finder](/14_Model_Finder.md)
  * [15_Visualizations_Summary](/15_Visualizations_Summary.md)
  * [16_Network_Graphs](/16_Network_Graphs.md)
  * [17_Python_Basics](/17_Python_Basics.md)
  * [18_Pandas_Basics](/18_Pandas_Basics.md)
  * [19_Music21_Basics](/18_Music21_Basics.md)
  * [99_Local_Installation](/99_Local_Installation.md)