# Lyrics

CRIM intervals can find all of the text syllables associated with notes in each piece. The `lyrics()` function can, moreover, be used with many other CRIM Intervals functions, such as `ngrams()`, `durations()`, and so on. The `homorhythym()`, for instance, compares ngrams of lyrics and durations to predict passages where two or more voices are declaiming the same text in the same rhythms.


## The `lyrics()` Function  

By default, applying the `lyrics()` function to a piece will generate a DataFrame containing the lyrics at each relevant offset, for each voice part.  

    lyrics = piece.lyrics()  

As opposed to integers or floats, the DataFrame produced by the `lyrics()` function will be in the form of **text strings**. Also unlike other functions, the `lyrics()` function has no parameters, and therefore can only be executed in one way. Its usage, however, can still be varied based on the other functions with which it is combined. Note, for instance, that piece.`piece.ngrams(df=piece.lyrics())` will result in a dataframe that contains cells of *tuples*, just as the ngrams() function will for any other musical feature.

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
    piece.ngrams(df=piece.lyrics(), n = _N)

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

**Lyric ngrams, cleaned, and as strings (not tuples):**

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
    lyric_ngs = piece.ngrams(df=piece.lyrics(), n = _N)
    #convert them to tuples
    lyric_ngs_strings = lyric_ngs.applymap(convertTuple)

Or more succinctly:

    n = _n
    #make the ngrams
    lyric_ngs_strings = piece.ngrams(df=piece.lyrics(), n = _N).applymap(convertTuple)

## Predicting Homorhythmic Passages:  `piece.homorhythm()`

The `piece.homorhythm()` function identifies passages in which more than one voice has the *same durational ngrams* and the *same lyrical ngrams* at the *same time*. The method follows various stages:

* gets durational ngrams, and finds passages in which these are the same in more than two voices at a given offsets
* gets lyric ngrams, and finds passages in which the same sequence of two syllables are heard successively in at least two voices at the same offsets.
* checks the number of active voices (in order to count the number moving on coordinated homorhythm)

### The Parameters in Brief

Users can supply either of two arguments:

* `ngram_length` (which is 4 by default, and determines the number of durations and syllables that must be in common among the voices in order to be marked as HR);

* `full_hr` (which is True by default).  When `full_hr=True` the method will find any passage where *all active voices* share the same durational ngram and syllables; if `full_hr=False` the method will find *any passage where even two voices share the same durational ngram and the same syllables*.

Typical use:

    piece.homorhythm()
    
Or 

    piece.homorhythm(ngram_length=4, full_hr=True)

## View Score Excerpts with Verovio

It is also possible to display the results of `piece.homorhythm()` as score excerpts using Verovio. The excerpts vary in length. 

Note that sometimes the same measure is part of overlapping groups--more work is pending to solve this problem.

The function also displays metadata about each excerpt: piece ID, composer, title, measures, and the minimum and maximum of voices in each passage moving in coordinated durations and syllables.

To use the function, pass the piece, homorhythm data frame, url of the piece, and mei_file name (all loaded in the first part of this notebook) as follows:

    piece.verovioHomorhythm()

The same parameters noted above can also be used here:

    piece.homorhythm(ngram_length=4, full_hr=True)

<!-- Note that the import code for this function and other verovio functions will need to be modified to allow for local files 

needs to be added to ALL Verovio functions!

And need to check for batch!

-->

def verovioHomorhythm(self, ngram_length=4, full_hr=True):
      if self.path.startswith('Music_Files/'):
         text_file = open(self.path, "r")
         fetched_mei_string = text_file.read()
      if piece.path.startswith('/'):
        text_file = open(piece.path, "r")
        fetched_mei_string = text_file.read()


-----

## Sections in this Guide

  * [01_Introduction](01_Introduction.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_MelodicIntervals](03_MelodicIntervals.md)
  * [04_HarmonicIntervals](04_HarmonicIntervals.md)
  * [05_Ngrams](05_Ngrams.md)
  * [06_Durations](06_Durations.md)
  * [07_Lyrics](07_Lyrics.md)
  * [08_TimeSignatures_BeatStrength](08_TimeSignatures_BeatStrength.md)
  * [09_DetailIndex](09_DetailIndex.md)
  * [10_Cadences](10_Cadences.md)
  * [11_Pandas](11_Pandas.md)
  * [12_Modules](12_Modules.md)