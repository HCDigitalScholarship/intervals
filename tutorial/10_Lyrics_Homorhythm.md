# Lyrics and Homorhythm

CRIM intervals can find all of the text syllables associated with notes in each piece. The `lyrics()` function can, moreover, be used with many other CRIM Intervals functions, such as `ngrams()`, `durations()`, and so on. The `homorhythm()`, for instance, compares ngrams of lyrics and durations to predict passages where two or more voices are declaiming the same text in the same rhythms. 

The `piece.lyrics()` function does not take any parameters.  But `piece.homorhythm()` does:

* `ngram_length` (which is 4 by default, and determines the number of durations and syllables that must be in common among the voices in order to be marked as HR);

* `full_hr` (which is True by default).  When `full_hr = True` the method will find any passage where *all active voices* share the same durational ngram and syllables; if `full_hr = False` the method will find *any passage where even two voices share the same durational ngram and the same syllables*. 

See more below for details on the meaning of the columns reported by `piece.homorhythm()`

## The `lyrics()` Function  

By default, applying the `lyrics()` function to a piece will generate a DataFrame containing the lyrics at each relevant offset, for each voice part.  

    lyrics = piece.lyrics()  

As opposed to integers or floats, the DataFrame produced by the `lyrics()` function will be in the form of **text strings**. Also unlike other functions, the `lyrics()` function has no parameters, and therefore can only be executed in one way. Its usage, however, can still be varied based on the other functions with which it is combined. Note, for instance, that piece.`piece.ngrams(df = Piece.lyrics())` will result in a dataframe that contains cells of *tuples*, just as the ngrams() function will for any other musical feature.

## Alphabetical Characters Only?  How to Remove Punctuation Marks from Results

Particularly for projects that aim to assemble lyric syllables into words (or at least ngrams), it might be useful to remove from the initial results the various dashes, hyphens, and punctuation marks from the individual cells before assembling them into ngrams. Fortunately Pandas and Python have a convenient *applymap* method that does this with one line of code: 

    lyrics = piece.lyrics()
    lyrics_cleaned = lyrics.applymap(alpha_only)

## Lyric Ngrams 

To find N-grams of length 5 (groupings of 5 consectuive syllables found in the lyrics of a piece):

    # define length of ngrams
    _n = 5
    # get the lyrics
    lyr = piece.lyrics()
    # get ngrams of lyrics
    piece.ngrams(df = lyr, n = 5, entries = True)

Or, more succinctly:

    n = _n
    piece.ngrams(df = Piece.lyrics(), n = _N)

## Cleaning Up Lyrics:  Dealing with Punctuation, Hyphens, etc

**Lyric ngrams without punctuation and hyphens:**

    #define length of ngrams
    _n = 5
    #get the lyrics
    lyr = piece.lyrics()
    #clean the lyrics
    lyrics_cleaned = lyrics.applymap(alpha_only)
    # get ngrams of cleaned lyrics
    piece.ngrams(df = lyrics_cleaned, n = _n)

**Lyric ngrams, cleaned, entries only:**

    #define length of ngrams
    _n = 5
    #get the lyrics
    lyr = piece.lyrics()
    #clean the lyrics
    lyrics_cleaned = lyrics.applymap(alpha_only)
    # get ngrams of cleaned lyrics, now with entries = True (see ngrams documentation for more detail)
    piece.ngrams(df = lyrics_cleaned, n = _n, entries = True)

**Lyric ngrams as strings:  avoiding "Tuple Trouble"**

Remember that the ngrams will be expressed as *tuples of syllables*.  If the plan is to match or search for certain collections of syllables, these will need be transformed as strings. Use a *convertTuple* function, like this:

    def convertTuple(tup):
    out = ""
    if isinstance(tup, tuple):
        out = ', '.join(tup)
    return out

Then use `applymap()` on the entire dataframe of ngrams:

    #select length of ngrams
    n = _n
    #make the ngrams
    lyric_ngs = piece.ngrams(df = Piece.lyrics(), n = _N)
    #convert them to tuples
    lyric_ngs_strings = lyric_ngs.applymap(convertTuple)

Or more succinctly:

    n = _n
    #make the ngrams
    lyric_ngs_strings = piece.ngrams(df = Piece.lyrics(), n = _N).applymap(convertTuple)

## Predicting Homorhythmic Passages:  `piece.homorhythm()`

The `piece.homorhythm()` function identifies passages in which more than one voice has the *same durational ngrams* and the *same lyrical ngrams* at the *same time*. The method follows various stages:

* gets durational ngrams, and finds passages in which these are the same in more than two voices at a given offsets
* gets lyric ngrams, and finds passages in which the same sequence of two syllables are heard successively in at least two voices at the same offsets.
* checks the number of active voices (in order to count the number moving on coordinated homorhythm)

### What the `piece.homorhythm()` Columns Mean

The results of `piece.verovioHomorhythm()` contain a multiIndex as well as several columns, as explained above:

* **Measures, Beats, and Offsets** (the multiIndex)
* **active_voices**
* **number_dur_ngrams**
* **hr_voices**
* one column for each voice part in the original piece, expressed in tuples of syllables.  The length of this tuple is determined by the *ngram_length* setting
* **syllable_set** is a list of the lyric ngrams (tuples) in this particular passage; the *length of this set* determines the kind of HR in the passage. For example, if *len(set(syllable_set))* = 1 then all the active voices are singing the same text; this value in turn determined the following column
* **count_lyr_ngrams** is the number of lyric ngrams in this particular passage, determined by *len(set(syllable_set))*
* **active_syll_voices** is the number of voices actively singing in this passage, since some parts might have rests (and thus no syllables)
* **voice_match** is a boolean value determined by the *count_lyr_ngrams*; should always be True for any HR results

### Homorhythm Parameters

Users can supply either of two arguments:

* `ngram_length` (which is 4 by default, and determines the number of durations and syllables that must be in common among the voices in order to be marked as HR);

* `full_hr` (which is True by default).  When `full_hr = True` the method will find any passage where *all active voices* share the same durational ngram and syllables; if `full_hr = False` the method will find *any passage where even two voices share the same durational ngram and the same syllables*.

### Typical Use of 'piece.homorhythm()`

    piece.homorhythm()
    
Or 

    piece.homorhythm(ngram_length = 4, full_hr = True)

### Filtering Homorhythm Results:  Voices, lists, and more

As a first step it will necessary to `fillna()`:

Note that it is probably a good idea to `fillna('')`:

    hr = piece.homorhythm(ngram_length = 4, full_hr = True).fillna('')

**Search for Lyrics**

If the plan is to search for a *particular word or words* in the lyric ngrams, it would be good to convert the *tuples of the *syllable_set* into *a string*.  Note that in the updated results, all of the syllables will be run together as a single string.

    #run hr function and convert hr['syllable_set'] to string
    hr = piece.homorhythm(ngram_length = 6, full_hr = True).fillna('')
    hr['syllable_set'] = hr['syllable_set'].apply(lambda x: ''.join(map(str, x[0]))).copy()

    #supply the list of words.  Capitalization matters!
    chosen_words = ["Maria", "immacula"]

    #filter the hr results for rows that contain any of the given words
    hr_with_chosen_words = hr[hr.apply(lambda x: hr['syllable_set'].str.contains('|'.join(chosen_words)))].dropna()
    hr_with_chosen_words

<!-- Show sample -->


**Search for Voices**

And if the plan is to search for the presence of a particular voice in the hr results, then the *lists of voices* in the *hr_voices* column will need to be converted into strings, too:

    #run hr function and convert hr['syllable_set'] to string
    hr = piece.homorhythm(ngram_length = 6, full_hr = True).fillna('')
    hr["hr_voices"] = hr["hr_voices"].apply(lambda x: ', '.join(map(str, x))).copy()

    #supply names of voices.  They must match the voice names in `piece.notes.columns()` 
    chosen_voices = ["Tenor", "Bassus"]
    #filter the results for hr passages involving chosen voices:
    hr_with_chosen_voices = hr[hr.apply(lambda x: hr['hr_voices'].str.contains('|'.join(chosen_voices)))].dropna()
    hr_with_chosen_voices

<!-- Show sample -->


## View Score Excerpts with Verovio

It is also possible to display the results of `piece.homorhythm()` as score excerpts using Verovio. The excerpts vary in length. 

Note that sometimes the same measure is part of overlapping groups--more work is pending to solve this problem.

The function also displays metadata about each excerpt: piece ID, composer, title, measures, and the minimum and maximum of voices in each passage moving in coordinated durations and syllables.

To use the function, pass the piece, homorhythm data frame, url of the piece, and mei_file name (all loaded in the first part of this notebook) as follows:

    piece.verovioHomorhythm()

<!-- The following does not work yet! -->

The same parameters noted above can also be used here, then passed to the `verovioHomorhythm()` function for rendering:

    hr = piece.homorhythm(ngram_length = 4, full_hr = True)
    piece.verovioHomorhythm(hr)

And it is possible to pass a *filtered set of results* to `piece.verovioHomorhythm()`.  For example, with chosen voices:

    #run hr function and convert hr['syllable_set'] to string
    hr = piece.homorhythm(ngram_length = 6, full_hr = True).fillna('')
    hr["hr_voices"] = hr["hr_voices"].apply(lambda x: ', '.join(map(str, x))).copy()

    #supply names of voices.  They must match the voice names in `piece.notes.columns()` 
    chosen_voices = ["Tenor", "Bassus"]
    #filter the results for hr passages involving chosen voices:
    hr_with_chosen_voices = hr[hr.apply(lambda x: hr['hr_voices'].str.contains('|'.join(chosen_voices)))].dropna()
    
    #render just the hr_with_chosen_voices using `piece.verovioHomorhythm()`:
    piece.verovioHomorhythm(hr_with_chosen_voices)





<!-- 

And need to check for batch!

-->


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