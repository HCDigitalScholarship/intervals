# CRIM Intervals: A Python Library for Analysis

Based on Python, Pandas, and Mike Cuthbert's [music21](http://web.mit.edu/music21/), CRIM Intervals is a pattern finding engine for musical scores, with an emphasis on the kinds of melodic and harmonic patterns found in Renaissance polyphony. It has been developed as a primary data analysis tool for CRIM, but can be applied and adapted to a wide range of styles. Results are reported in Pandas dataframes (and thus exportable in a variety of standard formats for further analysis), and also via several visualizations methods.

## File Types Compatible with CRIM Intervals

Since CRIM Intervals is based on music21, all the file types read by music21 will work with CRIM Intervals.  Be sure to include the appropriate file extension as part of each file name:  '.mei', '.mid', '.midi', '.abc', '.xml', '.musicxml'. Note that the `lyrics` function is untested with midi and abc files.

## Install CRIM Intervals and its Dependencies

Install with pypi package manager:  `pip install crim_intervals`

## Import Libraries

```python
# import crim_intervals
import crim_intervals
from crim_intervals import * 
from crim_intervals import main_objs
import crim_intervals.visualizations as viz
# import pandas and other libraries
import pandas as pd
import re
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import interact
from pandas.io.json import json_normalize
from pyvis.network import Network
from IPython.display import display
import requests
import os

# for use in Jupyter notebook, create a local folder for music files
MYDIR = ("saved_csv")
CHECK_FOLDER = os.path.isdir(MYDIR)

# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.makedirs(MYDIR)
    print("created folder : ", MYDIR)
else:
    print(MYDIR, "folder already exists.")
    
MUSDIR = ("Music_Files")
CHECK_FOLDER = os.path.isdir(MUSDIR)

# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.makedirs(MUSDIR)
    print("created folder : ", MUSDIR)

else:
    print(MUSDIR, "folder already exists.")
```


## Importing a Piece:  `importScore()`

CRIM Intervals begins by importing one or more MEI, MusicXML, or MIDI Files. This can be done directly, as shown:

```python
piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')
```

The field within the `importScore()` function can be either a url or local file path, and must be surrounded by quotes as shown.

Note that the **local file path must also be preceded by a `/` [forward slash]**, for example:

```python
piece = importScore('/path/to/mei_folder/file.mei')
```

### Check Metadata for Imported Piece

To confirm successful import, view the metadata: `print(piece.metadata)`. Alternatively, add the parameter `verbose = True` to the `importScore()` function. CRIM Intervals will automatically provide information to the user as it runs about whether or not it was able to successfully import the given piece.  For example: 

```python
piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei', verbose = True)
```

Note that import errors will be reported even if `verbose = False`
  

## Importing Multiple Pieces at Once: `CorpusBase()`

If you pass `importScore()` a **path to a directory** it will import all the files in that directory, for example:

```python
pieces = importScore('/Users/rfreedma/Downloads/MEI_Folder')
```  

Adding the parameter `recursive = True` will in turn import all of the pieces in the main directory and any subdirectories, for example: 

```python
pieces = importScore('/Users/rfreedma/Downloads/MEI_Folder', recursive = True)
```

And as with a single piece, the parameter `verbose = True` will the status of each attempted import.

The CRIM Interval library also allows the user to import multiple pieces at once through the `CorpusBase()` function. This function operates similarly to the `importPiece()` function, but accepts a **list of piece urls or paths** instead of a single url or path. The individual items in the Python list must be:

* surrounded by quotation marks (remember the `/` at the start of any time coming from a local path!)
* separated by commas (but no comma after the last item in the list)

And then the entire list must be surrounded in square brackets. 

The complete import statement will look like this:

```python
corpus = CorpusBase(['url_to_mei_file1.mei', 'url_to_mei_file2.mei', '/path/to/mei/file1.mei', '/path/to/mei/file2.mei'])  
```

Note that there is a special format required when a given CRIM Intervals function (such as melodic(), or harmonic() is applied to a **corpus** object. See below, and also the **batch method** documentation for each individual function.

## Using CRIM Intervals Functions

Once one or more pieces have been imported, they can be examined and analyzed through a wide variety of different functions that find the notes, durations, melodic intervals, harmonic intervals, and so on. Most of these functions follows one of a few common formats: 

*like this:*
  
    piece.func()  

*or:*  

    piece.func(some_parameter)

*or:*  

    piece.func(param_1 = True, param_2 = "d") 

Except in the case of a **corpus** of pieces (see below), the parentheses that follow the function are *always required*. Most functions have parameters that can be adjusted (for instance, the choice of diatonic or chromatic intervals). It is always possible simply to accept the default settings (no need to pass a parameter).  Or the parameters can be adjusted. 

The specific details of how to format the function varies from case to case. The choices and common settings for each function are detailed in the pages of this guide.  It is also possible to read the built-in documentation as explained below under **Help and Documentation**.

## Batch Methods for a Corpus of Pieces

In the case of a **corpus** of pieces, it is also necessary to use the `batch` function, which applies one of the main functions (such as `notes`, `melodic`, `harmonic`, etc.) to each of the pieces in the corpus in turn, and then assembles the results into a single dataframe. First create the corpus:

```python
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei', 'https://crimproject.org/mei/CRIM_Model_0009.mei'])
```

Then specify the function to be used (NB:  **do not include the parentheses after the function!**):
  
    func = ImportedPiece.notes

And finally run the function with each piece and concatenate them as a single dataframe:
  
    list_of_dfs = corpus.batch(func)

Normally parameters are passed to a function within the parentheses (as noted above). But with the batch methods for a corpus the parameters are instead passed as **kwargs** (that is, as a *dictionary of keyword arguments*, with each parameter and its corresponding value formatted as `{key: value}` pair). 

For example see this code for batch processing a corpus with the `melodic` function using some keywords:
  
 ```python
 #define the corpus
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei', 'https://crimproject.org/mei/CRIM_Model_0009.mei'])
#specify the function 
func = ImportedPiece.melodic  # <- NB there are no parentheses here
#provide the kwargs
kwargs = {'kind': 'c', 'directed': False}
#build a list of dataframes, one for each piece in the corpus
list_of_dfs = corpus.batch(func, kwargs)
#concatenate the list to a single dataframe
output = pd.concat(list_of_dfs)
```
  
### Chaining Together Batch Methods

CRIM Intervals functions often need to be chained together, as explained in the individual sections for each function. The results of the first function (which is a list of dataframes) is passed to the second fucntion via the `df` parameter as a `kwarg`

```python
#define the corpus
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                    'https://crimproject.org/mei/CRIM_Model_0009.mei'])
#first function
func1 = ImportedPiece.melodic
#first function results as list of dfs
list_of_dfs = corpus.batch(func = func1, kwargs = {'end': False}, metadata = False)
#second function
func2 = ImportedPiece.ngrams
#now the list_of_dfs from the first function is passed to the second function as the keyword argument 'df'
list_of_melodic_ngrams = corpus.batch(func = func2, kwargs = {'n': 4, 'df': list_of_dfs})
```

### Piece Metadata and Batch Methods:  The `metadata` Parameter

The `batch` method will normally include `metadata` for each piece. But if the aim is to chain several functions together in a series of batch processes, it is probably best to request the metadata only for the final step:

```python
#define the corpus
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                        'https://crimproject.org/mei/CRIM_Model_0009.mei'])
#first function
func1 = ImportedPiece.melodic
#first function results as list of dfs
#notice that 'metadata = False' for this step
list_of_dfs = corpus.batch(func = func1, kwargs = {'end': False}, metadata = False)
#second function
func2 = ImportedPiece.ngrams
#now the list_of_dfs from the first function is passed to the second function as the keyword argument 'df'
#here metadata remains as True (which is the default, and so we can omit the parameter) 
list_of_melodic_ngrams = corpus.batch(func = func2, kwargs = {'n': 4, 'df': list_of_dfs})
```

### Tracking Batch Processing Errors:  The `verbose` Parameter

As in the case of single piece imports, when used as part of a `batch` function, the `verbose = True` provides confirmation that each piece has been successfully imported. This can be useful to pinpoint a piece that is triggering a bug.

```python
corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei', 'https://crimproject.org/mei/CRIM_Model_0009.mei'])
func = ImportedPiece.notes
list_of_dfs = corpus.batch(func, verbose = True)
```

### Voice Part Names vs Staff Position in Batch Processing:  The `number_parts` Parameter

By default, .batch will replace columns that consist of part names (like `.melodic()` results) or combinations of part names (like `.harmonic()` results) with **staff position numbers**, starting with "1" for the highest part on the staff, "2" for the second highest, etc. This is useful when combining results from pieces with parts that have different names. For example:

```python
list_of_dfs_with_numbers_for_part_names = corpus.batch(ImportedPiece.melodic)
```

To keep the **original part names** in the columns, set `number_parts` parameter to False. For example:

```python
list_of_dfs_with_original_part_names = corpus.batch(ImportedPiece.melodic, number_parts = False)
```


## Exporting CRIM Intervals Results

CRIM Intervals is a Python library.  But it also makes extensive use of PANDAS (Python for Data Analysis).  The most common output for the CRIM Intervals functions is thus a **DataFrame**.  These can be viewed in output window of VS-Code (or similar IDE where CRIM Intervals is running), or can be seen in Juypyter Notebooks.  There are nevertheless two useful ways to download results for later use:

### Export to CSV:  

If you are running the Jupyter Hub version of this code, then there should be a folder provided called 'saved_csv'. This is where we will be exporting files, from which you can then download them to your computer.

If you wish to export a CSV a piece's that has been generated as a DataFrame, you can do so with the following command line: 
  
```python
notebook_data_frame_name.to_csv('saved_csv/your_file_title.csv')
```

'notebook_data_frame_name' should be replaced with the name of your DataFrame. For example, if you had ran the following lines:

```python
piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')
mel = piece.melodic() 
``` 

You could then save this model's melodic interval data to a CSV file with the file name 'CRIM_Model_0008.csv' by running the following: 

```python
mel.to_csv('saved_csv/CRIM_Model_0008.csv')
```

### Export to Excel:  

Alternatively, a DataFrame can be saved as an Excel file with the following command lines in order, once again replacing 'file_name.xlsx' with your desired file name, replacing 'Sheet1' with your desired sheet name **(in quotes)**, and replacing 'frame_name' in the second line with the name of your DataFrame **(without quotes)**, which was 'mel' in the last example: 

```python
writer = pd.ExcelWriter('saved_csv/file_name.xlsx', engine = 'xlsxwriter') 
frame_name.to_excel(writer, sheet_name = 'Sheet1')  
writer.save()```  

Substituting the information from the first example, we could write that same DataFrame to an Excel sheet with the following commands: 

```python
writer = pd.ExcelWriter('saved_csv/CRIM_Model_0008.xlsx', engine = 'xlsxwriter')
mel.to_excel(writer, sheet_name = 'CRIM Model 0008') 
writer.save() ```
 
## Help and Documentation

The documentation associated with each function can be read with a line of the following sample format: 

```python
print(piece.notes.__doc__)```

This line would print out the documentation (`.__doc__`) associated with the function `notes()`, a function applicable to the object `piece`. Note that to print the documentation for a function, some object able to utilize that function must be used in the command line as shown above.

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