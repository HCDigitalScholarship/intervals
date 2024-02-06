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
    an = analysisNow.copy()
    gt = groundTruth.copy()
    comb = pd.concat((an['index'], gt['index']), axis=1)
    print('Comparing current cadential analysis and ground truth...')
    isEqual = analysisNow.infer_objects(copy=False).fillna('-').equals(groundTruth.infer_objects(copy=False).fillna('-'))
    # Try to give feedback if the test fails
    if not isEqual:
        comp = pd.concat((an[['index', 'Measure', 'Beat']], gt[['index', 'Measure', 'Beat']]), axis=1, sort=True)
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
            colsEqual = analysisNow[col].equals(groundTruth[col])
            if not colsEqual:
                print('\n*********\nThere is a discrepancy in the {} column.\n*********\n'.format(col))

    assert(isEqual)
    print('All analysis values are unchanged so the test was successful.')

test_classifyCadences()
    
