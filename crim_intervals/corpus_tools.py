# these tools work with existing Crim Intervals classes and functions.

# each takes in a corpus object, along with various arguments

# typical usage:

# 
# import crim_intervals.corpus_tools as corpus_tools
# corpus_tools.corpus_notes(corpus, combine_unisons_choice=True, combine_rests_choice=False)

from crim_intervals import ImportedPiece


def corpus_notes(corpus, combine_unisons_choice=True, combine_rests_choice=False):
    """
    Creates table of notes and rests in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    combine_unisons_choice : bool
        Choice for combining unisons
    combine_rests_choice : bool
        Choice for combining rests

    Returns:
    --------
    pd.DataFrame
        DataFrame containing processed notes
    """
    func = ImportedPiece.notes  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'combineUnisons': combine_unisons_choice, 'combineRests': combine_rests_choice}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=True)
    
    
    nr = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    nr = nr[cols_to_move + [col for col in nr.columns if col not in cols_to_move]]
    return nr


# counting notes (just the number of occurences

def corpus_note_scaled(corpus, combine_unisons_choice=True, combine_rests_choice=False):
    """
    Count occurrences of notes and rests in a corpus, including scaled counts
    Must include: `from collections import Counter` as part of import statement

    Parameters:
    -----------
    corpus : object
        Corpus object
    combine_unisons_choice : bool
        Choice for combining unisons
    combine_rests_choice : bool
        Choice for combining rests

    Returns:
    --------
    pd.DataFrame
        DataFrame containing note counts
    """
    func = ImportedPiece.notes  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'combineUnisons': combine_unisons_choice, 
                                          'combineRests': combine_rests_choice}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=True)
    final_list_dfs = []
    for df in list_of_dfs:
        # clean up
        df = df.map(lambda x: '' if x == 'Rest' else x).fillna('')
        df['1'] = df['1'].map(lambda x: x[:-1])
        df['2'] = df['2'].map(lambda x: x[:-1])
        df = df[df.index != '']
        
        stacked_df = df.set_index(['Composer', 'Title', 'Date']).stack()
        counted_notes = Counter(stacked_df)
        first_key = next(iter(counted_notes))
        counted_notes.pop(first_key)

        total_n = sum(counted_notes.values())

        counted_notes = pd.Series(counted_notes).to_frame('count').sort_index()
        counted_notes['scaled'] = counted_notes['count'] / total_n
        counted_notes['scaled'] = counted_notes['scaled'].round(2)
        counted_notes.rename(columns={"count": "count", "scaled": "scaled_count"}, inplace=True)

        counted_notes['Composer'] = df.iloc[0]['Composer']
        counted_notes['Title'] = df.iloc[0]['Title']
        counted_notes = counted_notes[counted_notes.index != '']
        final_list_dfs.append(counted_notes)
        
    corpus_notes_counts = pd.concat(final_list_dfs)

    return corpus_notes_counts
# notes weighted by duration

def corpus_note_durs(corpus, pitch_class=True):
    """
    Calculate durations of notes in a corpus.
    Uses helper function extract_letter to extract the letter part of the note as pitch class (optional)

    Parameters:
    -----------
    corpus : object
        Corpus object
    pitch_class : bool, optional
        Whether to use pitch class instead of full note names (default: True)

    Returns:
    --------
    pd.DataFrame
        DataFrame containing note durations
    """

    func = ImportedPiece.notes  # <- NB there are no parentheses here
    list_of_note_dfs = corpus.batch(func = func,  
                                    metadata=True)
    func_voices = ImportedPiece.numberParts
    list_of_note_dfs = corpus.batch(func = func_voices,
                                   metadata=False,
                                   kwargs = {'df' : list_of_note_dfs})
    func2 = ImportedPiece.durations  # <- NB there are no parentheses here
    list_of_dur_dfs = corpus.batch(func = func2,  
                                    metadata=False)
    list_of_dur_dfs = corpus.batch(func = func_voices,
                                   metadata=True,
                                  kwargs = {'df' : list_of_dur_dfs})
    func3 = ImportedPiece.final
    list_of_finals = corpus.batch(func = func3,
                                  metadata=True)
    
    zipped_dfs = zip(list_of_note_dfs,  list_of_dur_dfs, list_of_finals)
    
    
    note_dur_dfs = []
    for a, b, c in zipped_dfs:
        
        id_columns = [col for col in a.columns if col not in ['1', '2', '3', '4', '5', '6', '7', '8']]
        var_cols = [col for col in a.columns if col in ['1', '2', '3', '4', '5', '6', '7', '8']]
    
        # Now melt the DataFrame
        melted_notes = a.melt(
            id_vars=id_columns,
            value_vars=var_cols,
            var_name='Voice',
            value_name='Notes'
        )
        melted_durs = b.melt(
            id_vars=id_columns,
            value_vars=var_cols,
            var_name='Voice',
            value_name='Durs'
        )
        # get metadata
        metadata = id_columns
        
        note_dur = pd.merge(melted_notes, melted_durs, left_index=True, right_index=True, suffixes=('', '_y'))
        note_dur = note_dur.dropna(subset=['Notes', 'Durs'])

        # option to extract pitch class
        if pitch_class == True:
            note_dur['Notes'] = note_dur['Notes'].apply(extract_letter)
        else:
            note_dur['Notes'] = note_dur['Notes']
        note_dur['Final'] = c

        # we always extract the letter from the final
        note_dur['Final'] = note_dur['Final'].apply(extract_letter)
        note_dur_final = note_dur
        
        # Drop columns ending with _y
        note_dur_final = note_dur_final.drop(columns=[col for col in note_dur.columns if col.endswith('_y')])
        note_dur_final = note_dur_final.dropna(subset=['Notes', 'Durs'])
        note_dur_final['Durs'] = note_dur_final['Durs'].map(float)
        note_dur_dfs.append(note_dur_final)
             
    corpus_note_durs = pd.concat(note_dur_dfs)
    return corpus_note_durs

# melodic intervals in a corpus
def corpus_mel(corpus, kind_choice='d', compound_choice=True, directed_choice=True):
    """
    Generate melodic intervals in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    kind_choice : str
        Kind of intervals to generate
    compound_choice : bool
        Whether to allow compound intervals
    directed_choice : bool
        Whether to allow directed intervals

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated melodic intervals
    """
    func = ImportedPiece.melodic  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'kind': kind_choice, 
                                         'compound' : compound_choice,
                                         'directed': directed_choice}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=True)
    
    
    mel = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    mel = mel[cols_to_move + [col for col in mel.columns if col not in cols_to_move]]
    return mel

# harmonic intervals in a corpus
def corpus_har(corpus, kind_choice='d', compound_choice=True, directed_choice=True):
    """
    Generate harmonic intervals in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    kind_choice : str
        Kind of intervals to generate
    compound_choice : bool
        Whether to allow compound intervals
    directed_choice : bool
        Whether to allow directed intervals

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated harmonic intervals
    """
    func = ImportedPiece.harmonic  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'kind': kind_choice, 
                                         'compound' : compound_choice,
                                         'directed': directed_choice},
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=True)
    
    
    har = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    har = har[cols_to_move + [col for col in har.columns if col not in cols_to_move]]
    return har

# contrapuntal grams in a corpus.  These are contrapuntal by default
def corpus_contrapuntal_ngrams(corpus, ngram_length):
    """
    Generate n-grams in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    ngram_length : int
        Length of n-grams to generate
    combine_rests_choice : bool
        Whether to combine rests

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated n-grams
    """
    func = ImportedPiece.ngrams  # <- NB there are no parentheses here
    list_of_dfs = corpus.batch(func = func, 
                                kwargs = {'n': ngram_length}, 
                                metadata=False)
    func1 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func1,
                               kwargs = {'df' : list_of_dfs},
                               metadata=True)
    
    
    ngrams = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    ngrams = ngrams[cols_to_move + [col for col in ngrams.columns if col not in cols_to_move]]
    return ngrams

# melodic grams in a corpus. 
def corpus_melodic_ngrams(corpus, ngram_length=4, kind_choice = 'd', end_choice=False, metadata_choice=True, include_offset=False
 ):
    """
    Generate n-grams in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    ngram_length : int
        Length of n-grams to generate; 4 by default
    kind_choice : str
        'd' for diatonic, by default
    end_choice: bool
        False to give position as of the first note of the interval
    metadata: bool
        whether to include composer, title, and data
    

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated n-grams
    """
    func1 = ImportedPiece.melodic
    list_of_dfs = corpus.batch(func=func1, kwargs={'kind': kind_choice, 'end': end_choice}, metadata=False)
    func2 = ImportedPiece.ngrams
    list_of_melodic_ngrams = corpus.batch(func=func2, kwargs={'n': ngram_length, 'df': list_of_dfs}, metadata=False)
    func3 = ImportedPiece.detailIndex
    list_of_detail_index = corpus.batch(func=func3, kwargs={'offset': include_offset,'df': list_of_melodic_ngrams}, metadata=False)
    func4 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func4,
                               kwargs = {'df' : list_of_dfs},
                               metadata=metadata_choice)

    corpus_mel_ngrams = pd.concat(list_of_detail_index)
    
    
    corpus_mel_ngrams = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    corpus_mel_ngrams = corpus_mel_ngrams[cols_to_move + [col for col in corpus_mel_ngrams.columns if col not in cols_to_move]]
    return corpus_mel_ngrams

# melodic grams with durational ration in a corpus. 
def corpus_melodic_durational_ratios_ngrams(corpus, ngram_length=4, 
                                            end_choice = False, 
                                            kind_choice = 'd', 
                                            metadata_choice=True, 
                                            include_offset=False
 ):
    """
    Generate n-grams in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    ngram_length : int
        Length of n-grams to generate; 4 by default
    kind_choice : str
        'd' for diatonic, by default
    end_choice: bool
        False to give position as of the first note of the interval
    metadata: bool
        whether to include composer, title, and data
    

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated n-grams
    """
    func1 = ImportedPiece.melodic
    list_of_mel_dfs = corpus.batch(func=func1, kwargs={'kind': kind_choice, 'end' : end_choice}, metadata=False)
    func2 = ImportedPiece.numberParts
    list_of_mel_dfs = corpus.batch(func = func2,
                               kwargs = {'df' : list_of_mel_dfs},
                               metadata=metadata_choice)
    func3 = ImportedPiece.durationalRatios
    list_of_dur_rat_dfs = corpus.batch(func=func3, kwargs={'end' : end_choice}, metadata=False)
    list_of_dur_rat_dfs = corpus.batch(func = func2,
                               kwargs = {'df' : list_of_dur_rat_dfs},
                               metadata=False)
    list_of_dur_rat_dfs_rounded = []
    for df in list_of_dur_rat_dfs:
        df_rounded = df.apply(lambda x: x.astype('float64')).round(2)

        list_of_dur_rat_dfs_rounded.append(df_rounded)
    func4 = ImportedPiece.ngrams
    list_of_mel_dur_ngrams = corpus.batch(func=func4, kwargs={'n': ngram_length, 
                                                              'df': list_of_mel_dfs, 
                                                              'other' : list_of_dur_rat_dfs_rounded}, metadata=False)
    list_of_mel_dur_rounded_no_tuple = []
    for df in list_of_mel_dur_ngrams:
        df_joined = df.applymap(lambda x: '_'.join(x) if isinstance(x, tuple) else x)

        list_of_mel_dur_rounded_no_tuple.append(df_joined)


    
    func5 = ImportedPiece.detailIndex
    list_of_detail_index = corpus.batch(func=func5, kwargs={'offset': include_offset, 
                                                            'df': list_of_mel_dur_rounded_no_tuple}, 
                                                            metadata=metadata_choice)
    

    corpus_mel_dur_rat_ngrams = pd.concat(list_of_detail_index)

    cols_to_move = ['Composer', 'Title', 'Date']
    corpus_mel_dur_rat_ngrams = corpus_mel_dur_rat_ngrams[cols_to_move + [col for col in corpus_mel_dur_rat_ngrams.columns if col not in cols_to_move]]
    return corpus_mel_dur_rat_ngrams

# harmonic grams in a corpus. 
def corpus_harmonic_ngrams(corpus, ngram_length=4, kind_choice = 'd', metadata_choice=True, include_offset=False
 ):
    """
    Generate n-grams in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    ngram_length : int
        Length of n-grams to generate; 4 by default
    kind_choice : str
        'd' for diatonic, by default
    end_choice: bool
        False to give position as of the first note of the interval
    metadata: bool
        whether to include composer, title, and data
    

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated n-grams
    """
    func1 = ImportedPiece.melodic
    list_of_dfs = corpus.batch(func=func1, kwargs={'kind': kind_choice}, metadata=False)
    func2 = ImportedPiece.ngrams
    list_of_harmonic_ngrams = corpus.batch(func=func2, kwargs={'n': ngram_length, 'df': list_of_dfs}, metadata=False)
    func3 = ImportedPiece.detailIndex
    list_of_detail_index = corpus.batch(func=func3, kwargs={'offset': include_offset,'df': list_of_harmonic_ngrams}, metadata=False)
    func4 = ImportedPiece.numberParts
    list_of_dfs = corpus.batch(func = func4,
                               kwargs = {'df' : list_of_dfs},
                               metadata=metadata_choice)

    corpus_har_ngrams = pd.concat(list_of_detail_index)
    
    
    corpus_har_ngrams = pd.concat(list_of_dfs)
    cols_to_move = ['Composer', 'Title', 'Date']
    corpus_har_ngrams = corpus_har_ngrams[cols_to_move + [col for col in corpus_har_ngrams.columns if col not in cols_to_move]]
    return corpus_har_ngrams


# sonorities plus bassline grams in a corpus. 
def corpus_sonority_ngrams(corpus, 
                           ngram_length=4, 
                           metadata_choice=True, 
                           include_offset=False,
                           include_progress=True,
                           compound=True,
                           sort=False,
                           minimum_beat_strength = 0.0
 ):
    """
    Generate sonority n-grams in a corpus.

    Parameters:
    -----------
    corpus : object
        Corpus object
    ngram_length : int
        Length of n-grams to generate; 4 by default
    metadata: bool
        whether to include composer, title, and data
    include_offset: bool
        whether to include offset along with measure and beat
    include_progress: bool
        whether to include progress column
    minimum_beat_strength: float
        minimum value for beat strength to report
    sort: bool
        if true, sorts intervals from largest to smallest; no unison
    

    Returns:
    --------
    pd.DataFrame
        DataFrame containing generated n-grams
    """

    func0 = ImportedPiece.beatStrengths
    list_of_beat_strength_dfs = corpus.batch(func0, metadata=False)

    func1 = ImportedPiece.sonorities
    list_of_sonority_dfs = corpus.batch(func=func1, 
                                        kwargs={'sort': sort, 'compound': compound}, 
                                        metadata=False)
    paired_sonority_bs_dfs = zip(list_of_sonority_dfs,list_of_beat_strength_dfs)

    # filtering for beat strength
    list_filtered_sonority_dfs = []
    for pair in paired_sonority_bs_dfs:
        son = pair[0]
        bs = pair[1]
        strong_beat_positions = bs[(bs > minimum_beat_strength).any(axis=1)].index
        filtered_sonorities = son[son.index.isin(strong_beat_positions)]
        list_filtered_sonority_dfs.append(filtered_sonorities)

    func2 = ImportedPiece.lowLine
    list_of_lowLine_dfs = corpus.batch(func=func2, metadata=False)
    paired_lowline_bs_dfs = zip(list_of_lowLine_dfs,list_of_beat_strength_dfs)

    list_of_fitered_lowLine_dfs = []
    for pair in paired_lowline_bs_dfs:
        low = pair[0]
        bs = pair[1]
        strong_beat_positions = bs[(bs > minimum_beat_strength).any(axis=1)].index
        filtered_lowline = low[low.index.isin(strong_beat_positions)]
        list_of_fitered_lowLine_dfs.append(filtered_lowline)

    # create df with both filtered sonorities and lowline
    paired_dfs = zip(list_filtered_sonority_dfs, list_of_fitered_lowLine_dfs)
    list_combined_dfs = []
    for pair in paired_dfs:
        sonorities_with_bass = pd.merge(pair[0], pair[1], left_index=True, right_index=True, how='left')
        list_combined_dfs.append(sonorities_with_bass)
        for df in list_combined_dfs:
            df['Low Line'].fillna('Held', inplace=True)
            df['Low_Sonority'] = df['Low Line'] + "_" + df['Sonority']


    func3 = ImportedPiece.ngrams
    list_of_son_bass_ngrams_dfs = corpus.batch(func=func3, 
                                               kwargs={'n': ngram_length, 'df': list_combined_dfs}, 
                                               metadata=False)
    func4 = ImportedPiece.detailIndex
    list_of_detail_index_dfs = corpus.batch(func=func4, 
                                            kwargs={'offset': include_offset,'df': list_of_son_bass_ngrams_dfs, 'progress' : include_progress}, 
                                            metadata=True)
    func5 = ImportedPiece.numberParts
    list_of_numberParts_dfs = corpus.batch(func = func5,
                               kwargs = {'df' : list_of_detail_index_dfs},
                               metadata=metadata_choice)
    for df in list_of_numberParts_dfs:
        if len(df) > 0:
            df['Low_Sonority'] = df['Low_Sonority'].apply(lambda x: '_'.join(x) if isinstance(x, tuple) else x)

    corpus_son_bass_ngrams = pd.concat(list_of_numberParts_dfs)
    
    cols_to_move = ['Composer', 'Title', 'Date']
    corpus_son_bass_ngrams = corpus_son_bass_ngrams[cols_to_move + [col for col in corpus_son_bass_ngrams.columns if col not in cols_to_move]]
    return corpus_son_bass_ngrams


def corpus_cadences(corpus):

    #select function.  remember to omit "()"
    func = ImportedPiece.cadences

    #run function on each piece; be sure to include keyword arguments
    list_of_dfs = corpus.batch(func = func, kwargs = {'keep_keys': True}, metadata = True)

    #concatenate the resulting dataframes into one
    corpus_cadences = pd.concat(list_of_dfs, ignore_index = False)

    # new order for columns:
    col_list = ['Composer', 'Title', 'Measure', 'Beat', 'Pattern', 'Key', 'CadType', 'Tone','CVFs',
                    'LeadingTones', 'Sounding', 'Low','RelLow','RelTone',
                    'Progress','SinceLast','ToNext']

    corpus_cadences = corpus_cadences[col_list]

    # show the results
    return corpus_cadences

def corpus_presentation_types(corpus, 
                              limit_to_entries=True, 
                              head_flex=1, 
                              body_flex=0,
                              include_hidden_types=False,
                              combine_unisons=True,
                              melodic_ngram_length=4,
                              kind='d',
                              end=False
                              ):
    # indicate the function
    func = ImportedPiece.presentationTypes  # <- NB there are no parentheses here

    #provide the kwargs
    kwargs = {'limit_to_entries': limit_to_entries, 
              'head_flex' : head_flex,
                                        'body_flex' : body_flex,
                                        'include_hidden_types' : include_hidden_types,
                                        'combine_unisons' : combine_unisons,
                                        'melodic_ngram_length' :  melodic_ngram_length,
                                        'kind': kind,
                                        'end': end}

    #build a list of dataframes, one for each piece in the corpus
    list_of_dfs = corpus.batch(func, kwargs, metadata=True)

    #concatenate the list to a single dataframe
    corpus_presentation_types = pd.concat(list_of_dfs)

    return corpus_presentation_types

