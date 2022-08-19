# An interval-analysis based music similarity engine


### Find the project on Github 
#### Current Version: 0.3.3
- [Github](https://github.com/HCDigitalScholarship/intervals)


## About CRIM Intervals

Based on **Python** and **Pandas**, and **music21** (https://web.mit.edu/music21/), **CRIM Intervals** is a pattern finding engine for musical scores, with an emphasis on the kinds of melodic and harmonic patterns found in Renaissance polyphony. It has been developed as a primary data analysis tool for **Citations:  The Renaissance Imitation Mass** (http://crimproject.org and https://sites.google.com/haverford.edu/crim-project/home), but can be applied and adapted to a wide range of styles.

Results are reported in **Pandas** dataframes (and thus exportable in a variey of standard formats for further analysis), and also via several visualizations methods.

Some methods in **CRIM Intervals** also work with **CRIM Project** data created by human observers.

## Getting Started with CRIM Intervals

CRIM intervals is now available in a series of interactive **Jupyter** notebooks easily launched via **Binder** at https://github.com/RichardFreedman/CRIM_Public_Notebooks.  These can in turn be downloaded and adapted for your own use.

### What can CRIM Intervals do?

As explained in the **ReadMe** section of our public **Jupyter** notebook (https://github.com/RichardFreedman/CRIM_Public_Notebooks), CRIM Intervals performs a variety of tasks.

- The individual tools (called methods in Python and Pandas) can be adjusted in various ways, such as diatonic vs chromatic, compound vs simple intervals, real vs constant durations, as well as pattern length, similarity.
- Read the documentation with this command ```print(model.YourMethod.__doc__)```, where you will replace ```'YourMethod'``` with the name of the individual method, for example ```print(model.melodic.__doc__)```.


#### Notes, Durations, Rests, Patterns (Melodic, Harmonic, Modular)

CRIM Intervals as various *methods*, notably:


- **notes**, which finds **all the notes and rests in a score**, with a tabular score-like representation of the pitches, pitch classes, and durations (expressed in music21 "offsets", in which each quarter note corresponds to the value of 1.0).  It can also derminte the location of any note as a measure+beat reference with **detailIndex**
- **melodic**, which finds **melodic intervals** in any voice part, with various options for *diatonic*, *chromatic* and *zero-based* distances. Intervals can be *compound* (distinguishing between tenths and thirds, for instance), or *simple*, and can include *quality* (distinguishing major and minor thirds, for instance), or not.
- **harmonic**, which finds **harmonic intervals** between every combination of two voices in a piece, with various options for *diatonic* and *chromatic*. These intervals can also be *directed* (as when a tenor voice sounds above the altus), or not.
- **ngrams**, which finds **nGrams of any length in each voice part**.  nGrams are frequently used in linguistic analysis (https://en.wikipedia.org/wiki/N-gram), and can help us find repeating patterns within and among works.

Other Features

- **Finds notes and patterns according to actual or incremental durations**. The default method follows the **actual durations** (so that melodic tones and ngrams are simply strings of events representing each new tone in a given voice), but we can also select a sample by fixed **incremental durations**, for instance by every half-note.
- **Finds contrapuntal modules** of any length.  Modular analysis represents in numerical values a combination of the vertical intervals made between any two voices with the melodic intervals heard in the motion of the lower voice.  A module of **7_Held 6_-2, 8** for instance, represents vertical intervals of **7, 6, 8** between two voices and **in the lower voice a tied note followed by a descending second**.  Together these five events represent a typical cadence formula.  Repeating modules are a key part of Renaissance contraputnal style.

Complete **documentation** of these capacities is available via **doc.strings** via this command ```print(model.YourMethod.__doc__)```, where you will replace ```'YourMethod'``` with the name of the individual method, for example ```print(model.melodic.__doc__)```.


#### Heatmaps, Graphs and Visualizations

- Some of these tools use **CRIM Project** human annotations (*Relationships* and *Observations*, providing ways to map what CRIM analysts have found within and between pieces in the corpus.  There are interactive **heatmaps** and **network graphs**, with links back to the live **CRIM Project** website.)
- Other tools rely on *derived data* presenting interactive **heatmaps** and **networks** of **nGrams** and other patterns in a given piece.
- Similarity Maps all users to chart similar soggetti (nGrams) across a piece, with variable thresholds.
- Network Graphs use CRIM Metadata and CRIM Interval data to chart connections between groups of pieces, according to the musical patterns or procedures they use, or the kinds of quotation and transformation they apply to their models.The notebooks also provide different ways to visualize music data.

#### Similarity Tools

CRIM Intervals is also developing various tools to explore the idea similarity in musical patterns.  To date we have implemented algorithms that use:

- Levenshtein Distances (https://en.wikipedia.org/wiki/Levenshtein_distance), in which differences are calculated according to the number of substitutions required for two patterns to match.

- Manhattan Distance (https://en.wikipedia.org/wiki/Taxicab_geometry), which is well suited to integer-based distances.

Among the heatmaps you will find interactive tools for adjusting the level of similarity against various nGrams are measured.

Soon we will be launching **Annotation Based Similarity Search**, in which users can point to a specific constellation of notes from any piece and return patterns similar to these.

#### Classification of Contrapuntal Types


The Classifier methods include various tools that predict Presentation Types commonly found in Renaissance polyphony, including Fugas, Imitative Duos, Non-Imitative Duos, Periodic Entries, and Cadences.

- Some features of the classifier run naively across one or more pieces.
- Others can be guided by strings chosen by


# Credits and Intellectual Property Statement

CRIM Intervals contributors include:

- Andrew Janco (Haverford College)
- Freddie Gould (Haverford College)
- Trang Dang (Bryn Mawr College)
- Alexander Morgan (McGill University)
- Daniel Russo-Batterham (Melbourne University)
- Richard Freedman (Haverford College)

CRIM Intervals is made possible generous support from:

- Haverford College
- The American Council of Learned Societies

All CRIM intervals tools are available via a **Creative Commons** license (Attribution-ShareAlike 4.0 International (CC BY-SA 4.0):  https://creativecommons.org/licenses/by-sa/4.0/.


# Documentation for CRIM Intervals Previous Versions (Summer 2020)

<<<<<<< Updated upstream
## Getting Started
To download the project via the Python Packagae Index, use ```pip install crim-intervals``` and in a python shell
enter ```from crim_intervals import *```
To use the project via github, clone the repository and in a python shell in the directory of the repository
enter ```from main import *```
=======
To download the project via the Python Packagae Index, use ```pip install crim-intervals``` and in a python shell enter ```from crim_intervals import *```
To use the project via github, clone the repository and in a python shell in the directory of the repository enter ```from main import *```
>>>>>>> Stashed changes

## Method, Class help

The project is now documented with docstrings, for help using/understanding methods or classes
use ```help(method_or_class_name)```

## Assisted Usage
For a guided way to get results for the basic intended usages of the project, simply enter:
```
from crim_intervals import *
assisted_interface()
```
wherever you are writing your code. The assisted interface will return an array of matches.

## User-inputted parameters
Each parameter listed has its own section below detailing configuration.

- Whether to input one score at a time, or a entire corpus at once with more limited selection ability, as well as what
  notes are to be analyzed, and the variety of ways in which they can be grouped (Detailed under "Note List Selection-
  Corpus" and "Note List Selection- Single Score")
- Whether to create generic or semitone intervals (Detailed under "Creating vectorized representations and selecting
  their types")
- The size of pattern to be analyzed (Detailed under "Grouping the vectors into patterns")
- The minimum number of matches needed to be displayed, and optionally, the cumulative difference threshold for a two
  patterns to be considered closely matched (Detailed under "Finding close and exact matches")

### Note List Selection- Corpus

This section covers the capabilities falling under the CorpusBase object, which has the capability to import multiple
pieces at once. To begin, import your scores using either as a list of urls and/or file paths. File paths must begin
with a '/', otherwise they will be processed as urls.
```
corpus = CorpusBase(['url_to_mei_file1.mei', 'url_to_mei_file2.mei', 'path/to/mei/file1.mei', 'path/to/mei/file2.mei'])
```
After, the first decision to be made is how you want to analyze the imported pieces:
- Get the whole piece ```corpus.note_list_whole_piece()```
- Get the whole piece combining unisons into one note ```corpus.note_list_no_unisons()```
- Get the whole piece only at selected offset within a
  measure ```corpus.note_list_selected_offset([offset1, offset2, offset3, etc.])```
- Get the note sounding at every regular offset ```corpus.note_list_incremental_offset(offset_increment)```
  *For more information on each method, use help(method name), for example: help(note_list_incremental_offset)*

### Note List Selection- Single Score

This section covers the capabilities falling under the ScoreBase object, which can give more precise note lists, but
only for a single piece at a time. To begin, import your score using either
```score1 = ScoreBase('https://url_to_mei_file.mei')``` for a file url or
```score2 = ScoreBase('/path/to/file.mei')``` for a file path (this path MUST start with a '/', otherwise it will be
read as a url After, decide on how you want to analyze or deconstruct your imported piece:

- Get the whole piece ```score1.note_list_whole_piece()```
- Get a note list from a selected measure range within a single
  voice ```score1.note_list_single_part(part_number, measure_start, measures_until_end)```
- Get a note list from a selected measure range over all
  voices ```score1.note_list_all_parts(measure_start, measures_until_end)```
- Get the whole piece combining unisons into one note ```score1.note_list_no_unisons()```
- Get the whole piece only at selected offset within a
  measure ```score1.note_list_selected_offset([offset1, offset2, offset3, etc.])```
- Get the note sounding at every regular offset ```score1.note_list_incremental_offset(offset_increment)```
<<<<<<< Updated upstream
- Get a note list from the whole piece, going by provided
  beats ```score1.note_list_selected_beat([beat1, beat2, etc.])```
  *For more information on each method, use help(method name), for example: help(note_list_incremental_offset)
=======
- Get a note list from the whole piece, going by provided beats ```score1.note_list_selected_beat([beat1, beat2, etc.])```

For more information on each method, use help(method name), for example: help(note_list_incremental_offset)
>>>>>>> Stashed changes

### Creating vectorized representations and selecting their types

At this point you should have constructed a note list from the methods of a CorpusBase or ScoreBase object. The next
step is to group those notes into intervals using the IntervalBase object, which accepts note lists as a list, in case
you want to analyze multiple ScoreBase note lists.

- Multiple note
  lists: ```vectors = IntervalBase([score1.note_list_whole_piece(), score2.note_list_incremental_offset(2), corpus.note_list_whole_piece()]```
- Just one: ```vectors = IntervalBase([corpus.note_list_whole_piece()]```
  The IntervalBase object's methods turn the note list given into the vectors with which we do pattern comparisons. To
  get those vectors, we must decide whether to use generic or semitone intervals:
- Semitone intervals: ```vectors.semitone_intervals()```
- Generic intervals: ```vectors.generic_intervals()```

### Grouping the vectors into patterns

Now that we have a list of vectors (or intervals between notes), we can begin to place them into patterns to be analyzed
for similarity. To do so we must select the size of pattern to be used for our analysis:
```patterns = into_patterns(vectors.generic_intervals, pattern_size)```
*As always, for information on methods and their parameters, use the help() function- help(into_patterns)*

### Finding close and exact matches

Now that we have patterns, it is time to analyze them for similarity, which can be either in the form of exact matches,
or "close" matches- which gauge similarity based on a cumulative difference threshold (for more on that,
see [this example notebook](https://colab.research.google.com/drive/10YmmjOCt2xvkqaJYbBbE5Wu29_sF7mV3?authuser=3#scrollTo=Py-Q9TjiHAfC))
. To find only exact matches- or those that follow the same melodic pattern (with potential for transposition across
pitches), we bring in the ```patterns``` variable from the previous section:
```exact_matches = find_exact_matches(patterns, min_matches)```
where the parameter ```min_matches``` determines the minimum number of matches a pattern needs to be considered relevant
and displayed. To print information about all matches found, use a simple for loop and another method:
```
for item in exact_matches:
    item.print_exact_matches()
```

Alternatively, if we want to look for "close" matches, we follow a similar stucture, but must provide the threshold
detailed above and print slightly differently:

```
close_matches = find_close_matches(patterns, min_matches, threshold)
for item in close_matches:
    item.print_close_matches()
```

### Accessing information about matches

There are a few ways information about matches can be accessed.

- To get information on the command line, use the for loop specified above, using the ```print_exact_matches```
  or ```print_close_matches``` methods
- To export the matches information to a csv file use: ```export_to_csv(exact_matches)```
  or ```export_to_csv(close_matches)``` where the parameter for the method is the return value from the match finding
  functions detailed above.
- To export the matches information to a pandas dataframe use: ```export_pandas(exact_matches)```
  or ```export_pandas(close_matches)``` where the parameter for the method is the return value from the match finding
  functions detailed above.
- For more programming-oriented users: The methods ```find_exact_matches``` and ```find_close_matches``` return an array
  of PatternMatches objects, each of which contain a list of Match object under the
  parameter ```pattern_match_obj.matches```. Each match object has information about its pattern and the notes which
  make it up, which can be useful for data analysis. Using the help function is always recommended if
  parameters/attributes are unclear.

### Additional Features

- Get a similarity "score" between 0 to 1, comparing the motifs shared between two
  pieces: ```similarity_score(first piece note list, second piece note list)```. The note lists are gathered from the
  methods of either a ScoreBase or CorpusBase object.
- Find a desired motif/soggetto within a corpus. Your soggetto must be specified as a list of intervals between notes.
  For example, the soggetto C-D-E-D-C would be vectorized in generic intervals as [2,2,-2,-2]
  .```find_motif(corpus, soggetto_vector_list)```. If instead you wish to search in terms of semitone intervals, you
  have to specify an additional parameter as False: ```find_motif(corpus, soggetto_vector_list, False)```
- Classify Matches into periodic entries, imitative duos, and fuga. Using the return value from ```find_exact_matches```
  or ```find_close_matches```, you can classify matches using ```classify_matches(exact_matches)```
  or ```classify_matches(exact_matches, 2)``` where the second parameter is an optional cumulative duration difference
  threshold. The return value of this function is a list of ClassifiedMatch objects, with Match object data inside the
  parameter matches. Use ```help(ClassifiedMatch)``` for more information.
  - Additionally, in addition to the printed terminal output, this information can be exported to a csv file using the
    return value of the function:
  ```
  classified_matches = classify_matches(exact_matches)
  export_to_csv(classified_matches)
  ```
