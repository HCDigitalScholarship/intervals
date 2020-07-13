# Building a music similarity engine based on intervals

## Find the project on Github and PyPI
[Github](https://github.com/HCDigitalScholarship/intervals)
[PyPI](https://pypi.org/project/crim-intervals/)

## Project Goals:
- Load mei file(s) from url or path
- Carve out desired portion of piece/corpus
- Create a sequence of interval objects from the score
- Set filters on parts, measures, ids
- Export ema
- Analyze similarity of two objects

## Assisted Usage
For a guided way to get results for the basic intended usages of the project, simply enter:
```
assisted_interface()
```
wherever you are writing your code.

## Sample Usage
- One piece at a time
```
piece1 = ScoreBase('https://crimproject.org/mei/CRIM_Model_0008.mei')
piece2 = ScoreBase('https://sameplemeifile.mei')
vectors1 = IntervalBase(piece1.note_list)
vectors2 = IntervalBase(piece2.note_list_all_parts(1, 20))
patterns = into_patterns([vector1.generic_intervals, vector.generic_intervals], 5)
exact_matches = find_exact_matches(patterns, 10)
```
- Loading in a Corpus
```
corpus = CorpusBase(['https://sameplemeifile1.mei', 'https://sameplemeifile.mei'],[/sample/path/to/mei/file, /sameple/path/two])
vectors = IntervalBase(corpus.note_list)
patterns = into_patterns([vectors.semitone_intervals], 5)
close_matches = find_close_matches(patterns, 10, 1)
```
- Outputting relevant information
  - Printing out matches information
  ```
  ...
  exact_matches = find_exact_matches(patterns, 10)
  for item in exact_matches:
      item.print_exact_matches()
  close_matches = find_close_matches(patterns, 10, 1)
  for item in close_matches:
      item.print_close_matches()
  ```
  - Similarity scores
  ```
  piece1 = ScoreBase('https://crimproject.org/mei/CRIM_Model_0008.mei')
  piece2 = ScoreBase('https://sameplemeifile.mei')
  print(similarity_score(piece1.note_list, piece2.note_list, 5))
  ```
  - Outputting match information to csv (includes ema, mei slices)
  ```
  export_to_csv(exact_matches)
  ```
  - Find occurences of a motif
  ```
  find_motif(CorpusBase object, [motif], generic intervals boolean)
  ```

## Usage Flow ~~~
- Load in files with either ScoreBase or CorpusBase
  ```
  ScoreBase(url)
  CorpusBase([url1, url2, ...], [filepath1, filepath2, ...])
  ```
  - Search for a motif:
  ```
  find_motif(corpus: CorpusBase, [motif], generic intervals: boolean)
  ```
- Create desired note list for use in IntervalBase
  - Options using CorpusBase:
    ```
    piece.note_list
    ```
  - Options using ScoreBase:
    ```
    piece.note_list
    piece.note_list_down_beats
    piece.note_list_selected_beats([beats])
    piece.note_list_all_parts(starting_measure, number_of_measures_after)
    piece.note_list_single_part(part_number, starting_measure, number_of_measures_after)
    piece.note_list_by_offset([offsets])
    ```
- At this point similarity scores can be shown
  - size of pattern indicates how many notes in a row need to follow the same rhythmic pattern to be considered a match
```
similarity_score(first piece note list, second piece note list, size of pattern)
```
- Decide between semitone intervals and generic intervals
```
vectors.generic_intervals
vectors.semitone_intervals
```
- Construct patterns from note_list (more options for pattern construction forthcoming)
```
into_patterns([list of piece note lists], size of pattern)
```
- Decide which type of matches to find
  - These will not work if you don't send it the return value from into_patterns
```
find_exact_matches(return value from into_patterns, minimum matches needed to be displayed)
find_close_matches(return value from into_patterns, minimum matches needed to be displayed, threshold)
```
  - Returns a list of matches for easy analysis, printing shown above
- Export to csv in current working directory:
```
export_to_csv(exact_matches)
```
- Run desired analysis with your own python code, print out results, etc.
