# Pandas  

Pandas is a Python library which allows for the creation and manipulation of DataFrames, which are two dimensional objects designed to store data. Below are a few of the many ways in which pandas DataFrames can be modified, filtered, or transformed. 

## Counting and Sorting Intervals: General Pandas Operations  

The outputs of the `notes()`, `melodic()`, and `harmonic()` functions are all in the format of a pandas DataFrame. Therefore, they can each be manipulated by the functions built into pandas for this purpose. A cheat sheet of pandas DataFrame operations can be [found here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf). For the following examples, we can assume that some piece has been imported, and define a variable "mel" as the melodic intervals DataFrame for that piece:  

    mel = piece.melodic()  

### Working with Rows

Dataframes can be **long**, since they will have a row for every event in the composition (beats and subbeats alike).  By default Pandas displays dataframes in an abbreviated view consisting of the first five and last five rows. The last row will be included, so it is easy to see just how long the results are!

But it is possible to show various slices and segments (see the cheatsheet linked above for many examples), such as:

    piece.notes().head(20)
    piece.notes().tail(20)
    piece.notes().sample(20)

`df.loc[]` and `df.iloc[]` have two different meanings! The first of these selects some range of *specific index values* (`df.loc[10:20]` would in this case return a slice of the frame 'df' where the actual offsets are between 10 (inclusive) and 20 (exclusive).

    nr = piece.notes()
    nr.loc[10:20]

On the other hand, the `iloc[]` method with Pandas will select the rows according to their *position in the index* rather than the index values.  So this would report the 10th until the 19th row of the frame for notes and rests:

    nr = piece.notes()
    nr.iloc[10:20]

#### Examples from CRIM Intervals:  Filter df of Notes according to Measure or Beat Strength

The `piece.measures()` function returns a df that shows were each new measure begins.  The index of this df is saved as a list, which in turn is tested against the index of the df for notes to produce a Boolean series: `nr.index.isin(measure_starts)`.  This Boolean is then passed to nr.loc to yield the final dataframe:  `nr2 = nr.loc[nr.index.isin(measure_starts)]`.

    #df of measures (that is, where each starts)
    ms = piece.measures()
    #index of that df as list
    measure_starts = ms.index.to_list()
    #df of notes and rests
    nr = piece.notes()
    #filter nr to show only those offsets (=index) that are in the list just made
    notes_at_start_of_measures = nr.loc[nr.index.isin(measure_starts)]
    notes_at_start_of_measures

### Working With Columns  


#### Show Column Names

A list of the columns could be useful as a way to list the voice parts in a composition:

    voices = piece.notes().columns.to_list()
    voices
    #output as follows
    ['Superius', 'Contratenor', 'PrimusTenor', 'SecundusTenor', 'Bassus']


#### Rename Columns
Perhaps in turn it might be necessary to rename some or all of the columns.  This could be done by passing a Python 'dictionary' in which the old and new voice (column) names are given as `key : value` pairs inside curved braces, separated by commas: `{old_col_1_name : new_col_1_name, old_col_2_name : new_col_2_name }`. It is only necessary to provide dictionaries for the columns to be renamed; the others can be left out. For instance:

    mel.rename(columns = {'Superius':'Soprano', 'Contratenor':'Alto'})


#### Selected Columns in New Dataframe

**By Name with `loc` Method**

Image that only the "PrimusTenor" and "SecundusTenor" are needed in a new dataframe.  These can be selected with `loc` by name:

    nr = piece.notes()
    nr2 = nr.loc[:, ['PrimusTenor', 'SecundusTenor']]

Note that the information about the columns to select appears to the right of the comma. In this case the `:` to the left of the column means that *all rows* are returned.  But these could be specified, too, as shown above.

**By Position with `iloc` Method**

It is also possible to select columns on the basis of their *position* in the dataframe (the first is '0', the last is '-1'). To return just the top and bottom voices (Superius and Bassus from the list above), use the `iloc` function:

    nr = piece.notes()
    nr2 = nr.iloc[:, [0, -1]]

Note that `iloc` method allows selection of either rows or columns (or both). 

Note that the information about the columns to select appears to the right of the comma. In this case the `:` to the left of the column means that *all rows* are returned.  But these could be specified, too, as shown above.

Pandas provides several other ways to rename, select or reorganize columns. See the cheat sheet above.

### Counting and Sorting

#### Counting Notes
A count of the *rows* of the dataframe will be in effect a count of the number of offsets.  Pass the entire function to the Python `len` method, for instance:

    len(piece.notes())

But it is also possible to count the number of **notes** in each voice (column):

    nr = piece.notes() 
    nr.count()
    #output as follows:
    Superius         388
    Contratenor      448
    PrimusTenor      373
    SecundusTenor    377
    Bassus           337

Or `stack()` all the columns on top of each other, then report the **total number of unique values** (that is, a count of the unique pitches):

    nr.stack().nunique()


#### Sorting Notes

Count the notes in each voice part, then *sort the df alphabetically by note* (which is the index in this case.  Since music21 names the notes by pitch class and octave, the result is a table from low to high of all the tones in the piece:

    nr.apply(pd.Series.value_counts).fillna(0).astype(int)

Or sorted by the *counts in a particular voice* (here the NA's are filled with 0 [zero]. To select a different column, change `nr.columns[0]` to a different number. To sort them in descending order, try `ascending = True`.

    nr.apply(pd.Series.value_counts).fillna(0).astype(int).sort_values(by = nr.columns[0], ascending = False)

But it is also possible to *declare a sort order for the pitches* , then organize the entire data frame in that sequence. This will show the voice ranges of each part.

First, create a list of the pitches in order (from low to high, in this case). Note that music21 (and thus CRIM Intervals) represents B-flat as `B-`. C-sharp is `C#`.

    pitch_order = ['E-2', 'E2', 'F2', 'F#2', 'G2', 'A2', 'B-2', 'B2', 
               'C3', 'C#3', 'D3', 'E-3','E3', 'F3', 'F#3', 'G3', 'G#3','A3', 'B-3','B3',
               'C4', 'C#4','D4', 'E-4', 'E4', 'F4', 'F#4','G4', 'A4', 'B-4', 'B4',
               'C5', 'C#5','D5', 'E-5','E5', 'F5', 'F#5', 'G5', 'A5', 'B-5', 'B5']

Then, create a dataframe corresponding to our piece, and sort it by pitches, as shown:

    #find notes, fill NA's
    df = piece.notes().fillna('-') 
    #count the values, fill NA's and make a copy for safety
    df = nr.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy() 
    #rename the index as 'pitch'
    df.rename(columns = {'index':'pitch'}, inplace = True) 
    #assign the order from pitch_order above
    df['pitch'] = pd.Categorial(df["pitch"], categories = pitch_order)
    #sort values, drop NA's, and copy 
    df = df.sort_values(by = "pitch").dropna().copy()
    #display results as df
    df


#### Counting Melodic Intervals

The same approach could be applied to melodic intervals.  The count of melodic intervals:

    len(piece.melodic())

Melodic intervals in each voice:

    mel = piece.melodic() 
    mel.count()
  
And so on, as above. Remember that it is also possible to specify various parameters for the `melodic()` function, thus reporting different kinds of intervals, qualities, and so on.

#### Sorting Melodic Intervals  

Similar to the note order created above, first define an order of intervals as follows:  

    int_order = ["P1", "m2", "M2", "m3", "M3", "P4", "P5", "m6", "M6", "m7", "M7", "P8", "-m2", "-M2", "-m3", "-M3", "-P4", "-P5", "-m6", "-M6", "-m7", "-M7", "-P8"]  

This `int_order` can now be used to sort the intervals from smallest to largest, ascending to descending:

    #df of melodic intervals, NA's filled
    mel = piece.melodic().fillna("-") 
    #counting the intervals, NA's filled as 0, and copy the df to avoid problems
    mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()
    #rename the index as 'interval' 
    mel.rename(columns = {'index':'interval'}, inplace = True) 
    #map each interval to the order specified in the "int_order" list above
    mel['interval'] = pd.Categorical(mel["interval"], categories = int_order)
    #sort the results, remove NA's, and make a copy to avoid problems
    mel = mel.sort_values(by = "interval").dropna().copy()
    #reset the index and display
    mel.reset_index() 





-----

## Sections in this guide

  * [01_Introduction_and_Corpus](01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](02_Notes_Rests.md)
  * [03_Durations](03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](04_TimeSignatures_Beat_Strength.md)
  * [05_DetailIndex](05_DetailIndex.md)
  * [06_MelodicIntervals](06_MelodicIntervals.md)
  * [07_HarmonicIntervals](07_HarmonicIntervals.md)
  * [08_Contrapuntal_Modules](08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](10_Lyrics_Homorhythm.md)
  * [11_Cadences](11_Cadences.md)
  * [12_Presentation_Types](12_Presentation_Types.md)
  * [13_Model_Finder](13_Model_Finder.md)
  * [14_Visualizations_Summary](14_Visualizations_Summary.md)
  * [15_Network_Graphs](15_Network_Graphs.md)
  * [16_Python_Basics](16_Python_Basics.md)
  * [17_Pandas_Basics](17_Pandas_Basics.md)