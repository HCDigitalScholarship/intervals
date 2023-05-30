# Detail Index  

## Showing Measures and Beats:  `detailIndex()`

By default, CRIM Intervals dataframes display results according to the `offset` of each event, which appear as the **Index** for the given dataframe. Each increment of 1.0 corresponds to a single quarter note duration. Remember that the first offset will be 0.0, in accordance with Python series format.

But it is easy to include information about measures and beats (as well as offsets)in any combination. This can be done with the help of the `detailIndex()` function (which can also be abbreviated as `di()`. 

To use `detailIndex`, simply pass the dataframe from any function (which will have a list of offsets as the Index) to `detailIndex()``.  For instance:

    nr = piece.notes()
    det = piece.detailIndex(nr)
    det
*or:*

    mel = piece.melodic()
    det = piece.detailIndex(mel)
    det

Indeed, this method works with any dataframe (provided that it relates to a single piece already previously loaded), and so it can be used to find the measure + beat reference for any subset of events that result from filtering or other algorithms.

## Advanced Parameters for `detailIndex`

This function also has a number of parameters that can be adjusted according to need: 

    piece.detailIndex(df, measure=True, beat=True, offset=False, t_sig=False, sounding=False, progress=False, lowest=False, highest=False, _all=False)

At least **one** of either `measure`, `beat`, or `offset` must be `True`.  If more than one is `True`, the dataframe will have a multi-index.

### The `measure` parameter

If `measure=True`, the dataframe includes **measure number** as an index column.

### The `beat` parameter

If `beat=True`, the dataframe includes **beat number within the given measure** as an index column.

### The `offset` parameter

`True` by default, if `offset=False` then the **offset will not be shown** in the dataframe.

### The `t_sig` parameter

If `t_sig=True`, the dataframe includes the **prevailing time signature** at each moment as an index column.

### The `sounding` parameter

If `sounding=True` the dataframe includes an integer reporting the **total number of voices with a non-rest event** at this offset.

### The `progress` parameter

If `progress=True` the dataframe includes a decimal point (float) that reports the **relative position of the event in the piece** as whole (with the first note as `0.000000`) and the **onset** of the last note as `1.000000`. 

### The `lowest` parameter

If `lowest=True` the dataframe includes a column listing the **lowest-sounding tone** at each offset (or beat).

### The `highest` parameter

If `highest=True` the dataframe includes a column listing the **highest-sounding tone** at each offset (or beat).

### The `_all` parameter

As the name suggests, this sets all parameters as `True`.

# [  ]

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