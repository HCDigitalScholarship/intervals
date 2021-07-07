from main_objs import *

FILES_FEW = ["01", "02", "04", "17", "09"]
FILES_WRONG= ["01", "08", "14", "16", "17"]
FILES_MANY = [
    'https://crimproject.org/mei/CRIM_Model_0001.mei',
    'https://crimproject.org/mei/CRIM_Model_0002.mei',
    'https://crimproject.org/mei/CRIM_Model_0008.mei'
    'https://crimproject.org/mei/CRIM_Model_0009.mei',
    'https://crimproject.org/mei/CRIM_Model_0010.mei',
    'https://crimproject.org/mei/CRIM_Model_0011.mei',
    'https://crimproject.org/mei/CRIM_Model_0012.mei',
    'https://crimproject.org/mei/CRIM_Model_0013.mei',
    'https://crimproject.org/mei/CRIM_Model_0014.mei',
    'https://crimproject.org/mei/CRIM_Model_0015.mei',
    'https://crimproject.org/mei/CRIM_Model_0016.mei',
    'https://crimproject.org/mei/CRIM_Model_0017.mei',
    'https://crimproject.org/mei/CRIM_Model_0019.mei',
    'https://crimproject.org/mei/CRIM_Model_0020.mei',
    'https://crimproject.org/mei/CRIM_Model_0021.mei',
    'https://crimproject.org/mei/CRIM_Mass_0001_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0001_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0001_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0001_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0001_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0002_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0002_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0002_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0002_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0002_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0003_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0003_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0003_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0003_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0003_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0004_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0004_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0004_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0004_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0004_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0005_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0005_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0005_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0005_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0005_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0006_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0006_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0006_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0006_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0006_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0007_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0007_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0007_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0007_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0007_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0008_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0008_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0008_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0008_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0008_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0009_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0009_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0009_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0009_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0009_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0010_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0010_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0010_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0010_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0010_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0011_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0011_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0011_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0011_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0011_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0012_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0012_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0012_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0012_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0012_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0013_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0013_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0013_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0013_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0013_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0014_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0014_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0014_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0014_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0014_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0015_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0015_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0015_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0015_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0015_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0016_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0016_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0016_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0016_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0016_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0017_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0017_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0017_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0017_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0017_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0018_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0018_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0018_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0018_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0018_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0019_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0019_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0019_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0019_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0019_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0020_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0020_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0020_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0020_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0020_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0021_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0021_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0021_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0021_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0021_5.mei',
    'https://crimproject.org/mei/CRIM_Mass_0022_1.mei',
    'https://crimproject.org/mei/CRIM_Mass_0022_2.mei',
    'https://crimproject.org/mei/CRIM_Mass_0022_3.mei',
    'https://crimproject.org/mei/CRIM_Mass_0022_4.mei',
    'https://crimproject.org/mei/CRIM_Mass_0022_5.mei'
]

def build_crim_models(files):
    """
    Build a list of crim models for the selected files.
    """
    root = "https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/"
    prefix = "CRIM_Model_00"
    postfix = ".mei"
    models = {}
    for file in files:
        try:
            if not "http" in file:
                corpus = CorpusBase([root + prefix + file + postfix])
            else:
                file = file.split("/")[-1]
                corpus = CorpusBase([root + file])
            model = corpus.scores[0]
            models[file] = model
        except:
            print("Can't import file", file)

    return models

def validate_ngrams_last_offsets(model, df, n, how='columnwise', other=None, held='Held',
                                 exclude=['Rest'], interval_settings=('d', True, True), unit=0):

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

def has_diff_measure_offsets(model):
    # get columns
    measures = model.getMeasure()
    # compare each columns, return FALSE for strange columns
    voices = measures.columns
    first_voice = measures[voices[0]]

    for voice in voices[1:]:
        if not first_voice.equals(measures[voice]):
            return True
    return False

def find_measures_with_diff(model):
    ms = model.getMeasure()
    num_voices = len(ms.columns)

    # create a df with time signature and note_rests
    ts = model.getTimeSignature()
    nr = model.getNoteRest()
    dur = model.getDuration(nr)

    # combine and divide dataframe
    big_df = pd.concat([nr, ts, dur, ms], axis=1)
    nr_part = big_df.iloc[:, :num_voices]
    ts_part = big_df.iloc[:, num_voices:num_voices * 2]
    dur_part = big_df.iloc[:, num_voices * 2:num_voices * 3]
    ms_part = big_df.iloc[:, num_voices * 3:]
    ts_part.fillna(method='ffill', axis=0, inplace=True)

    # conditions
    ts_condition = ts_part == '3/1'
    nr_condition = nr_part == 'Rest'
    dur_condition = dur_part == 8.0

    ms_part = ms_part[ts_condition & nr_condition & dur_condition].dropna(how='all')

    return ms_part

def identify_faulty_measures_offsets():
    files = FILES_MANY
    models = build_crim_models(files)

    for file, model in models.items():
        if has_diff_measure_offsets(model):
            print(file)
            print(find_measures_with_diff(model))

def test_main():
    files = FILES_MANY
    models = build_crim_models(files)

    for file, model in models.items():
        # cover all different ngrams possibility
        mel = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
        validate_ngrams_last_offsets(model, mel, 5)
        
        mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
        validate_ngrams_last_offsets(model, mel_diatonic, 5)

        # sampling
        mel_sampling = model.getMelodic(kind='q', directed=True, compound=True, unit=4)
        validate_ngrams_last_offsets(model, mel_sampling, 5)

        mel_diatonic_sampling = model.getMelodic(kind='d', directed=True, compound=True, unit=4)
        validate_ngrams_last_offsets(model, mel_diatonic_sampling, 5)
        
        # modules mode
        validate_ngrams_last_offsets(model, df=None, n=5, how='modules')

        # test get measure
        ms = model.getMeasure()

        # test sounding count
        sc = model.getSoundingCount()

        # test time signature
        ts = model.getTimeSignature()

        # TODO add test with n=-1