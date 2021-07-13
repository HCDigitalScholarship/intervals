from main_objs import *
from test_constants import *

def get_crim_model(file):
    root = "https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/"
    return CorpusBase([root + file]).scores[0]

def validate_ngrams_last_offsets(model, df, n, how='columnwise', other=None, held='Held',
                                 exclude=['Rest'], interval_settings=('d', True, True), unit=0):
    """
    Objective: Make sure that ngrams' offsets parameter is correct by checking the nrgams
    grouped by the offsets of the first notes against the nrgams grouped by the offsets
    of the last notes. If we receive the same ngrams in both cases, then the output is correct
    """

    df1 = model.getNgrams(df=df, n=n, how=how, other=other, held=held,
                  exclude=exclude, interval_settings=interval_settings, unit=unit,
                  offsets='first')

    df2 = model.getNgrams(df=df, n=n, how=how, other=other, held=held,
                  exclude=exclude, interval_settings=interval_settings, unit=unit,
                  offsets='last')

    # compare patterns
    df1_cols = [df1.iloc[:, i] for i in range(len(df1.columns))]
    df2_cols = [df1.iloc[:, i] for i in range(len(df2.columns))]

    # making sure that we would get the same pattern whichever offsets we choose.
    for i in range(len(df1.columns)):
        df1_cols[i].dropna(inplace=True)
        df2_cols[i].dropna(inplace=True)

        df1_cols[i].reset_index(drop=True)
        df2_cols[i].reset_index(drop=True)

        assert(df1_cols[i].equals(df2_cols[i]))

"""
def has_diff_measure_offsets(model):
    
    # Search for different measure offsets across voices
    # get columns
    measures = model.getMeasure()
    # compare each columns, return FALSE for strange columns
    voices = measures.columns
    first_voice = measures[voices[0]]

    for voice in voices[1:]:
        if not first_voice.equals(measures[voice]):
            return True
    return False
"""

def test_ngrams_last_offsets():
    """
    For a long and short, sampled and not sampled ngrams with different interval
    settings, test if they output the same ngrams when either offsets='first' and
    offset='last' is used.
    """

    for i in range(len(FILES_FEW)):
        model = get_crim_model(FILES_FEW[i])
        mel = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
        validate_ngrams_last_offsets(model, mel, 5)
        
        # modules mode
        validate_ngrams_last_offsets(model, df=None, n=10, how='modules')

        # n=-1 mode
        validate_ngrams_last_offsets(model, mel, -1)

def test_get_measure():
    """
    Validate getMeasure() by making sure that the measures are the same
    as the hardcoded values for each files
    """

    for i in range(len(FILES_FEW)):
        file = FILES_FEW[i]
        model = get_crim_model(file)

        # check measures
        ms = model.getMeasure()
        hardcoded_ms = pd.DataFrame(FILES_FEW_MS[i])

        for row in hardcoded_ms.index:
            for col in hardcoded_ms.columns:
                assert hardcoded_ms.loc[row, col] == ms.loc[row, col]

def test_get_time_signature():
    """
    Validate getTimeSignature by making sure that the time signature are the same
    as the hardcoded values for each files
    """

    for i in range(len(FILES_FEW)):
        model = get_crim_model(FILES_FEW[i])

        # check measures
        ts = model.getTimeSignature()
        hardcoded_ts = pd.DataFrame(FILES_FEW_TS[i])

        for row in hardcoded_ts.index:
            for col in hardcoded_ts.columns:
                assert hardcoded_ts.loc[row, col] == ts.loc[row, col]

def test_get_sounding_count():
    """
    Validate getSoundingCount() by making sure that the sounding count are the same
    as the hardcoded values for each files
    """

    for i in range(len(FILES_FEW)):
        model = get_crim_model(FILES_FEW[i])

        # check measures
        sc = model.getSoundingCount()
        hardcoded_sc = pd.Series(FILES_FEW_SC[i])

        for row in hardcoded_sc.index:
            assert hardcoded_sc.loc[row] == sc.loc[row]

def test_intervals_settings():
    # harmonic
    # TODO hardcoded harmonic tests
    # melodic
    # TODO hardcoded melodic test
    pass