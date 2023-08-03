# Detail Index  

<!-- Add brief description and parameters at a glance -->

## Showing Measures and Beats:  `detailIndex()`

By default, CRIM Intervals dataframes display results according to the `offset` of each event, which appear as the **Index** for the given dataframe. Each increment of 1.0 corresponds to a single quarter note duration. Remember that the first offset will be 0.0, in accordance with Python series format.

But it is easy to include information about measures and beats (as well as offsets)in any combination. This can be done with the help of the `detailIndex()` function (which can also be abbreviated as `di()`. 

To use `detailIndex`, simply pass the dataframe from any function (which will have a list of offsets as the Index) to `detailIndex()``.  For instance:

    nr = piece.notes()
    piece.detailIndex(nr)

*or:*

    mel = piece.melodic()
    piece.detailIndex(mel)


<!-- add examples -->


Indeed, this method works with any dataframe (provided that it relates to a single piece already previously loaded, and provided that the passed dataframe has offsets as its index), and so it can be used to find the measure + beat reference for any subset of events that result from filtering or other algorithms.

<!-- Add examples for these -->

## Advanced Parameters for `detailIndex`

This function also has a number of parameters that can be adjusted according to need: 

    piece.detailIndex(df, measure = True, beat = True, offset = False, t_sig = False, sounding = False, progress = False, lowest = False, highest = False, _all = False)

At least **one** of either `measure`, `beat`, or `offset` must be `True`.  If more than one is `True`, the dataframe will have a multi-index.

#### Showing Measures

If `measure = True`, the dataframe includes **measure number** as an index column.

#### Showing Beats

If `beat = True`, the dataframe includes **beat number within the given measure** as an index column.

#### Hiding Offsets

`True` by default, if `offset = False` then the **offset will not be shown** in the dataframe.

#### Showing Time Signatures

If `t_sig = True`, the dataframe includes the **prevailing time signature** at each moment as an index column.

#### Showing Number of Active Voices

If `sounding = True` the dataframe includes an integer reporting the **total number of voices with a non-rest event** at this offset.

#### Relative Position ("Progress")

If `progress = True` the dataframe includes a decimal point (float) that reports the **relative position of the event in the piece** as whole (with the first note as `0.000000`) and the **onset** of the last note as `1.000000`. 

#### Lowest Sounding Tone

If `lowest = True` the dataframe includes a column listing the **lowest-sounding tone** at each offset (or beat).

#### Highest Sounding Tone

If `highest = True` the dataframe includes a column listing the **highest-sounding tone** at each offset (or beat).

#### Show All of the Above

As the name suggests, this sets all parameters as `True`.



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