# Notes and Rests

## The `notes()` Function
  * After importing one or more pieces, the `notes()` function can be run to create a table of all of a piece's notes and rests, in order. The `notes()` function may be run in the following format:  

`piece.notes()`  
  * These notes will be printed in a table, where each new row represents the fact that any voice has changed its note. The left-most column is an index representing the offset of the change in note, where 0 represents the first note of the piece, and 1 unit of offset represents a single quarter note. Note that this index will not necessarily be regularly spaced.  
  * Each column of the `notes()` table represents a different voice of the pieces, as indicated by the headings of the table
  * By default, printing `piece.notes()` will print the first and last five rows of the table. That is, the first and last 5 points in the piece at which any voice changes in note.
  * To control how many rows are printed;  

`piece.notes().head(20)` will print only the first 20 rows of the table, while  
`piece.notes().tail(20)` will print only the last 20 rows of the table.  

## `notes()` parameters  

## combineUnisons

  * A unison is when a new note is sounded, but the pitch remains the same (e.g. a C5 half note followed by a C5 quarter note). the `notes()` function contains a parameter called `combineUnisons`, which defaults to `False`.  
  * When `combineUnisons` is set to `True`, any unisons will be treated as a continuation of the previous note, effectively adding a tie between those notes. As a result, the table output of the `notes()` function will not printing anything at the offset of the given note's repititon.  
  * The combineUnisons parameter may be run as follows:  

`piece.notes(combineUnisons = True)` OR `piece.notes(combineUnisons = False)` (Default)  
  * The `head()` function can be combined with `notes(combineUnisons = True/False)` as follows:  

`whole_piece = piece.notes(combineUnisons = True)`  
`whole_piece.head(20)`  
Or, more directly:  
`piece.notes(combineUnisons = True).head(20)`  

  * Beyond applications of the CRIM Intervals library, it is often more efficient in code to declare a variable, and then perform functions on that variable, rather than performing multiple functions simultaneously. This will prevent unnecessary repetitions of the same statement, saving memory as well as time.

## combineRests

  * The combineRests parameter operates similarly to the combineUnisons parameter, where any rests in the piece that does not preceed the first non-rest note are combined with neighboring rests (e.g. three whole rest measures in a row).
  * By default, the combineRests parameter of the `notes()` function is set to `True`. Note that this is different from the default state of the `combineUnisons` parameter. This can be controlled similarly to the `combineUnison` parameter by the following code:  

`piece.notes(combineRests = False)`  
Or, once again,  
`piece_seperate_rests = piece.notes(combineRests = False)`  
`piece_seperate_rests.head(20)`  
  
Additionally, the `combineRests()` and `combineUnisons()` parameters may be changed simultaneously as follows:  
`piece.notes(combineRests = False, combineUnisons = True).head(20)`  

## Removing "NaN"

  * If a note changes in one voice but not another, then a row will be created in the table only partially filled. This is because  the table will attempt to populate a change in note for all of the voices in the piece, but subsequent beats of a note or rest (e.g. beats 2, 3, and 4 of a whole rest) do not appear, only the first instance of the note's creation does.
  * These empty slots, which we now understand to represent a note or rest being *held* rather than ommitted are therefore printed as "NaN", which stands for "Not a Number", since the code is unable to find a value for the "missing" note.
  * To decrease the visual clutter of the table, these "NaN" outputs can be replaced with the `fillna()` function, which is used as follows:  

`piece.notes().fillna('')`

  * The `fillna()` function accepts a parameter for the text which will replace the "NaN" elements of the `notes()` output table. This field may contain empty quotes, as shown above, or another symbol such as '-':  

`piece.notes().fillna('-')`  

  * Note that the parameter of the `fillna()` function is not necessarily a text, as any valid data could be provided, such as an integer value in place of the text field. Later, we will see how it can be useful to perform the function as written below, but in many cases, it is simply most optimal to pass either an empty quote string, a dash, or some other discrete symbol to the `fillna()` function for the benefit of a human reader.  

`piece.notes().fillna(0)`  

  * Once again, the amount of rows shown by this function can be modified by adding a `.head()` function to the line, which may be placed either before or after the `fillna('')` function. For example, both of the following lines will each output the first 20 lines of the give piece, with all "NaN" elements replace by a dash:  

`piece.notes().fillna('-').head(20)`  
`piece.notes.head(20).fillna('-')`  

  * Note that this property is not true of all functions depending on their properties, so take care to order functions correctly when applying multiple functions to an object simultaneously. In general, it is good form to include the `head()` function as the last function in the line.  

## Counting, Sorting, and Graphing Notes

  * Since the output of the `notes()` function is in the form of a pandas DataFrame, all of the functions applicable to DataFrames in general apply here as well. A cheat sheet of pandas DataFrame functions can be [found here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf). These operations include the following:  

First, let's create a variable to represent the DataFrame for our piece:  
> df = piece.notes()  

### Count the number of rows in the DataFrame (table)

> df.count()  

### Rename a column in the DataFrame (table)

> df.rename(columns = {'[Superious]':'Cantus'}, inplace = False)

  * More detail about `DataFrame.rename()` can be [found here](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html?highlight=rename#pandas.DataFrame.rename).  

### Stack all columns on top of each other to get one list of all notes  

> df.stack()  

### Stack all columns, and count unique tones in the piece  

> df.stack().nunique()  

### Count the number of each note in each voice part  

> df.apply(pd.Series.value_counts).fillna(0).astype(int)  

### Count the number of each note in a single voice part, sorted in descending order  

> df.apply(pd.Series.value_counts).fillna(0).astype(int).sort_values(by = df.columns[0], ascending = False)  

`sort_values()` can be modified as follows:  
  * Parameter `ascending` (default = True) can be changed to False  
  * Parameter `by` must be set equal to the name of the column by which the table will be sorted. For example, to sort the entire table such that the first column appears in descending order, set `by = df.columns[0]` and `ascending = False` as shown above. The value for `by` can be set with either `df.columns[index_value]` or the actual text of the column's name itself. `index_value` may be any number from 0 to 1 less than the number of voices in the table, values which corresponding to the first and last voice in the piece, respectively. Index values progress forward starting from the first voice as 0, 1, 2 ... N, while index values progress backwards starting from the last voice as -1, -2, -3 ... -(N + 1).  

## Sorting pitches  

We previously saw how to sort the pitches by their frequency in a particular voice. We are also able to declare a **sort order** for the pitches themselves, then organize the entire data frame in that sequence to show the voice ranges of each part. This will providing values of how many times each voice sounded a specific pitch, in a table sorted by pitch order rather than by any voice's requency of pitches.  
First, create a list of the pitches in order (in this case, from the lowest note to the highest).  Note that music21 (and thus CRIM Intervals) represents **B-flat** as **B-**.  **C-sharp** is **C#**.  


  * First, set the order of pitches:  

`pitch_order = ['E-2', 'E2', 'F2', 'F#2', 'G2', 'A2', 'B-2', 'B2', 
               'C3', 'C#3', 'D3', 'E-3','E3', 'F3', 'F#3', 'G3', 'G#3','A3', 'B-3','B3',
               'C4', 'C#4','D4', 'E-4', 'E4', 'F4', 'F#4','G4', 'A4', 'B-4', 'B4',
               'C5', 'C#5','D5', 'E-5','E5', 'F5', 'F#5', 'G5', 'A5', 'B-5', 'B5']`  

  * Then, create a dataframe corresponding to our piece, and sort it by pitches, as shown:  

`df = piece.notes().fillna('-')`  
`df = nr.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()`  
`df.rename(columns = {'index':'pitch'}, inplace = True)`  
`df['pitch'] = pd.Categorial(df["pitch"], categories = pitch_order)`  
`df = df.sort_values(by = "pitch").dropna().copy()`  

  * Now, running `df` as a command will print a DataFrame where every row is a pitch, sorted in ascending order, and each column represents a voice part. Each element of the table itself is the number of times the voice in its column sounded the pitch in its row.  


### Graphing pitches  

  * Various python libraries exist to help create graphs and charts. Below is an example of how we might use Matplot to create a historgram of the of how many times each voice sounded each pitch:  

`%matplotlib inline`  
`nr = piece.notes().fillna('-')`  
`nr = nr.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()`  
`nr.rename(columns = {'index':'pitch'}, inplace = True)`  
`nr['pitch'] = pd.Categorical(nr["pitch"], categories=pitch_order)`  
`nr = nr.sort_values(by = "pitch").dropna().copy()`  
`voices = nr.columns.to_list()`  
`palette = sns.husl_palette(len(voices), l=.4)`  
`md = piece.metadata`  
`for key, value in md.items():`  
`    print(key, ':', value)`  
`sns.set(rc={'figure.figsize':(15,9)})`  
`nr.set_index('pitch').plot(kind='bar', stacked=True)`  


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
  * [11_Item](link.to.item)