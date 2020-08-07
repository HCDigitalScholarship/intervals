# An interval-analysis based music similarity engine

### Find the project on Github and PyPI
#### Current Version: 0.3.1
- [Github](https://github.com/HCDigitalScholarship/intervals)
- [PyPI](https://pypi.org/project/crim-intervals/)

## Project Capabilities
- Find exact and close melodic matches given an mei file
- Find occurences of matching soggetto given a "vectorized" pattern
- Output a 0-1 similarity score between two musical works
- Classify melodic matches into periodic entries, imitative duos, fuga
- Output match data in a variety of ways: command line output, csv, python data types

## Getting Started
To download the project via the Python Packagae Index, use ```pip install crim-intervals``` and in a python shell enter ```from crim_intervals import *```
To use the project via github, clone the repository and in a python shell in the directory of the repository enter ```from main import *```  

## Method, Class help
The project is now documented with docstrings, for help using/understanding methods or classes use ```help(method_or_class_name)```

## Assisted Usage
For a guided way to get results for the basic intended usages of the project, simply enter:
```
from crim_intervals import *
assisted_interface()
```
wherever you are writing your code. The assisted interface will return an array of matches.

## User-inputted parameters
Each parameter listed has its own section below detailing configuration.
- Whether to input one score at a time, or a entire corpus at once with more limited selection ability, as well as what notes are to be analyzed, and the variety of ways in which they can be grouped (Detailed under "Note List Selection- Corpus" and "Note List Selection- Single Score")
- Whether to create generic or semitone intervals (Detailed under "Creating vectorized representations and selecting their types") 
- The size of pattern to be analyzed (Detailed under "Grouping the vectors into patterns")
- The minimum number of matches needed to be displayed, and optionally, the cumulative difference threshold for a two patterns to be considered closely matched (Detailed under "Finding close and exact matches")

### Note List Selection- Corpus
This section covers the capabilities falling under the CorpusBase object, which has the capability to import multiple pieces at once. To begin, import your scores using either a url or a file path. If you only have urls, input them as formatted below leave the second parameter blank, or make it an empty array. If you only have file paths, give the first parameter as an empty array.
```
corpus = CorpusBase(['url_to_mei_file1.mei', url_to_mei_file2.mei'], ['path/to/mei/file1.mei', 'path/to/mei/file2.mei'])
```
After, the first decision to be made is how you want to analyze the imported pieces:
- Get the whole piece ```corpus.note_list_whole_piece()```
- Get the whole piece combining unisons into one note ```corpus.note_list_no_unisons()```
- Get the whole piece only at selected offset within a measure ```corpus.note_list_selected_offset([offset1, offset2, offset3, etc.])```
- Get the note sounding at every regular offset ```corpus.note_list_incremental_offset(offset_increment)```
*For more information on each method, use help(method name), for example: help(note_list_incremental_offset)*

### Note List Selection- Single Score
This section covers the capabilities falling under the ScoreBase object, which can give more precise note lists, but only for a single piece at a time. To begin, import your score using either
```score1 = ScoreBase('https://url_to_mei_file.mei')``` for a file url or
```score2 = ScoreBase('/path/to/file.mei')``` for a file path (this path MUST start with a '/', otherwise it will be read as a url
After, decide on how you want to analyze or deconstruct your imported piece:
- Get the whole piece ```score1.note_list_whole_piece()```
- Get a note list from a selected measure range within a single voice ```score1.note_list_single_part(part_number, measure_start, measures_until_end)```
- Get a note list from a selected measure range over all voices ```score1.note_list_all_parts(measure_start, measures_until_end)```
- Get the whole piece combining unisons into one note ```score1.note_list_no_unisons()```
- Get the whole piece only at selected offset within a measure ```score1.note_list_selected_offset([offset1, offset2, offset3, etc.])```
- Get the note sounding at every regular offset ```score1.note_list_incremental_offset(offset_increment)```
- Get a note list from the whole piece, going by provided beats ```score1.note_list_selected_beat([beat1, beat2, etc.])```
*For more information on each method, use help(method name), for example: help(note_list_incremental_offset)

### Creating vectorized representations and selecting their types
At this point you should have constructed a note list from the methods of a CorpusBase or ScoreBase object. The next step is to group those notes into intervals using the IntervalBase object, which accepts note lists as a list, in case you want to analyze multiple ScoreBase note lists. 
- Multiple note lists: ```vectors = IntervalBase([score1.note_list_whole_piece(), score2.note_list_incremental_offset(2), corpus.note_list_whole_piece()]```
- Just one: ```vectors = IntervalBase([corpus.note_list_whole_piece()]```
The IntervalBase object's methods turn the note list given into the vectors with which we do pattern comparisons. To get those vectors, we must decide whether to use generic or semitone intervals:
- Semitone intervals: ```vectors.semitone_intervals()```
- Generic intervals: ```vectors.generic_intervals()```

### Grouping the vectors into patterns
Now that we have a list of vectors (or intervals between notes), we can begin to place them into patterns to be analyzed for similarity. To do so we must select the size of pattern to be used for our analysis:
```patterns = into_patterns(vectors.generic_intervals, pattern_size)```
*As always, for information on methods and their parameters, use the help() function- help(into_patterns)*

### Finding close and exact matches
Now that we have patterns, it is time to analyze them for similarity, which can be either in the form of exact matches, or "close" matches- which gauge similarity based on a cumulative difference threshold (for more on that, see [this example notebook](https://colab.research.google.com/drive/10YmmjOCt2xvkqaJYbBbE5Wu29_sF7mV3?authuser=3#scrollTo=Py-Q9TjiHAfC)). To find only exact matches- or those that follow the same melodic pattern (with potential for transposition across pitches), we bring in the ```patterns``` variable from the previous section:
```exact_matches = find_exact_matches(patterns, min_matches)```
where the parameter ```min_matches``` determines the minimum number of matches a pattern needs to be considered relevant and displayed. To print information about all matches found, use a simple for loop and another method:
```
for item in exact_matches:
    item.print_exact_matches()
```
Alternatively, if we want to look for "close" matches, we follow a similar stucture, but must provide the threshold detailed above and print slightly differently:
```
close_matches = find_close_matches(patterns, min_matches, threshold)
for item in close_matches:
    item.print_close_matches()
```

### Accessing information about matches
 There are a few ways information about matches can be accessed.
- To get information on the command line, use the for loop specified above, using the ```print_exact_matches``` or ```print_close_matches``` methods
- To export the matches information to a csv file use: ```export_to_csv(exact_matches)``` or ```export_to_csv(close_matches)``` where the parameter for the method is the return value from the match finding functions detailed above.
- For more programming-oriented users: The methods ```find_exact_matches``` and ```find_close_matches``` return an array of PatternMatches objects, each of which contain a list of Match object under the parameter ```pattern_match_obj.matches```. Each match object has information about its pattern and the notes which make it up, which can be useful for data analysis. Using the help function is always recommended if parameters/attributes are unclear.


### Additional Features
- Get a similarity "score" between 0 to 1, comparing the motifs shared between two pieces: ```similarity_score(first piece note list, second piece note list)```. The note lists are gathered from the methods of either a ScoreBase or CorpusBase object.
- Find a desired motif/soggetto within a corpus. Your soggetto must be specified as a list of intervals between notes. For example, the soggetto C-D-E-D-C would be vectorized in generic intervals as [2,2,-2,-2].```find_motif(corpus, soggetto_vector_list)```. If instead you wish to search in terms of semitone intervals, you have to specify an additional parameter as False: ```find_motif(corpus, soggetto_vector_list, False)```
