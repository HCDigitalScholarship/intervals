# Finding Contrapuntal Modules (and Other Complex nGrams)

## What is a Contrapuntal Module?
A **contrapuntal module** (as formulated by our colleagues Julie Cumming and Peter Schubert) is a special kind **nGram** that describes the movement of any two voices:  

- a succession of **harmonic intervals** between the two voices (normally reprensented by the odd-numbered positions in the nGram), and
- a succession of **melodic intervals** made by the lower ('tenor') voice of the pair.

One might think that we would need to describe the melodic motion of *both voices* (and that is possible via an advanced setting of the CRIM Intervals `nGrams` method).  But in fact knowing the movement of the harmonic intervals and the melodic intervals of the lower voice alone is enough to fully describe the counterpoint (since we could infer the motion of the upper voice from the parts of the result).

Consider the following example from Josquin's *Ave Maria*:

![Alt text](images/modules.png)

The **red squares represent the harmonic intervals**; the **blue ovals represent the melodic motion in the lower part**.  Together they form a 3-gram, since there are three harmonic 'states'. The `n` parameter (explained below) allows us to find contrapuntal ngrams of any length. But '3' is the default.

## The `ngram()` Function in Detail

Default usage:  

    piece.ngrams()

You will probably want to fill the `na values`:

    piece.ngrams().fillna(')

![Alt text](images/modules_2.png)

It is also worth noting that by default the `ngrams` method uses `compound` intervals (melodic and harmonic alike). This is why the ngrams for the Cantus-Altus pair are different from the Tenor-Bassus pair (the Altus begins a 12th below the Cantus when it first enters; the Bassus is only a 5th below the Tenor). If you would like to use `simple` intervals instead (and thus find identical modules regardless of these octave differences) then see below.

## `ngrams()` Parameters
​
* **Length of nGrams**.  Remember that this will be number of the odd-numbered positions.  An `n=3` will in fact show 5 intervals (three harmonic surrounding two melodic).  Thus: `piece.ngrams(n=5)`. The default value is 3.
* **interval type** (such as diatonic, chromatic, etc, or in CRIM Intervals: d, c, z, or q): `piece.ngrams(interval_settings='c')`.  The default value is 'd'.
* The **'endpoint' of the offset reference** (whether the offset represents the start or end of the ngram).  Thus `piece.ngrams(offsets=
first)` or `piece.ngrams(offsets=last)`. 
* The **show_both** parameter, determines the results show only the melodic intervals of the lowest part (which is default), or both voices: `piece.ngrams(show_both=True)`.  This latter setting can be helpful in finding cadences.  But 

Thus a typical request:

    piece.ngrams(interval_settings='c', offsets='first', n=5).fillna('')


-----  

## Sections in this guide

  * [01_Introduction_and_Corpus](tutorial/01_Introduction_and_Corpus.md)
  * [02_Notes_Rests](tutorial/02_Notes_Rests.md)
  * [03_Durations](tutorial/03_Durations.md) 
  * [04_TimeSignatures_Beat_Strength](tutorial/04_TimeSignatures_Beat_Strength.md)
  * [05_Detail_Index](tutorial/05_Detail_Index.md)
  * [06_Melodic_Intervals](tutorial/06_Melodic_Intervals.md)
  * [07_Harmonic_Intervals](tutorial/07_Harmonic_Intervals.md)
  * [08_Contrapuntal_Modules](tutorial/08_Contrapuntal_Modules.md)
  * [09_Ngrams_Heat_Maps](tutorial/09_Ngrams_Heat_Maps.md)
  * [10_Lyrics_Homorhythm](tutorial/10_Lyrics_Homorhythm.md)
  * [11_Cadences](tutorial/11_Cadences.md)
  * [12_Presentation_Types](tutorial/12_Presentation_Types.md)
  * [13_Model_Finder](tutorial/13_Model_Finder.md)
  * [14_Visualizations_Summary](tutorial/14_Visualizations_Summary.md)
  * [15_Network_Graphs](tutorial/15_Network_Graphs.md)
  * [16_Python_Basics](tutorial/16_Python_Basics.md)
  * [17_Pandas_Basics](tutorial/17_Pandas_Basics.md)
  * [18_Music21_Basics](tutorial/18_Music21_Basics.md)