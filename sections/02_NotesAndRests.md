# Notes and Rests

## The `notes()` Function
  * After importing one or more pieces, the `notes()` function can be run to create a table of all of a piece's notes and rests, in order. The `notes()` function may be run in the following format:  

`piece.notes()`  
  * These notes will be printed in a table, where each new row represents the fact that any voice has changed its note. The left-most column is an index representing the offset of the change in note, where 0 represents the first note of the piece, and 1 unit of offset represents a single quarter note. Note that this index will not necessarily be regularly spaced.  
  * Each column of the `notes()` table represents a different voice of the pieces, as indicatd by the headings of the table
  * By default, printing `piece.notes()` will print the first and last five rows of the table. That is, the first and last 5 points in the piece at which any voice changes in note.
  * To control how many rows are printed;  

`piece.notes().head(20)` will print only the first 20 rows of the table, while  
`piece.notes().tail(20)` will print only the last 20 rows of the table.

## combineUnisons

  * A unison is when a new note is sounded, but the pitch remains the same (e.g. a half note C5 followed by a quarter note C5). the `notes()` function contains a parameter called combineUnisons, which defaults to False.  
  * When combineUnisons is set to true, any unisons will be treated as a continuation of the previous note, effectively adding a tie between those notes. As a result, the table output of the `notes()` function will not printing anything at the offset of the given note's repition.  
  * The combineUnisons parameter may be run as follows:  

`piece.notes(combineUnisons = True)` OR `piece.notes(combineUnisons = False)`  
  * The `head()` function can be combined with `notes(combineUnisons = True/False)` as follows:  

`whole_piece = piece.notes(combineUnisons = False)`  
`whole_piece.head(20)`  
Or, more directly:  
`piece.notes(combineUnisons = False).head(20)`  

  * Sometimes, declaring variables, such as in the first example, may be more useful, since it allows you to reference a specific condition of the piece more easily than adding `combineUnisons = True/False` to the function every time you want to reference that piece with those paremters. This type of variable declaration with specific parameters is useful in many instances not limited to applications of the CRIM Intervals library to increase your code's efficiency and prevent unnecessariily repeatedly declaring the same statement.

## combineRests

  * The combineRests parameter operates similarly to the combineUnisons parameter, where any rests in the piece that does not preceed the first non-rest note are combined with neighboring rests, such as three whole rest measures in a row.
  * By default, the combineRests parameter of the `notes()` function is set to True, and can similarly be toggled by the following code:  

`piece.notes(combineRests = True/False)`  
Or, once again,
`piece_seperate_rests = piece.notes(combineRests = False)`  
`piece_seperate_rests.head(20)`  
Additionally, the `combineRests()` and `combineUnisons()` parameters may be changed simultaneously as follows:  
`piece.notes(combineRests = False, combineUnisons = True).head(20)`  

## Removing "NaN"

  * If a note changes in one voice but not another, then a row will be created in the table only partially filled. This is because while the table will attempt to populate the change in note for all voices, but subsequent beats of a note or rest (for example, beats 2, 3, and 4 of a whole rest) do not appear for the note or rest's entire duration, only at its first instance.
  * These empty slots, which we now see as representing some note or rest being held, are therefore printed as "NaN", which stands for "Not a Number"
  * To decrease the visual clutter of the table, these "NaN" outputs can be replaced with the `fillna()` function, which is used as follows:  

`piece.notes().fillna('')`

  * The `fillna()` function accepts a parameter which, in quotes, represents the text which will replace the "NaN" elements of the `notes()` output table. This field may contain empty quotes, as shown above, or another symbol such as '-':  

`piece.notes().fillna('-')`  

  * Once again, the amount of rows shown by this function can be controlled by adding a `.head()` function to the line, which may be placed either before or after the `fillna('')` function. For example, both of the following lines will each output the first 20 lines of the give piece, with all "NaN" elements replace by a dash:  

`piece.notes().fillna('-').head(20)`  
`piece.notes.head(20).fillna('-')`  

## Counting, Sorting, and Graphing Notes

  * Since the output of the `notes()` function is in the form of a pandas dataframe, all of the functions applicable to dataframes in general apply here as well. A cheat sheet of pandas dataframe functions can be [found here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf). These operations include the following:  

First, let's create a variable to represent the dataframe for our piece:  
`df = piece.notes()`  

> Count the number of rows in the dataframe (table)

`df.count()`  

> Rename a column in the dataframe (table)

`df.rename(columns = {'[Superious]':'Cantus'}, inplace = False)`

  * More detail about `dataframe.rename()` can be [found here](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html?highlight=rename#pandas.DataFrame.rename).  

> Stack all columns on top of each other to get one list of all notes  

`df.stack()`  

> Stack all columns, and count unique tones in the piece  

`df.stack().nunique()`  

> Count the number of each note in each voice part  

`df.apply(pd.Series.value_counts).fillna(0).astype(int)`  

> Count the number of each note in a single voice part, sorted in descending order  

`df.apply(pd.Series.value_counts).fillna(0).astype(int).sort_values(by = df.columns[0], ascending = False)`  

`sort_values()` can be modified as follows:  
  * Parameter `ascending` (default = True) can be changed to False  
  * Parameter `by` must be set as equal to the name of the column by which the table will be sorted. For example, to sort the entire table such that the first column appears in descending order, set `by = df.columns[0]` and `ascending = False` as shown above. The value for `by` can be set with either `df.columns[index_value]` or the actual text of the column's name itself. `index_value` may be any number from 0 to the number of voices in the table - 1, corresponding to the first and last voice in the piece, respectively. To index from the last voice rather than the first, use -1 as the last index, -2 as the second to last index, etc.  

## Sorting pitches  

We Previously saw how to sort the columns by the **counts** of the pitches in a particular voice.  
But we can also declare a **sort order** for the pitches themselves, then organize the entire data frame in that sequence.  This will show the voice ranges of each part.  
We first create a list of the pitches in order (from low to high, in this case).  Note that music21 (and thus CRIM Intervals) represents **B-flat** as **B-**.  **C-sharp** is **C#**.  


  * First, set the order of pitches:  

`pitch_order = ['E-2', 'E2', 'F2', 'F#2', 'G2', 'A2', 'B-2', 'B2', 
               'C3', 'C#3', 'D3', 'E-3','E3', 'F3', 'F#3', 'G3', 'G#3','A3', 'B-3','B3',
               'C4', 'C#4','D4', 'E-4', 'E4', 'F4', 'F#4','G4', 'A4', 'B-4', 'B4',
               'C5', 'C#5','D5', 'E-5','E5', 'F5', 'F#5', 'G5', 'A5', 'B-5', 'B5']`  

`df = piece.notes().fillna('-')`  
`df = nr.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()`  
`df.rename(columns = {'index':'pitch'}, inplace = True)`  
`df['pitch'] = pd.Categorial(df["pitch"], categories = pitch_order)`  
`df = df.sort_values(by = "pitch").dropna().copy()`  

  * Now, running `df` will print a dataframe where every row is a pitch, sorted in ascending order, and each column represents a voice part. Each element of the table itself is the number of times the voice in its column sounded the pitch in its row.  


### Graphing pitches  

  * Various python libraries exist to help create graphs and charts. Below is an example of how we can use Matplot to create a historgram of the of how many times each voice sounded each pitch:  

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
  * [05_Lyrics](05_Lyrics.md)
  * [06_Durations](06_Durations.md)
  * [07_N-grams](07_Ngrams.md)
  * [08_Time-Signatures](08_TimeSignatures.md)
  * [09_DetailIndex](09_DetailIndex.md)
  * [10_Cadences](10_Cadences.md)
  * [11_Item](link.to.item)