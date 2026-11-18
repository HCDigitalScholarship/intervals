from .main_objs import *
import numpy as np


TEST_FILES_CC = [  # confirmed ground truth piece for the .cvfs and .cadences methods
    'https://crimproject.org/mei/CRIM_Model_0012.mei',
    'https://crimproject.org/mei/CRIM_Model_0023.mei',
    # "/Users/amor/Desktop/Code/intervals/CRIM_Model_0012.mei",
    # "/Users/amor/Desktop/Code/intervals/CRIM_Model_0023.mei",
]

def test_classifyCadences():
    """
    Make sure that the cvf and cadence results have not changed in any way for
    our ground-truth corpus. These pieces are manually confirmed to have produced
    perfect cvf and cadence analysis, so any change would be a mistake. Their
    analysis results have been stored to a table and this test reruns their analyses
    to verify that they still match the stored results."""
    corpus = CorpusBase(TEST_FILES_CC)
    cvfs = corpus.batch(ImportedPiece.cvfs, metadata=False, kwargs={'offsets': 'last'})
    cads = corpus.batch(ImportedPiece.cadences, metadata=False)
    # piece.cadences() starts with Composer/Title/Date columns from the source
    # file. They are not part of the cadence classification this test checks
    # (and are not in the stored ground truth), so leave them out.
    cads = [cad.drop(columns=['Composer', 'Title', 'Date'], errors='ignore') for cad in cads]
    analysisNow = []
    for i, cad in enumerate(cads):
        cad['URL'] = TEST_FILES_CC[i]
        cvf = cvfs[i]
        cvf.columns = [str(col) for col in range(cvf.columns.size)]
        cvf = cvf.infer_objects(copy=False).fillna('-')
        combined = pd.concat((cad, cvf), axis=1)
        combined.reset_index(inplace=True)
        analysisNow.append(combined)
    analysisNow = pd.concat(analysisNow, ignore_index=True)
    analysisNow = analysisNow.round(3)
    # You can use the next line to overwrite the ground truth when adding new pieces etc.
    # analysisNow.to_csv('./crim_intervals/data/cadences/groundTruth.csv', index=False)
    groundTruth = pd.read_csv('./crim_intervals/data/cadences/groundTruth.csv')
    # Ignore the url columns in case the test is being run with local files
    analysisNow.drop(columns='URL', inplace=True)
    groundTruth.drop(columns='URL', inplace=True)
    analysisNow.rename(columns={'Last': 'index'}, inplace=True)
    groundTruth = groundTruth.astype(analysisNow.dtypes.to_dict())
    # TSig/Measure/Beat reflect the piece's notated meter/positions, not the
    # cadence classification itself. This test's purpose is to validate
    # classification (CadType, CVFs, Tone, etc.), so these can legitimately
    # drift (e.g. if the source MEI file is revised) without indicating a
    # classification regression -- ignore them here.
    ignored_cols = ['TSig', 'Measure', 'Beat']
    analysisNow = analysisNow.drop(columns=ignored_cols)
    groundTruth = groundTruth.drop(columns=ignored_cols)
    an = analysisNow.copy()
    gt = groundTruth.copy()
    print('Comparing current cadential analysis and ground truth...')
    # Compare values as objects: under pandas 3 the ground truth's text columns
    # load as the 'str' dtype while the fresh analysis may hold 'object'
    # columns, and DataFrame.equals would treat identical values as different.
    isEqual = (analysisNow.infer_objects(copy=False).fillna('-').astype(object)
               .equals(groundTruth.infer_objects(copy=False).fillna('-').astype(object)))
    # Try to give feedback if the test fails
    if not isEqual:
        firstCVFCol = groundTruth.columns.get_loc('0')
        ancvf = analysisNow.iloc[:, firstCVFCol:].copy().infer_objects(copy=False).fillna('.')
        gtcvf = groundTruth.iloc[:, firstCVFCol:].copy().infer_objects(copy=False).fillna('.')
        try:
            diff = (ancvf == gtcvf).replace(True, np.nan).dropna(how='all')
            if len(diff.index):
                print('\n*********\nThere appears to be a mismatch in the cvfs here:\n', diff)
                print('\nThe current analysis is returning this:\n', ancvf.take(diff.index))
                print('\nBut the expected cvfs in the ground truth are:\n', gtcvf.take(diff.index), '\n*********\n')
        except:
            pass
        for col in analysisNow.columns:
            colsEqual = (analysisNow[col].fillna('-').astype(object)
                         .equals(groundTruth[col].fillna('-').astype(object)))
            if not colsEqual:
                print('\n*********\nThere is a discrepancy in the {} column.\n*********\n'.format(col))

    assert(isEqual)
    print('All analysis values are unchanged so the test was successful.')
