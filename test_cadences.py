import intervals
from intervals.main_objs import *


TEST_FILES_CC = [  # confirmed ground truth piece for classifyCadences
    'https://crimproject.org/mei/CRIM_Model_0012.mei',
    'https://crimproject.org/mei/CRIM_Model_0023.mei',
]

def test_classifyCadences():
    """Make sure that the cvf and cadence results have not changed in any way for
    our ground-truth corpus. These pieces are manually confirmed to have produced
    perfect cvf and cadence analysis, so any change would be a mistake. Their
    analysis results have been stored to a table and this test reruns their analyses
    to verify that nothing has changed."""
    corpus = CorpusBase(TEST_FILES_CC)
    cvfs = corpus.batch(ImportedPiece.cvfs, metadata=False)
    cads = corpus.batch(ImportedPiece.cadences, metadata=False)
    analysisNow = []
    for i, cad in enumerate(cads):
        cad['URL'] = TEST_FILES_CC[i]
        cvf = cvfs[i]
        cvf.columns = [str(col) for col in range(cvf.columns.size)]
        cvf.fillna('-', inplace=True)
        combined = pd.concat((cad, cvf), axis=1)
        combined.reset_index(inplace=True)
        analysisNow.append(combined)
    analysisNow = pd.concat(analysisNow, ignore_index=True)
    analysisNow = analysisNow.round(3)
    # analysisNow.to_csv('./intervals/data/cadences/groundTruth.csv', index=False)
    groundTruth = pd.read_csv('./intervals/data/cadences/groundTruth.csv')
    groundTruth = groundTruth.astype(analysisNow.dtypes, copy=False)
    print('Comparing current cadential analysis and ground truth...')
    assert(analysisNow.equals(groundTruth))
    print('All analysis values are unchanged so the test was successful.')

test_classifyCadences()
    