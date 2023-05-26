# Pandas  

  * Pandas is a python library which allows for the creation and manipulation of DataFrames, which are two dimensional objects designed to store data. Below are a few of the many ways in which pandas DataFrames can be modified.  

## Counting and Sorting Intervals: General pandas operations  

  * The outputs of the `notes()`, `melodic()`, and `harmonic()` functions are all in the format of a pandas DataFrame. Therefore, they can each be manipulated by the functions built into pandas for this purpose. A cheat sheet of pandas DataFrame operations can be [found here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf). For the following examples, we can assume that some piece has been imported, and define a variable "mel" as the melodic intervals DataFrame for that piece:  

`mel = piece.melodic()`  

### Count the number of rows/find the size of the DataFrame  

  * This value will be equal to the number of beats in the piece, since it counts the number of offsets in the piece. The offsets will include every beat, even those without any voice sounding.  

> mel.count()  

### Rename columns in the DataFrame  

Executing the first line of code below will rename the column named '[Superious]' to 'Cantus'. More than one column name could be changed by adding more commands formatted as `'existingColumnName':'newColumnName'` within the curly brackets, separated by commas. Executing the second line of code below will rename the existing column named '[Superious]' to 'Canuts', and rename the existing column named 'Altus' to 'Alto'.  
> mel.rename(columns = {'[Superious]':'Cantus'})  
> mel.rename(columns = {'[Superious]':'Cantus', 'Altus':'Alto'})  

### Stack all the columns on top of each other to get one list of all the notes. [Flattens table into a single column, but still differentiates based on voice]  

> mel.stack()  

### Stack and count the number of unique values (which will tell us how many different intervals appear in this piece accross all voices, since they are all now in a single column)  

> mel.stack().nunique()  

### Count the number of times each interval appears in each part  

> mel.apply(pd.Series.value_counts).fillna(0).astype(int)  

# Application to melodic intervals:  

### Count and sort the intervals in a single voice part: 

> mel.apply(pd.Series.value_counts).fillna(0).astype(int).sort_values("[Superious]", ascending=False)  

  * Similarly to the note order created when [sorting pitches of notes](02_NotesAndRests.md#sorting-pitches), we can define an order of intervals as follows:  

`int_order = ["P1", "m2", "M2", "m3", "M3", "P4", "P5", "m6", "M6", "m7", "M7", "P8", "-m2", "-M2", "-m3", "-M3", "-P4", "-P5", "-m6", "-M6", "-m7", "-M7", "-P8"]`  

  * This `int_order` can now be used to sort the intervals from smallest to largest, ascending to descending:  

`mel = piece.melodic().fillna("-")`  
`mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()`  
`mel.rename(columns = {'index':'interval'}, inplace = True)`  
`mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)`
`mel = mel.sort_values(by = "interval").dropna().copy()`
`mel.reset_index()`  

## Charting intervals  

  * Similarly to how we created a histogram of frequency of pitch usage per voice, we can use the Matplot library to create a chart of the frequence of interval usage:  

> %matplotlib inline  
> int_order = ["P1", "m2", "-m2", "M2", "-M2", "m3", "-m3", "M3", "-M3", "P4", "-P4", "P5", "-P5", "m6", "-m6", "M6", "-M6", "m7", "-m7", "M7", "-M7", "P8", "-P8"]  
> mel = piece.melodic()  
> mel = mel.fillna("-")  
> mel = mel.apply(pd.Series.value_counts).fillna(0).astype(int).reset_index().copy()  
> mel.rename(columns = {'index':'interval'}, inplace = True)  
> mel['interval'] = pd.Categorical(mel["interval"], categories=int_order)  
> mel = mel.sort_values(by = "interval").dropna().copy()  
> voices = mel.columns.to_list()  
> md = piece.metadata  
> for key, value in md.items():  
>    print(key, ':', value)  

Graph options:  
> palette = sns.husl_palette(len(voices), l=.4)  
> sns.set(rc={'figure.figsize':(15,9)})  
> mel.set_index('interval').plot(kind='bar', stacked=True)  

# Application to pitches:  

### Sorting pitches  

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
  * [11_Pandas](11_Pandas.md)