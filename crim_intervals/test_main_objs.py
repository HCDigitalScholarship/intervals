from .main_objs import *
from .test_constants import *


def get_crim_model(file):
    root = "https://crimproject.org/mei/"
    return importScore(root + file)

def test_get_semi_flat_parts_name():
    """
    Make sure that we could have correct names for each part.
    Somewhat make sure that we could get all parts in the score.
    """
    hardcoded_names = FILES_PART_NAMES
    for i in range(len(TEST_FILES)):
        file = TEST_FILES[i]
        model = get_crim_model(file)
        names = model._getPartNames()
        for j in range(len(hardcoded_names)):
            assert(names[j] == hardcoded_names[i][j])

def test_get_note_rests():
    for i in range(len(TEST_FILES)):
        hardcoded_nr = pd.DataFrame(FILES_NOTE_RESTS[i])
        file = TEST_FILES[i]
        model = get_crim_model(file)
        nr = model.notes()

        for row in hardcoded_nr.index:
            for col in hardcoded_nr.columns:
                assert (hardcoded_nr.loc[row, col] == nr.loc[row, col] or
                        (pd.isna(hardcoded_nr.loc[row, col]) and pd.isna(nr.loc[row, col])))


# TODO: fix this flawed test. You can't dropna from 1 column at a time in a dataframe because they just get filled back in if the missing indecies are in other columns
# def validate_ngrams_last_offsets(model, df, n, how='columnwise', other=None, held='Held',
#                                  exclude=['Rest'], interval_settings=('d', True, True), unit=0):
#     """
#     Objective: Make sure that ngrams' offsets parameter is correct by checking the nrgams
#     grouped by the offsets of the first notes against the nrgams grouped by the offsets
#     of the last notes. If we receive the same ngrams in both cases, then the output is correct
#     """

#     df1 = model.ngrams(df=df, n=n, how=how, other=other, held=held,
#                           exclude=exclude, interval_settings=interval_settings, unit=unit,
#                           offsets='first')

#     df2 = model.ngrams(df=df, n=n, how=how, other=other, held=held,
#                           exclude=exclude, interval_settings=interval_settings, unit=unit,
#                           offsets='last')

#     # compare patterns
#     df1_cols = [df1.iloc[:, i] for i in range(len(df1.columns))]
#     df2_cols = [df1.iloc[:, i] for i in range(len(df2.columns))]

#     # making sure that we would get the same pattern whichever offsets we choose.
#     for i in range(len(df1.columns)):
#         df1_cols[i].dropna(inplace=True)
#         df2_cols[i].dropna(inplace=True)

#         df1_cols[i].reset_index(drop=True)
#         df2_cols[i].reset_index(drop=True)

#         assert (df1_cols[i].equals(df2_cols[i]))


# def test_ngrams_last_offsets():
#     """
#     For a long and short, sampled and not sampled ngrams with different interval
#     settings, test if they output the same ngrams when either offsets='first' and
#     offset='last' is used.
#     """

#     for i in range(len(TEST_FILES)):
#         model = get_crim_model(TEST_FILES[i])
#         mel = model.melodic(kind='q', directed=True, compound=True, unit=0)
#         validate_ngrams_last_offsets(model, mel, 5)

#         # modules mode
#         validate_ngrams_last_offsets(model, df=None, n=10, how='modules')

#         # n=-1 mode
#         validate_ngrams_last_offsets(model, mel, -1)


def test_get_measure():
    """
    Validate measures() by making sure that the measures are the same
    as the hardcoded values for each files
    """

    for i in range(len(TEST_FILES)):
        file = TEST_FILES[i]
        model = get_crim_model(file)

        # check measures
        ms = model.measures()
        hardcoded_ms = pd.DataFrame(TEST_FILES_MS[i])

        for row in hardcoded_ms.index:
            for col in hardcoded_ms.columns:
                assert hardcoded_ms.loc[row, col] == ms.loc[row, col]


def test_get_time_signature():
    """
    Validate timeSignatures by making sure that the time signature are the same
    as the hardcoded values for each files
    """

    for i in range(len(TEST_FILES)):
        model = get_crim_model(TEST_FILES[i])

        # check measures
        ts = model.timeSignatures()
        hardcoded_ts = pd.DataFrame(TEST_FILES_TS[i])

        for row in hardcoded_ts.index:
            for col in hardcoded_ts.columns:
                assert hardcoded_ts.loc[row, col] == ts.loc[row, col]


def test_get_sounding_count():
    """
    Validate soundingCount() by making sure that the sounding count are the same
    as the hardcoded values for each files
    """

    for i in range(len(TEST_FILES)):
        model = get_crim_model(TEST_FILES[i])

        # check measures
        sc = model.soundingCount()
        hardcoded_sc = pd.Series(TEST_FILES_SC[i])

        for row in hardcoded_sc.index:
            assert hardcoded_sc.loc[row] == sc.loc[row]


def interval_settings_helper(df, hardcoded_df):
    for row in hardcoded_df.index:
        for col in hardcoded_df.columns:
            assert (hardcoded_df.loc[row, col] == df.loc[row, col] or
                    (pd.isna(hardcoded_df.loc[row, col]) == pd.isna(df.loc[row, col])))


def test_intervals_settings():
    for i in range(len(TEST_FILES)):
        file = TEST_FILES[i]
        model = get_crim_model(file)

        # harmonic
        harqtt = model.harmonic(kind='q', directed=True, compound=True)
        hardcoded_harqtt = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_QTT[i])
        interval_settings_helper(harqtt, hardcoded_harqtt)

        harqtf = model.harmonic(kind='q', directed=True, compound=False)
        hardcoded_harqtf = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_QTF[i])
        interval_settings_helper(harqtf, hardcoded_harqtf)

        hardtt = model.harmonic(kind='d', directed=True, compound=True)
        hardcoded_hardtt = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_DTT[i])
        interval_settings_helper(hardtt, hardcoded_hardtt)
        hardtf = model.harmonic(kind='d', directed=True, compound=False)
        hardcoded_hardtf = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_DTF[i])
        interval_settings_helper(hardtf, hardcoded_hardtf)
        hardft = model.harmonic(kind='d', directed=False, compound=True)
        hardcoded_hardft = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_DFT[i])
        interval_settings_helper(hardft, hardcoded_hardft)

        harztt = model.harmonic(kind='z', directed=True, compound=True)
        hardcoded_harztt = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_ZTT[i])
        interval_settings_helper(harztt, hardcoded_harztt)

        harctt = model.harmonic(kind='c', directed=True, compound=True)
        hardcoded_harctt = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_CTT[i])
        interval_settings_helper(harctt, hardcoded_harctt)
        harcff = model.harmonic(kind='c', directed=False, compound=False)
        hardcoded_harcff = pd.DataFrame.from_dict(TEST_FILES_HARMONIC_CFF[i])
        interval_settings_helper(harcff, hardcoded_harcff)

        # melodic
        # TODO hardcoded melodic test
