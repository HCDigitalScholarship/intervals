# Intervals Onboarding Notes

There are a few key tools and concepts that we need to get started developing the Intervals program for CRIM. The skills you'll learn and/or strengthen here are extremely practical, and you're almost certain to draw on them time and again in your future work, even if the tools that you use aren't the same.

We'll take a look at the following:

1. Using Intervals 101
2. Basics of music21
3. Basics of using Pandas (indexing, slicing, simple methods, .concat)
4. Critical Pandas methods (basic math, .applymap, .apply, .shift)
5. Memoization on multiple levels

## Using Intervals 101

Let's write a script together to get started. I keep a testing script in the same folder as the main.py and main_objs.py files. This way we can import all the stuff we might need from them like this:

```
from main import *
import pandas as pd
```

Right there we have a small issue. If you're getting an error, you can try changing the first line of main.py to this: from main_objs import *
Please let me know if you have any issues, especially right here!

This tutorial is only going to show you how to use some of the newer things from main_objs, but there are other great methods too. There are pieces on the database that you can download like this:

```
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0017.mei'])
```

That created a CorpusBase object with one item (the score from the link). Let's call that piece the model, and get it out of the list:

```
model = corpus[0]
```

*Useful: corpus is incorrect, correct is actually `model = corpus.scores[0]`*

The new approach we're adopting in Intervals is to store a single type of data about the events in a piece of music, all in one pandas dataframe. Since we need lots of different types of information about a piece to run a query, we'll have lots of dataframes for each piece, as many as the query needs. Here are some examples: 

- df of all the notes and rests in the piece
- df of the durations of each note or rest
- df of the beat strength (metric position) of each note or rest
- df of the mensuration signs (time signatures) -> this one doesn't exist yet, so you'll build it for us :-)
- df of the 2-voice contrapuntal modules between all voice pairs

Here's an example of all the notes and rests from that piece:

```
model.getNoteRest()
```

              [Discantus] [Contratenor] [Tenor] [QuintaVox] [SextaVox] [Bassus]
       0.0             G4            G3    Rest        Rest       Rest     Rest
       4.0            NaN            G3     NaN         NaN        NaN      NaN
       7.0            NaN            A3     NaN         NaN        NaN      NaN
       8.0             G4            B3    Rest        Rest       Rest     Rest
       10.0           NaN            C4     NaN         NaN        NaN      NaN
       ...            ...           ...     ...         ...        ...      ...
       1480.0         NaN          None     NaN         NaN        NaN       G3
       1484.0         NaN           NaN     NaN          B3        NaN      NaN
       1488.0          B4           NaN     NaN         NaN        NaN      NaN
       1492.0         NaN           NaN      G3         NaN        NaN      NaN
       1496.0         NaN            G4     NaN         NaN        NaN      NaN

In each case, the row index is the time from the beginning of the piece, where 1 = the duration of a quarter note. The columnar index is made of either single voice names, or voice pairs. This means that reading down a given row is like reading a part (or voice pair) in a musical score left-to-right.

What about that line of ellipses in the middle? That's because the dataframe is pretty big, so pandas printed out a summary of it by default. What are those NaNs? It stands for not a number and it's the primary way that pandas shows that a cell is empty. In our case, when there is an event (note or rest) at a given time, every column must have something in its cell for that row. So if a voice doesn't have a real event, the NaN is used as a placeholder. For example, in the second row (row index 4.0), only the Contratenor has a new event, so it's new note is entered, and the rest of the cells in the row are filled with NaNs.

There are other "get..." methods. You can check them out by examining any imported piece, and just looking at the get___ methods.

*Useful: Can use this command to identify the methods that comes with an object*
```
dir(model)
```

**I'm only showing the user-facing ones here:**

```
['analyses', 'getBeatStrength', 'getDuration', 'getHarmonic', 'getMelodic', 'getNgrams', 'getNoteRest', 'regularize', 'score']
```

Let's take a look at the first seven rows of the melodic intervals. We can use .head(X) to only look at the first X rows.

```
mel1 = model.getMelodic().head(7)
mel1
```

          [Discantus] [Contratenor] [Tenor] [QuintaVox] [SextaVox] [Bassus]
    0.0          NaN           NaN    Rest        Rest       Rest     Rest
    4.0          NaN            P1     NaN         NaN        NaN      NaN
    7.0          NaN            M2     NaN         NaN        NaN      NaN
    8.0           P1            M2    Rest        Rest       Rest     Rest
    10.0         NaN            m2     NaN         NaN        NaN      NaN
    12.0         NaN           -P4     NaN         NaN        NaN      NaN
    14.0         NaN            P8     NaN         NaN        NaN      NaN

There are different ways to notate melodic intervals. Intervals supports 12 ways, and the default shown above is to show the interval quality with the letter (P, M, m, d, or a for perfect, major, minor, diminished, and augmented), followed by the size of the interval shown in steps where 1 is a unison, 2 is a second, etc. Rests are just given the string "Rest". What about all the other ways to display intervals? Let's consult the documentation on the getMelodic method. I tried to write decent documentation for user-facing functions:

```
print(model.getMelodic.__doc__)  # calling print makes this legible
```


        Return melodic intervals for all voice pairs. Each melodic interval
        is associated with the starting offset of the second note in the
        interval. If you want melodic intervals measured at a regular duration,
        do not pipe this methods result to the `unit` method. Instead,
        pass the desired regular durational interval as an integer or float as
        the `unit` parameter.

        :param str kind: use "q" (default) for diatonic intervals with quality,
            "d" for diatonic intervals without quality, "z" for zero-indexed
            diatonic intervals without quality (i.e. unison = 0, second = 1,
            etc.), or "c" for chromatic intervals. Only the first character is
            used, and it's case insensitive.
        :param bool directed: defaults to True which shows that the voice that
            is lower on the staff is a higher pitch than the voice that is
            higher on the staff. This is desginated with a "-" prefix.
        :param bool compound: whether to use compound (True, default) or simple
            (False) intervals. In the case of simple diatonic intervals, it
            simplifies to within the octave, so octaves don't get simplified to
            unisons. But for semitonal intervals, an interval of an octave
            (12 semitones) would does get simplified to a unison (0).
        :param int/float unit: regular durational interval at which to measure
            melodic intervals. See the documentation of the `unit` method for
            more about this.
        :returns: `pandas.DataFrame` of melodic intervals in each part

Cool, so we learned that there are kind, directed, compound, and unit settings. Let's not worry about the unit setting for now. Let's take a look at the first 7 rows of that same piece's melodic intervals, but let's do diatonic without quality, undirected, simple intervals.

`mel2 = model.getMelodic(kind='d', directed=False, compound=False).head(7)   # or just mel2 = model.getMelodic('d', False, False).head(7)
mel2`


              [Discantus] [Contratenor] [Tenor] [QuintaVox] [SextaVox] [Bassus]
       0.0          NaN           NaN    Rest        Rest       Rest     Rest
       4.0          NaN             1     NaN         NaN        NaN      NaN
       7.0          NaN             2     NaN         NaN        NaN      NaN
       8.0            1             2    Rest        Rest       Rest     Rest
       10.0         NaN             2     NaN         NaN        NaN      NaN
       12.0         NaN             4     NaN         NaN        NaN      NaN
       14.0         NaN             8     NaN         NaN        NaN      NaN


The idea with these get methods is that all needed set-up steps are automated for the user if the results are deterministic. If there are multiple ways to do an analysis, we always provide a default so that most methods can be called without passing any settings if you just want the defaults.

One last thing, let's look at a df where each column refers to a voice pair. Harmonic intervals are a straight-forward example:

```
har = model.getHarmonic().tail()
har
```

              [Bassus]_[SextaVox] [Bassus]_[QuintaVox] [Bassus]_[Tenor] [Bassus]_[Contratenor]  ... [QuintaVox]_[Discantus] [Tenor]_[Contratenor] [Tenor]_[Discantus] [Contratenor]_[Discantus]
       1242.0                 NaN                  NaN              NaN                    NaN  ...                      m3                   NaN                  m6                        P8
       1294.0                 NaN                  NaN              NaN                    NaN  ...                    Rest                   NaN                  P4                      Rest
       1449.0                 NaN                  NaN              NaN                    NaN  ...                      m7                   NaN                  m9                      Rest
       1450.0                 NaN                  NaN              NaN                    NaN  ...                      P5                   NaN                  m7                      Rest
       1488.0                 NaN                  NaN              NaN                    NaN  ...                      P8                   NaN                  M9                        A4

What is `.tail()`? That's just like` .head(),` but it shows the last X rows. Notice that if you don't enter a number, the default is to show 5 rows (same goes for .head). This time, there are too many columns to fit on the screen easily, so pandas has just shown the first and last few columns and the column of ellipses means that some are omitted. How many columns are there in all? Since harmonic intervals obtain between pairs of voices, it is the number of combinations, which is X * (X - 1) / 2 where X = the number of voices. So in this case, 6 * (6 - 1) / 2 = 15. Let's check by looking at all the columns of that dataframe:

       har.columns

       Index(['[Bassus]_[SextaVox]', '[Bassus]_[QuintaVox]', '[Bassus]_[Tenor]',
              '[Bassus]_[Contratenor]', '[Bassus]_[Discantus]',
              '[SextaVox]_[QuintaVox]', '[SextaVox]_[Tenor]',
              '[SextaVox]_[Contratenor]', '[SextaVox]_[Discantus]',
              '[QuintaVox]_[Tenor]', '[QuintaVox]_[Contratenor]',
              '[QuintaVox]_[Discantus]', '[Tenor]_[Contratenor]',
              '[Tenor]_[Discantus]', '[Contratenor]_[Discantus]'],
             dtype='object')

This returned a pandas index object of the column names. It's a little messy so let's use len to count them:

```
len(har.columns)

15
```



## Basics of music21

music21 is developed by Myke Cuthbert's lab at MIT. It's a great library with solid documentation so we don't actually have to talk about it much here. Just know that if there's something that you need to know about a note, or some other event in a piece, you can probably find it in one of the properties of the corresponding music21 object. We'll only really venture into these details as needed though.


## Pandas

##### Remember the two ways we looked at melodic intervals? Let's dig a little deeper into those two versions. The contratenor had the most non-NaN values, so let's compare the two versions of that part side-by-side. To do this, we'll index into the two dfs and get just the columns we want, and then concatenate them together in a new dataframe. In pandas, we can index by label or by index, and we can get a single value or a slice (generally multiple values). Let's start with indexing by label and getting a slice of the dataframe. Let's say we want the first 12 rows of just the contratenor. We use .loc[rows, columns] to slice a df by labels:

```
ct1 = mel1.loc[:12, '[Contratenor]']
ct1
```

       0.0     NaN
       4.0      P1
       7.0      M2
       8.0      M2
       10.0     m2
       12.0    -P4

What?! That's only 6 rows! That's because .loc is by LABEL, so :12 gave us all the rows up to the index 12. If we wanted the first twelve, we'd have to see what the twelfth index label is, and then use that in .loc.

```
twelfthIndexVal = mel1.index[12]  
twelfthIndexVal
```

`24.0`

```
ct1 = mel1.loc[:twelfthIndexVal, '[Contratenor]']
ct1
```

       0.0     NaN
       4.0      P1
       7.0      M2
       8.0      M2
       10.0     m2
       12.0    -P4
       14.0     P8
       16.0    NaN
       18.0    -M2
       19.0    -m2
       20.0     m2
       22.0    -m3
       24.0    NaN
       Name: [Contratenor], dtype: object

Since this is just 1 column, it technically gets returned as a pandas.Series. Notice how the "Name" property is what the column name used to be. Let's try indexing by integer instead. That's with .iloc. Remember, i is for integer. We'll do this for the second way we calculated melodic intervals. Note that the contratenor is the second column, so it's integer index is 1 since it's zero-indexed.

```
ct2 = mel2.iloc[:12, 1]
ct2
```


       0.0     NaN
       4.0       1
       7.0       2
       8.0       2
       10.0      2
       12.0      4
       14.0      8
       16.0    NaN
       18.0      2
       19.0      2
       20.0      2
       22.0      3
       Name: [Contratenor], dtype: object

Cool, now let's use .concat to put them together into new table so that they're easier to compare. You can read the docs on concat, but a little tricky thing tends to be the "axis" parameter. The default is usually 0 (rows) but for what we do we usually need it to be 1 (columns). No big deal if you have to try it both ways and see which one is what you meant to do.

```
combined_cts = pd.concat([ct1, ct2], axis=1)
combined_cts
```

            [Contratenor] [Contratenor]
       0.0            NaN           NaN
       4.0             P1             1
       7.0             M2             2
       8.0             M2             2
       10.0            m2             2
       12.0           -P4             4
       14.0            P8             8
       16.0           NaN           NaN
       18.0           -M2             2
       19.0           -m2             2
       20.0            m2             2
       22.0           -m3             3
       24.0           NaN           NaN

Ok, so now we can see how the labels are basically the same, but the one on the right doesn't show quality or direction. You can't see in this slice, but the right one also simplifies compound intervals greater than an octave down to within the octave.

When there were the other voices in the df, it made sense to have the placeholder NaNs. But now we might want to get rid of these rows where there are just NaNs.

```
combined_cts.dropna()
```


            [Contratenor] [Contratenor]
       4.0             P1             1
       7.0             M2             2
       8.0             M2             2
       10.0            m2             2
       12.0           -P4             4
       14.0            P8             8
       18.0           -M2             2
       19.0           -m2             2
       20.0            m2             2
       22.0           -m3             3

When working with pandas, you always have to keep in mind whether the things you do to a table are done in place or not. If you look at combined_cts again, you'll see the NaNs are still there.

       combined_cts

            [Contratenor] [Contratenor]
       0.0            NaN           NaN
       4.0             P1             1
       7.0             M2             2
       8.0             M2             2
       10.0            m2             2
       12.0           -P4             4
       14.0            P8             8
       16.0           NaN           NaN
       18.0           -M2             2
       19.0           -m2             2
       20.0            m2             2
       22.0           -m3             3
       24.0           NaN           NaN

If we wanted to do it in place, we can pass that argument:
       
       combined_cts.dropna(inplace=True)
       combined_cts
       
            [Contratenor] [Contratenor]
       4.0             P1             1
       7.0             M2             2
       8.0             M2             2
       10.0            m2             2
       12.0           -P4             4
       14.0            P8             8
       18.0           -M2             2
       19.0           -m2             2
       20.0            m2             2
       22.0           -m3             3

That's pretty good for now, more to come soon!