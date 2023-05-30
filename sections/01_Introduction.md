# Introduction

## File Types Compatible with CRIM Intervals

  * Since CRIM Intervals is based on music21, all the file types read by music21 will work with CRIM Intervals.  Be sure to include the appropriate file extension as part of each file name:  '.mei', '.mid', '.midi', '.abc', '.xml', '.musicxml'
  * Note that the lyrcs functions are untested with midi and abc files

## Importing a Piece:  `importScore()`

  * CRIM Intervals begins by importing one or more MEI, MusicXML, or MIDI Files. This can be done directly, as shown:  
`piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')`
  * The field within the `importScore()` function can be either a url or local file path, and must be surrounded by quotes as shown
  * Note that the **local file path must also be preceded by a `/` [forward slash]**, for example `piece = importScore('/path/to/mei/file2.mei')`

### Check Metadata for Imported Piece
  * To confirm successful import, view the metadata: `print(piece.metadata)`
  * Alternatively, add the parameter `verbose = True` to the `importScore()` function. CRIM Intervals will automatically provide information to the user as it runs about whether or not it was able to successfully import the given piece.  For example: `piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei', verbose = True)`.  Note that import errors will be reported even if `verbose = False`
  

## Importing Multiple Pieces at Once: `CorpusBase()`

  * If you pass `importScore()` a **path to a directory** it will import all the files in that directory, for example: `pieces = importScore('/Users/rfreedma/Downloads/MEI_Folder')`.  
  * Adding the parameter `recursive = True` will in turn import all of the pieces in the main directory and any subdirectories, for example: `pieces = importScore('/Users/rfreedma/Downloads/MEI_Folder', recursive=True)`
  * And as with a single piece, the parameter `verbose=True` will the status of each attempted import
  * The CRIM Interval library also allows the user to import multiple pieces at once through the `CorpusBase()` function  
  * This function operates similarly to the `importPiece()` function, but accepts a **list of piece urls or paths** instead of a single url or path  
  * The individual items in the Python list must be:
    + surrounded by quotation marks (remember the `/` at the start of any time coming from a local path)
    + separated by commas (but no comma after the last item in the list)
  * And then the entire list must be surrounded in square brackets. 
  * The complete import statement will look like this: `corpus = CorpusBase(['url_to_mei_file1.mei', 'url_to_mei_file2.mei', '/path/to/mei/file1.mei', '/path/to/mei/file2.mei'])`  
  * Note that there is a special format required when a given CRIM Intervals function (such as melodic(), or harmonic() is applied to a **corpus** object. See below, and also the **batch method** documentation for each individual function.

## Using CRIM Intervals Functions
  * Once one or more pieces have been imported, they can be examined and analyzed through a wide variety of different functions that find the notes, durations, melodic intervals, harmonic intervals, and so on. Most of these functions follows one of a few common formats: 

LIKE THIS:
  
    piece.func()   

OR:  

    piece.func(some_parameter)  

OR:  

    piece.func(param_1 = True, param_2 = "d") 

  * Except in the case of a **corpus** of pieces (see below), the parentheses that follow the function are *always required*. Most functions have parameters that can be adjusted (for instance, the choice of diatonic or chromatic intervals). It is always possible simply to accept the default settings (no need to pass a parameter).  Or the parameters can be adjusted. 
  * The specific details of how to format the function varies from case to case. The choices and common settings for each function are detailed in the pages of this guide.  It is also possible to read the built-in documentation as explained below under **Help and Documentation**.

## Batch Methods for a Corpus of Pieces

  * In the case of a **corpus** of pieces, it is also necessary to use the `batch` function, which applies one of the main functions (such as `notes`, `melodic`, `harmonic`, etc.) to each of the pieces in the corpus in turn, and then assembles the results into a single dataframe. First create the corpus:


    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])

  * Then specify the function to be used (NB:  **do not include the parentheses after the function!**):
  
    func = ImportedPiece.notes

  * And finally run the function with each piece and concatenate them as a single dataframe:
  
    list_of_dfs = corpus.batch(func)

  * Normally parameters are passed to a function within the parentheses (as noted above). But with the batch methods for a corpus the parameters are instead passed as **kwargs** (that is, as a *dictionary of keyword arguments*, with each parameter and its corresponding value formatted as `{key: valule}` pair). For example see this code for batch processing a corpus with the `melodic` function using some keywords:
    
    #define the corpus:
    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
                             'https://crimproject.org/mei/CRIM_Model_0009.mei'])
    #specify the function
    func = ImportedPiece.melodic  # <- NB there are no parentheses here
    #provide the kwargs
    kwargs = {'kind': 'c', 'directed': False}
    #build a list of dataframes, one for each piece in the corpus
    list_of_dfs = corpus.batch(func, kwargs)
    #concatenate the list to a single dataframe
    output = pd.concat(list_of_dfs)
  

  ### Chaining Together Batch Methods

  ### Voice Part Names vs Staff Position in Batch Processing:  the `number_parts` Parameter

  ### Piece Metadata and Batch Methods:  the `metadata` Parameter

  ### Tracking Batch Processing Errors:  the `verbose` Parameter


## Exporting CRIM Intervals Results

  * CRIM Intervals is a Python library.  But it also makes extensive use of PANDAS (Python for Data Analysis).  The most common output for the CRIM Intervals functions is thus a **DataFrame**.  These can be viewed in output window of VS-Code (or similar IDE where CRIM Intervals is running), or can be seen in Juypyter Notebooks.  There are nevertheless two useful ways to download results for later use:

### Export to CSV:  

  * If you are running the Jupyter Hub version of this code, then there should be a folder provided called 'saved_csv'. This is where we will be exporting files, from which you can then download them to your computer.  
  * If you wish to export a CSV a piece's that has been generated as a DataFrame, you can do so with the following command line:  

`notebook_data_frame_name.to_csv('saved_csv/your_file_title.csv')`  

  * 'notebook_data_frame_name' should be replaced with the name of your DataFrame. For example, if you had ran the following lines;  

`piece = importScore('https://crimproject.org/mei/CRIM_Model_0008.mei')`  
`mel = piece.melodic()`  

  * You could then save this model's melodic interval data to a CSV file with the file name 'CRIM_Model_0008.csv' by running the following:  

`mel.to_csv('saved_csv/CRIM_Model_0008.csv')`  

### Export to Excel:  

  * Alternatively, a DataFrame can be saved as an Excel file with the following command lines in order, once again replacing 'file_name.xlsx' with your desired file name, replacing 'Sheet1' with your desired sheet name **(in quotes)**, and replacing 'frame_name' in the second line with the name of your DataFrame **(without quotes)**, which was be 'mel' in the last example:  

`writer = pd.ExcelWriter('saved_csv/file_name.xlsx', engine='xlsxwriter')`  
`frame_name.to_excel(writer, sheet_name='Sheet1')`  
`writer.save()`  

Substituting the information from the first example, we could write that same DataFrame to an Excel sheet with the following commands:  

`writer = pd.ExcelWriter('saved_csv/CRIM_Model_0008.xlsx', engine = 'xlsxwriter')`  
`mel.to_excel(writer, sheet_name = 'CRIM Model 0008')`  
`writer.save()`  
 
## Help and Documentation

  * The documentation associated with each function can be read with a line of the following sample format:  
`print(piece.notes.__doc__)`
  * This line would print out the documentation (`.__doc__`) associated with the function `notes()`, a function applicable to the object `piece`
  * Note that to print the documentation for a function, some object able to utilize that function must be used in the command line as shown above

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