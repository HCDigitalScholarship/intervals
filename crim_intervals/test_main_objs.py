from .main_objs import *
from .test_constants import *


def get_crim_model(file):
    root = "https://crimproject.org/mei/"
    return importScore(root + file)


# Small, real pieces (rather than mocks) used for CorpusBase-level sanity tests,
# so those tests exercise real ImportedPiece/music21 behavior instead of the
# hand-rolled duck-typed DummyPiece below.
CORPUS_TEST_FILES = ['CRIM_Model_0001.mei', 'CRIM_Model_0002.mei']


def get_test_corpus():
    return CorpusBase([get_crim_model(file) for file in CORPUS_TEST_FILES])


class DummyPiece:
    def __init__(self, title, composer, notes_df=None, durations_df=None):
        self.metadata = {'title': title, 'composer': composer, 'date': None}
        self._notes_df = notes_df if notes_df is not None else pd.DataFrame({'1': ['C4', 'Rest']}, index=[0, 1])
        self._durations_df = durations_df if durations_df is not None else pd.DataFrame({'1': [1.0, 0.5]}, index=[0, 1])
        self.analyses = {}
        self.file_name = title.lower().replace(' ', '-')
        self.score = type('DummyScore', (), {'highestTime': 1.0})()

    def _getM21ObjsNoTies(self):
        return self._notes_df.copy()

    def _noteRestHelper(self, noteOrRest):
        if noteOrRest == 'Rest':
            return 'Rest'
        return str(noteOrRest)

    def _combineRests(self, col):
        return col.dropna()

    def _combineUnisons(self, col):
        return col.dropna()

    def numberParts(self, df):
        return df

    def _getPartNumberDict(self):
        return {'1': '1'}

    def notes(self, combineRests=True, combineUnisons=False):
        return self._notes_df.copy()

    def _durationHelper(self, col, n):
        col = col.dropna()
        vals = col.index[n:] - col.index[:-n]
        return pd.Series(vals, col.index[:-n])

    def durations(self, df=None, n=1, mask_df=None):
        if df is None:
            return self._durations_df.copy()
        return self._durations_df.copy()

    def final(self):
        return 'C4'


def test_tuple_helpers_convert_between_strings_and_lists():
    assert tuple_to_list(("A", "B", "C")) == ["A", "B", "C"]
    assert tuple_to_list("A, B, C") == ["A", "B", "C"]
    assert tuple_to_string(["A", "B", "C"]) == "A, B, C"
    assert tuple_to_string(("A", "B"), separator="/") == "A/B"


def test_sort_pitch_values_uses_custom_order():
    values = ["E4", "C4", "Rest", "A4"]
    ordered = sort_pitch_values(values, order=["Rest", "C4", "E4", "A4"])
    assert ordered == ["Rest", "C4", "E4", "A4"]


def test_corpus_helpers_expose_basic_corpus_summary_methods():
    corpus = CorpusBase([DummyPiece('One', 'Composer A'), DummyPiece('Two', 'Composer B')])

    notes_df = corpus.notes(combine_rests_choice=False)
    assert isinstance(notes_df, pd.DataFrame)
    assert len(notes_df) >= 2

    weights_df = corpus.note_weights(include_rests=True)
    assert isinstance(weights_df, pd.DataFrame)
    assert {'pitch_class', 'scaled'}.issubset(weights_df.columns)


def test_corpus_tools_wrappers_delegate_to_corpus_base_methods():
    """corpus_tools.py functions should be thin wrappers around the merged CorpusBase methods.

    Uses real pieces (via get_test_corpus) rather than DummyPiece: ImportedPiece
    caches intermediate results on self.analyses, and calling a method a second
    time on an already-"warmed" DummyPiece can return a differently-typed (but
    value-equal) result -- a quirk of that particular mock, not of the real
    parsing pipeline. Each comparison below still uses its own freshly-built
    corpus so neither call is warmed by the other.
    """
    from . import corpus_tools

    direct_notes = get_test_corpus().notes(combine_rests_choice=False)
    wrapped_notes = corpus_tools.corpus_notes(get_test_corpus(), combine_rests_choice=False)
    pd.testing.assert_frame_equal(direct_notes, wrapped_notes)

    direct_weights = get_test_corpus().note_weights(include_rests=True)
    wrapped_weights = corpus_tools.corpus_note_weights(get_test_corpus(), include_rests=True)
    pd.testing.assert_frame_equal(direct_weights, wrapped_weights)


def test_corpus_key_signatures_smoke():
    """Sanity check that keySignatures()/detailIndex(key_sig=True) work against real pieces."""
    corpus = get_test_corpus()
    for piece in corpus.scores:
        ks = piece.keySignatures()
        assert isinstance(ks, pd.DataFrame)
        assert not ks.empty

        indexed = piece.detailIndex(piece.notes(), key_sig=True)
        assert 'KeySig' in indexed.index.names


def _make_two_part_score_with_key_signatures():
    from music21 import stream, note, key, meter, metadata

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = 'Key Sig Test'
    score.metadata.composer = 'Tester'

    part1 = stream.Part(id='Soprano')
    part1.append(key.KeySignature(1))
    part1.append(meter.TimeSignature('4/4'))
    part1.append(note.Note('C5', quarterLength=1))
    part1.append(note.Note('D5', quarterLength=1))

    part2 = stream.Part(id='Bass')
    part2.append(key.KeySignature(-2))
    part2.append(meter.TimeSignature('4/4'))
    part2.append(note.Note('C3', quarterLength=1))
    part2.append(note.Note('D3', quarterLength=1))

    score.insert(0, part1)
    score.insert(0, part2)
    return score


def test_key_signatures_and_detail_index_key_sig_flag():
    piece = ImportedPiece(_make_two_part_score_with_key_signatures(), 'test.xml')

    ks = piece.keySignatures()
    assert ks.iloc[0].tolist() == [1, -2]

    indexed = piece.detailIndex(piece.notes(), key_sig=True)
    assert 'KeySig' in indexed.index.names
    # detailIndex reports the prevailing (first part's) key signature, same
    # convention as its existing t_sig/measure columns.
    key_sig_values = indexed.index.get_level_values('KeySig')
    assert set(key_sig_values) == {1.0}


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
