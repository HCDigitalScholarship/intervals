# Model Finder

## Find Models by Comparing Soggetti and Modules

The `modelFinder` methods works with a corpus of pieces to detect shared patterns.  Here we describe ways of comparing **melodic ngrams** ('soggetti') and **contrapuntal modules** (also types of ngrams, as explained elswhere in the these tutorials). These two types of comparisons are useful as indicators of both similarity and difference across a matrix of pieces.  Of course there are other ways of considering such connections.

The `modelFinder` method provides a **macro-level view** of the percentages of soggetti (melodic ngrams) or contrapuntal modules shared across a corpus. The method first finds all the "entry" soggetti in each piece in your corpus, then measures the percentage of each model found in a corresponding Mass movement. The resulting 'cross_plot' is a driving distance style of results (from 0 to 1) showing the relatedness of each pair of movements.

The *specific number of times* each soggetto (or module) appears is not considered, but rather the *percentage of unique entries* that each pair of pieces shares*.

## Melodic Ngrams (Soggetti)  as Similarity Matrix

This method uses 'entries' (that is soggetti limited to those after section breaks, fermatas, or rests).  

The default length of soggetti is 4, but it can be set to any length by passing `n=6` (for example).

Here we pass an entire corpus to the tool, which case *every piece* will be *compared to every other* as a 'cross plot'.  

Note that a value of "1.00" in the cross plot means that 100% of the 'entry' soggetti are shared by the corresponding piece.  When comparing every piece to every other piece, it is thus normal for every piece to be compared to itself (and expected result of that is naturally "1.00").

    corpus_list = ['https://crimproject.org/mei/CRIM_Model_0008.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_1.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_2.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_3.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_4.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_5.mei']


    corpus = CorpusBase(corpus_list)
    soggetto_cross_plot = corpus.modelFinder(n=6)
    soggetto_cross_plot

![modelFinder_1.png](images%2FmodelFinder_1.png)

It is also possible to divide your corpus into two segments:  models and Masses, for instance (of course you could arbitrarily assign any pieces to these specific segments in order to compare one subgroup of pieces against another).  Doing so will result in a simpler table than for the previous method, comparing each model to each Mass movement (but not all pieces to each other).


Typical Use:


    # define the model list
    model_list = ['https://crimproject.org/mei/CRIM_Model_0010.mei', 'https://crimproject.org/mei/CRIM_Model_0011.mei', 'https://crimproject.org/mei/CRIM_Model_0014.mei']
    
    # and the mass list:
    mass_list = ['https://crimproject.org/mei/CRIM_Mass_0008_1.mei', 'https://crimproject.org/mei/CRIM_Mass_0008_2.mei', 'https://crimproject.org/mei/CRIM_Mass_0008_3.mei']
    
    # now build each of these lists as a pair of corpora:
    mod_corp = CorpusBase(model_list)
    mass_corp = CorpusBase(mass_list)
    
    # run the comparison, passing in both sets as parameters:
    soggetto_cross_plot = mod_corp.modelFinder(masses=mass_corp, models=mod_corp)

    # view the result
    soggetto_cross_plot


### How to Read the Results:

* As you read across, you will see the percentage of melodies in the row value that come from the corresponding column value.

![model_finder_3.png](images%2Fmodel_finder_3.png)

### Heatmap Display of Results


It is possible to display the cross-plot matrix as a heatmap.  Darker colors represent stronger relationships between the corresponding pairs of pieces on the grid.  

Note that if you are comparing every piece to every other piece, all the comparisons of a piece to itself will appear as the darkest blue.  A diagonal band of these 'identities' is typical of such comparisons.

Typical Use:


    dataplot = sns.heatmap(soggetto_cross_plot, cmap="YlGnBu", annot=False)
    plt.show()

Results for every piece to every other piece (note diagonal bar of 'self to self'):

![modelFinder_2.png](images%2FmodelFinder_2.png)

Results for "split corpus" comparing models to masses (no comparison of 'self to self'):

![model_Finder_4.png](images%2Fmodel_Finder_4.png)

---

## Contrapuntal (Modular) Ngrams as Similarity Matrix

**Contrapuntal Modules** are 'ngrams' that represent the motion of a pair of voices.  

This tool finds the *patterns between every pair of voices*, then filters these to correspond to the moments of the 'entries'.  So it tells us not only that there are shared melodies, but *what is happening to the melodies in their contrapuntal context*.  We might consider this a measure of 'transformation'.

The `moduleFinder`  method identifies all of the `contrapuntal-modular ngrams` in each piece that **coincide with the melodic entries**.  These are the modules found in _all_ voices around the moment of the given melodic entry, so they will
include both the entries and other soggetti, too.

Lists of unique contrapuntal-ngrams are then compared across the corpus, resulting in a matrix of values.

This method in turn returns a "driving distance table" showing how likely each model was a source for each mass. This
is represented by a score 0-1 where 0 means that this relationship was highly unlikely
and 1 means that the the two are highly likely to be related in this way (or that a
piece was compared to itself). 

Specifically, **the value is the percentage of each piece's
modular ngrams (the ones that occur at the moment of the entries) can be found in each of the other pieces in the corpus.**

Note that a value of "1.00" in the cross plot means that 100% of the modules associated with the given soggetto are shared by the corresponding piece.  When comparing every piece to every other piece, it is thus normal for every piece to be compared to itself (and expected result of that is naturally "1.00").

### Typical Use


    corpus = CorpusBase(corpus_list)
    module_matrix = corpus.moduleFinder()
    module_matrix


### Split Corpus for Mass and Model:


    mod_corp = CorpusBase(model_list)
    mass_corp = CorpusBase(mass_list)
    module_matrix = mod_corp.moduleFinder(masses=mass_corp, models=mod_corp)
    module_matrix


###  How to Read the Results:
    - As you read across, you will see the percentage of modular ngrams in the row value that come from the corresponding column value.  

See example for soggetti above.
   
### Heatmap Display of Matrix

See explanation above.


    dataplot = sns.heatmap(module_matrix, cmap="YlGnBu", annot=False)
    plt.show()

![model_Finder_5.png](images%2Fmodel_Finder_5.png)

### Compare the Differences between the Model Finder and Module Finder outputs

This shows the movement between the two matching tables.  The higher the number, the more transformation is apparent.

    comparison_table = module_matrix.compare(model_matrix).round(2)
    comparison_table


### Map of 'transformation'.  Dark blue = places where the differences between melodic and modular borrowing are greatest!

    dataplot = sns.heatmap(comparison_table, cmap="YlGnBu", annot=False)
    plt.show()

![model_Finder_6.png](images%2Fmodel_Finder_6.png)

---

## A Closer Look:  The Micro Level

### Here we explore *where* and *how* the shared melodies (or modules) are presented in each piece

* Load a specific pair of closely related pieces from your corpus
* Find exactly which melodic entries are shared
* Find out *where* these melodies occur in each piece
* Check the Fuga, PEN, and ID Presentation Types to see how the melodies are treated in each piece.  Pick one or two melodies (and Presentation Types) as examples to describe.


    corpus_list = ['https://crimproject.org/mei/CRIM_Model_0008.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_1.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_2.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_3.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_4.mei', 'https://crimproject.org/mei/CRIM_Mass_0005_5.mei']


### Specify the Model

    model = corpus_list[0] # <== the model will be score "0" in the previous list
    model = importScore(model)

### Specify the Mass Movement(s)

    mass_movement = corpus_list[1] # <== select the index number of your mass movement from the corpus.  "1" is the Kyrie, "5" is the Agnus
    mass_movement = importScore(mass_movement)
    print(model.metadata, mass_movement.metadata)


![Model_Finder_11.png](images%2FModel_Finder_11.png)


### Get the Entries and Detailed Index for A Pair of Pieces


    # set parameters:
    thematic = True
    anywhere = True
    offset = True
    progress = True
    n = 4

For the model:


    model_entries = model.entries(thematic=thematic, anywhere=anywhere, n=n)
    model_entries_det = model.detailIndex(model_entries, offset=offset, progress=progress)
    model_entries_det

For the Mass movement:

    mass_movement_entries = mass_movement.entries(thematic=thematic, anywhere=anywhere, n=n)
    mass_movement_entries_det = mass_movement.detailIndex(mass_movement_entries, offset=offset, progress=progress)

Check the detailed view as needed for each:

    print(model_entries_det, mass_movement_entries_det)

![model_finder_7.png](images%2Fmodel_finder_7.png)

### Find the nGrams shared by your pieces


    model_entries = model.entries(thematic=True, anywhere=True, n=4)
    model_entries_stack = model_entries.stack()
    mass_movement_entries = mass_movement.entries(thematic=True, anywhere=True, n=4)
    mass_movement_entries_stack = mass_movement_entries.stack()
    shared_entries = list(set(mass_movement_entries_stack).intersection(model_entries_stack))
    shared_entries = shared_entries[:]
    shared_entries


###  Make Heatmaps of Shared Entries in Two Pieces

* Let's look at **where** the shared melodies appear in each of your pieces.
The Model Heatmap:


    nr = model.notes(combineUnisons=True) 
    mel = model.melodic(df=nr, kind='d', compound=True, unit=0, end=False)
    mel_ngrams = model.ngrams(df=mel, n=4)
    entry_ngrams = model.entries(df=mel, n=4)
    mel_ngrams_duration = model.durations(df=mel, n=4, mask_df=entry_ngrams)
    viz.plot_ngrams_heatmap(entry_ngrams, mel_ngrams_duration, selected_patterns=shared_entries, voices=[], includeCount=False)

![mode_Finder_9.png](images%2Fmode_Finder_9.png)

The Mass Movement Heatmap


    nr = mass_movement.notes(combineUnisons=True) 
    mel = mass_movement.melodic(df=nr, kind='d', compound=True, unit=0, end=False)
    mel_ngrams = mass_movement.ngrams(df=mel, n=4)
    entry_ngrams = mass_movement.entries(df=mel, n=4)
    mel_ngrams_duration = mass_movement.durations(df=mel, n=4, mask_df=entry_ngrams)
    viz.plot_ngrams_heatmap(entry_ngrams, mel_ngrams_duration, selected_patterns=shared_entries, voices=[], includeCount=False)

![model_Finder_10.png](images%2Fmodel_Finder_10.png)

### Make the Short Lists of These Shared Ngrams and Their Offsets

For the model:

    model_short_list = model_entries_det[model_entries_det.isin(shared_entries)].dropna(how='all').stack()
    model_offsets_of_shared_entries = model_short_list.index.get_level_values(2)
    model_offsets_of_shared_entries = model_offsets_of_shared_entries.unique()

For the mass movement:

    mass_movement_short_list = mass_movement_entries_det[mass_movement_entries_det.isin(shared_entries)].dropna(how='all').stack()
    mass_movement_offsets_of_shared_entries = mass_movement_short_list.index.get_level_values(2)
    mass_movement_offsets_of_shared_entries = mass_movement_offsets_of_shared_entries.unique()

    model_offsets_of_shared_entries

![model_Finder_8.png](images%2Fmodel_Finder_8.png)

### Get Shared Entries as Presentation Types

* Note that not all shared entries will be used as Fuga, ID, and PEN but for those that appear in a pair of pieces, it can be informative to compare **how** they are treated!

Here we filter the PTypes to include ONLY those found in both the model and Mass movement.  First the model:


    model_p_types = model.presentationTypes(limit_to_entries = True,
                            body_flex = 0,
                            head_flex = 1,
                            include_hidden_types = False,
                            combine_unisons = True,
                           melodic_ngram_length = 4)
    
    model_shared_entry_ptypes = model_p_types[model_p_types.First_Offset.isin(model_offsets_of_shared_entries)]

And now for the Mass movement:


    mass_movement_p_types = mass_movement.presentationTypes(limit_to_entries = True,
                            body_flex = 0,
                            head_flex = 1,
                            include_hidden_types = False,
                            combine_unisons = True,
                           melodic_ngram_length = 4)
    
    
    mass_movement_shared_entry_ptypes = mass_movement_p_types[mass_movement_p_types.First_Offset.isin(mass_movement_offsets_of_shared_entries)]

And finally combine the two outputs as one dataframe showing all of the presentation types that involve the *shared entries* identified above:

    combined_ptypes = pd.concat([model_shared_entry_ptypes, mass_movement_shared_entry_ptypes])
    combined_ptypes.head()

![model_Finder_12.png](images%2Fmodel_Finder_12.png)

Sort the Results so we see the Shared Melodies Together

    combined_ptypes.sort_values('Soggetti')

It would also be possible to print With Verovio. Here you will need to send one piece at a time, using the output from above:


    model.verovioPtypes(mass_movement_p_types)



---

## Sections in this guide

  * [01_Introduction_and_Corpus](01_Introduction_and_Corpus.md)
  * [02_NotesAndRests](02_NotesAndRests.md)
  * [03_Durations.md](03_Durations.md)
  * [04_Time-Signatures](04_TimeSignatures.md)
  * [05_DetailIndex](05_DetailIndex.md)
  * [06_MelodicIntervals](06_MelodicIntervals.md)
  * [07_HarmonicIntervals](07_HarmonicIntervals.md)
  * [08_Modules](08_Modules.md)
  * [09_Ngrams_Heatmaps](09_Ngrams_Heatmaps.md)
  * [10_Lyrics_Homorhythm](10_Lyrics_Homorhythm.md)
  * [11_Cadences](11_Cadences.md)
  * [12_Presentation_Types](12_Presentation_Types.md)
  * [13_Model_Finder](13_Model_Finder.md)
  * [14_Visualizations_Summary](14_Visualizations_Summary.md)
  * [15_Network_Graphs](15_Network_Graphs.md)
  * [16_Python_Basics](16_Python_Basics.md)
  * [17_Pandas](17_Pandas_Basics.md)