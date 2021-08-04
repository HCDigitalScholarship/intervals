"""
This file contains the exploratory tests while I develop new methods
"""

# from test_main_objs import *
# from visualizations import *
# from visualizations import *
from main_objs import *
import visualizations as viz

from bs4 import BeautifulSoup
from urllib.request import urlopen
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
import requests

model_0008 = 'https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/CRIM_Model_0008.mei'

RANDOM = [
    '54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1',
    '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
    '1/1/@1-3',
    '44-46/1,1,1/@3,@1-3,@1',
    '46-48/1+3-4,1+3-4,1+4/@3+@2-4+@4,@1-3+@1-4+@1-3,@1+@1',
    '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1',
    '1/1/@1-3',
    '1/1/@1-3',
    '1/1/@3',
    '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1']
HARDCODED_RANDOM = [{'[Superius]': {428.0: np.nan, 432.0: '3, -1, 1, 1, -2, -1, -1, 0, 0, 1, -1, 3, -1, 1',
                                    472.0: np.nan, 476.0: np.nan},
                     'Altus': {428.0: 'Rest, 3, -1, 1, 1, -2, -1, -1, 0, -1, 1, 1, -1', 432.0: np.nan, 472.0: np.nan,
                               476.0: np.nan},
                     'Tenor': {428.0: np.nan, 432.0: np.nan, 472.0: '3, -1, 1, 1, -2, -1, -1, 0, 0, 1, -1, 3, -1, 1',
                               476.0: np.nan}, 'Bassus': {428.0: np.nan, 432.0: np.nan, 472.0: np.nan,
                                                          476.0: '3, -1, 1, 1, -2, -1, -1, 0, -1, 1, 1, -1'}, 'ema': {
        428.0: '54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1',
        432.0: '54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1',
        472.0: '54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1',
        476.0: '54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1'}},
                    {'[Superius]': {4.0: '3, 0, 1, 1, -2', 8.0: np.nan},
                     'Altus': {4.0: np.nan, 8.0: 'Rest, 3, 0, 1, 1, -2'},
                     'Tenor': {4.0: np.nan, 8.0: 'Rest, Rest, Rest, 3, 0, 1, 1, -2'},
                     'Bassus': {4.0: np.nan, 8.0: 'Rest, Rest, Rest, Rest, Rest, 3, 0, 1, 1, -2'}, 'ema': {
                        4.0: '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
                        8.0: '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1'}},
                    {'[Superius]': {4.0: '3'}, 'Altus': {4.0: np.nan}, 'Tenor': {4.0: np.nan}, 'Bassus': {4.0: np.nan},
                     'ema': {4.0: '1/1/@1-3'}},
                    {'[Superius]': {352.0: '1, 1, 1'}, 'Altus': {352.0: np.nan}, 'Tenor': {352.0: np.nan},
                     'Bassus': {352.0: np.nan}, 'ema': {352.0: '44-46/1,1,1/@3,@1-3,@1'}},
                    {'[Superius]': {366.0: np.nan, 368.0: '1, 1, 1'}, 'Altus': {366.0: np.nan, 368.0: np.nan},
                     'Tenor': {366.0: '1, 1, 1', 368.0: np.nan}, 'Bassus': {366.0: np.nan, 368.0: '1, 1, 1'},
                     'ema': {366.0: '46-48/1+3-4,1+3-4,1+4/@3+@2-4+@4,@1-3+@1-4+@1-3,@1+@1',
                             368.0: '46-48/1+3-4,1+3-4,1+4/@3+@2-4+@4,@1-3+@1-4+@1-3,@1+@1'}},
                    {'[Superius]': {401.0: '-1, -1, -1, 1, 1, -1, -1, -1, 1', 416.0: np.nan},
                     'Altus': {401.0: np.nan, 416.0: np.nan}, 'Tenor': {401.0: np.nan, 416.0: '-1'},
                     'Bassus': {401.0: np.nan, 416.0: np.nan},
                     'ema': {401.0: '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1',
                             416.0: '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1'}},
                    {'[Superius]': {4.0: '3'}, 'Altus': {4.0: np.nan}, 'Tenor': {4.0: np.nan}, 'Bassus': {4.0: np.nan},
                     'ema': {4.0: '1/1/@1-3'}},
                    {'[Superius]': {4.0: '3'}, 'Altus': {4.0: np.nan}, 'Tenor': {4.0: np.nan}, 'Bassus': {4.0: np.nan},
                     'ema': {4.0: '1/1/@1-3'}}, {'[Superius]': {}, 'Altus': {}, 'Tenor': {}, 'Bassus': {}, 'ema': {}},
                    {'[Superius]': {4.0: '3, 0, 1, 1, -2', 20.0: np.nan, 36.0: np.nan, 52.0: np.nan},
                     'Altus': {4.0: np.nan, 20.0: '3, 0, 1, 1, -2', 36.0: np.nan, 52.0: np.nan},
                     'Tenor': {4.0: np.nan, 20.0: np.nan, 36.0: '3, 0, 1, 1, -2', 52.0: np.nan},
                     'Bassus': {4.0: np.nan, 20.0: np.nan, 36.0: np.nan, 52.0: '3, 0, 1, 1, -2'}, 'ema': {
                        4.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
                        20.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
                        36.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
                        52.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1'}}]

FUGA = ['23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3',
        '5-10/3-4,3-4,3-4,3-4,3-4,4/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
        '95-96,99-100,104-107/2,2,2,2,1+3,1+3,2,2/@1-3.5,@1,@1-3.5,@1,@1-3.5+@2-3.5,@1+@1-2,@1-3.5,@1',
        '1-4/1-2,1-2,1-2,1-2/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3',
        '54-56/1-2,1-2,1-2/@3+@3,@1-4+@1-3,@1-3+@1-3',
        '54-64/1-2,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4/@3+@3,@1-4+@1-3+@all+@all,@1-3+@1-3+@all+@all,@1-4.5+@1-3+@all+@all,@1-4+@1-3+@all+@all,@1-4+@1-3+@1-3+@all,@1+@1-3+@1-4+@1-3,@all+@all+@1-3+@3,@all+@all+@1-4.5+@1-3,@all+@all+@1-4+@2.5-3,@1-3+@all+@1-2+@1-3',
        '44-48/3-4,3-4,3-4,3-4,3-4/@3-4+@4,@1-4+@1-3,@1-4+@1-4,@1-4+@1-3,@1+@1',
        ]
HARDCODED_FUGA = [{'[Superius]': {184.0: np.nan, 200.0: '-2, -1, 3, 1, 1', 208.0: np.nan, 224.0: np.nan},
                   'Altus': {184.0: '-2, -1', 200.0: np.nan, 208.0: np.nan, 224.0: np.nan},
                   'Tenor': {184.0: np.nan, 200.0: np.nan, 208.0: '-2, -1', 224.0: np.nan},
                   'Bassus': {184.0: np.nan, 200.0: np.nan, 208.0: np.nan, 224.0: '-2, -1'},
                   'ema': {184.0: '23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3',
                           200.0: '23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3',
                           208.0: '23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3',
                           224.0: '23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3'}},
                  {'[Superius]': {32.0: np.nan, 36.0: np.nan}, 'Altus': {32.0: np.nan, 36.0: np.nan},
                   'Tenor': {32.0: np.nan, 36.0: '3, 0, 1, 1, -2, Rest'},
                   'Bassus': {32.0: 'Rest, Rest, 3, 0, 1, 1, -2', 36.0: np.nan},
                   'ema': {32.0: '5-10/3-4,3-4,3-4,3-4,3-4,4/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
                           36.0: '5-10/3-4,3-4,3-4,3-4,3-4,4/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3,@all+@1-3,@1'}},
                  {'[Superius]': {762.0: np.nan, 870.0: '-1, -1, -1, -1', 872.0: np.nan},
                   'Altus': {762.0: '-1, -1, -1, -1, 4, -1, -1, -1, -1, 6, -1, -1, -1, -1', 870.0: np.nan,
                             872.0: np.nan}, 'Tenor': {762.0: np.nan, 870.0: np.nan, 872.0: '3, -1, -1'},
                   'Bassus': {762.0: np.nan, 870.0: np.nan, 872.0: np.nan}, 'ema': {
                      762.0: '95-96,99-100,104-107/2,2,2,2,1+3,1+3,2,2/@1-3.5,@1,@1-3.5,@1,@1-3.5+@2-3.5,@1+@1-2,@1-3.5,@1',
                      870.0: '95-96,99-100,104-107/2,2,2,2,1+3,1+3,2,2/@1-3.5,@1,@1-3.5,@1,@1-3.5+@2-3.5,@1+@1-2,@1-3.5,@1',
                      872.0: '95-96,99-100,104-107/2,2,2,2,1+3,1+3,2,2/@1-3.5,@1,@1-3.5,@1,@1-3.5+@2-3.5,@1+@1-2,@1-3.5,@1'}},
                  {'[Superius]': {0.0: np.nan, 4.0: '3, 0, 1, 1, -2'}, 'Altus': {0.0: 'Rest, Rest, 3, 0', 4.0: np.nan},
                   'Tenor': {0.0: np.nan, 4.0: np.nan}, 'Bassus': {0.0: np.nan, 4.0: np.nan},
                   'ema': {0.0: '1-4/1-2,1-2,1-2,1-2/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3',
                           4.0: '1-4/1-2,1-2,1-2,1-2/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3'}},
                  {'[Superius]': {428.0: np.nan, 432.0: '3, -1, 1, 1'},
                   'Altus': {428.0: 'Rest, 3, -1, 1', 432.0: np.nan}, 'Tenor': {428.0: np.nan, 432.0: np.nan},
                   'Bassus': {428.0: np.nan, 432.0: np.nan},
                   'ema': {428.0: '54-56/1-2,1-2,1-2/@3+@3,@1-4+@1-3,@1-3+@1-3',
                           432.0: '54-56/1-2,1-2,1-2/@3+@3,@1-4+@1-3,@1-3+@1-3'}}, {'[Superius]': {428.0: np.nan,
                                                                                                   432.0: '3, -1, 1, 1, -2, -1, -1, 0, 0, 1, -1, 3, -1, 1, Rest, Rest, Rest, Rest'},
                                                                                    'Altus': {
                                                                                        428.0: 'Rest, 3, -1, 1, 1, -2, -1, -1, 0, -1, 1, 1, -1, Rest, Rest, Rest, Rest, Rest',
                                                                                        432.0: np.nan},
                                                                                    'Tenor': {428.0: np.nan,
                                                                                              432.0: 'Rest, Rest, Rest, Rest, Rest, 3, -1, 1, 1, -2, -1, -1, 0, 0, 1, -1, 3'},
                                                                                    'Bassus': {428.0: np.nan,
                                                                                               432.0: 'Rest, Rest, Rest, Rest, Rest, 3, 0, 1, -2, -2, 0, -1, 1, 1'},
                                                                                    'ema': {
                                                                                        428.0: '54-64/1-2,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4/@3+@3,@1-4+@1-3+@all+@all,@1-3+@1-3+@all+@all,@1-4.5+@1-3+@all+@all,@1-4+@1-3+@all+@all,@1-4+@1-3+@1-3+@all,@1+@1-3+@1-4+@1-3,@all+@all+@1-3+@3,@all+@all+@1-4.5+@1-3,@all+@all+@1-4+@2.5-3,@1-3+@all+@1-2+@1-3',
                                                                                        432.0: '54-64/1-2,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4/@3+@3,@1-4+@1-3+@all+@all,@1-3+@1-3+@all+@all,@1-4.5+@1-3+@all+@all,@1-4+@1-3+@all+@all,@1-4+@1-3+@1-3+@all,@1+@1-3+@1-4+@1-3,@all+@all+@1-3+@3,@all+@all+@1-4.5+@1-3,@all+@all+@1-4+@2.5-3,@1-3+@all+@1-2+@1-3'}},
                  {'[Superius]': {350.0: np.nan, 352.0: np.nan}, 'Altus': {350.0: np.nan, 352.0: np.nan},
                   'Tenor': {350.0: '1, 1, 1, -2, 1, 1, 1', 352.0: np.nan},
                   'Bassus': {350.0: np.nan, 352.0: '1, 1, 1, -2, 1, 1, 1'},
                   'ema': {350.0: '44-48/3-4,3-4,3-4,3-4,3-4/@3-4+@4,@1-4+@1-3,@1-4+@1-4,@1-4+@1-3,@1+@1',
                           352.0: '44-48/3-4,3-4,3-4,3-4,3-4/@3-4+@4,@1-4+@1-3,@1-4+@1-4,@1-4+@1-3,@1+@1'}}]

PEN = [
    '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
    '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
    '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
    '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@1-3,@1']
HARDCODED_PEN = [
    {'[Superius]': {4.0: '3, 0, 1, 1, -2', 8.0: np.nan}, 'Altus': {4.0: np.nan, 8.0: 'Rest, 3, 0, 1, 1, -2'},
     'Tenor': {4.0: np.nan, 8.0: 'Rest, Rest, Rest, 3, 0, 1, 1, -2'},
     'Bassus': {4.0: np.nan, 8.0: 'Rest, Rest, Rest, Rest, Rest, 3, 0, 1, 1, -2'}, 'ema': {
        4.0: '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
        8.0: '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1'}},
    {'[Superius]': {4.0: '3, 0, 1, 1, -2', 20.0: np.nan, 36.0: np.nan, 52.0: np.nan},
     'Altus': {4.0: np.nan, 20.0: '3, 0, 1, 1, -2', 36.0: np.nan, 52.0: np.nan},
     'Tenor': {4.0: np.nan, 20.0: np.nan, 36.0: '3, 0, 1, 1, -2', 52.0: np.nan},
     'Bassus': {4.0: np.nan, 20.0: np.nan, 36.0: np.nan, 52.0: '3, 0, 1, 1, -2'}, 'ema': {
        4.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        20.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        36.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        52.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1'}},
    {'[Superius]': {4.0: '3, 0, 1, 1, -2', 20.0: np.nan, 36.0: np.nan, 52.0: np.nan},
     'Altus': {4.0: np.nan, 20.0: '3, 0, 1, 1, -2', 36.0: np.nan, 52.0: np.nan},
     'Tenor': {4.0: np.nan, 20.0: np.nan, 36.0: '3, 0, 1, 1, -2', 52.0: np.nan},
     'Bassus': {4.0: np.nan, 20.0: np.nan, 36.0: np.nan, 52.0: '3, 0, 1, 1, -2'}, 'ema': {
        4.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        20.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        36.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
        52.0: '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1'}},
    {'[Superius]': {0.0: np.nan, 4.0: '3, 0, 1, 1, -2, Rest, Rest, Rest'},
     'Altus': {0.0: 'Rest, Rest, 3, 0, 1, 1, -2, Rest', 4.0: np.nan},
     'Tenor': {0.0: 'Rest, Rest, Rest, Rest, 3, 0, 1, 1, -2', 4.0: np.nan},
     'Bassus': {0.0: 'Rest, Rest, Rest, Rest, Rest, Rest, 3, 0, 1, 1, -2', 4.0: np.nan}, 'ema': {
        0.0: '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@1-3,@1',
        4.0: '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@1-3,@1'}}]

CADENCE = ['50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1',  # checked
           '23-24/2-3,2-3/@1+@1-4,@1-3+@1-3',  # checked
           '33-35/1-2,1-2,1-2/@4+@4,@1-4+@1-3,@1+@1',  # checked
           '59-60/1-2,1-3/@2-4+@2-3,@1+@1+@1',  # checked
           '64-65/3-4,3-4/@2-4+@2-3,@1+@1',  # checked
           ]
HARDCODED_CADENCE = [
    {'[Superius]': {401.0: '-1, -1, -1, 1, 1, -1, -1, -1, 1', 416.0: np.nan}, 'Altus': {401.0: np.nan, 416.0: np.nan},
     'Tenor': {401.0: np.nan, 416.0: '-1'}, 'Bassus': {401.0: np.nan, 416.0: np.nan},
     'ema': {401.0: '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1', 416.0: '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1'}},
    {'[Superius]': {178.0: np.nan, 184.0: np.nan}, 'Altus': {178.0: np.nan, 184.0: '-2, -1'},
     'Tenor': {178.0: '2, -1, 3, -1, 1', 184.0: np.nan}, 'Bassus': {178.0: np.nan, 184.0: np.nan},
     'ema': {178.0: '23-24/2-3,2-3/@1+@1-4,@1-3+@1-3', 184.0: '23-24/2-3,2-3/@1+@1-4,@1-3+@1-3'}},
    {'[Superius]': {265.0: '-1, 0, -1, 1', 266.0: np.nan}, 'Altus': {265.0: np.nan, 266.0: '-1, -1, -1'},
     'Tenor': {265.0: np.nan, 266.0: np.nan}, 'Bassus': {265.0: np.nan, 266.0: np.nan},
     'ema': {265.0: '33-35/1-2,1-2,1-2/@4+@4,@1-4+@1-3,@1+@1', 266.0: '33-35/1-2,1-2,1-2/@4+@4,@1-4+@1-3,@1+@1'}},
    {'[Superius]': {468.0: np.nan, 470.0: '-1, 1'}, 'Altus': {468.0: '1, -1', 470.0: np.nan},
     'Tenor': {468.0: np.nan, 470.0: np.nan}, 'Bassus': {468.0: np.nan, 470.0: np.nan},
     'ema': {468.0: '59-60/1-2,1-3/@2-4+@2-3,@1+@1+@1', 470.0: '59-60/1-2,1-3/@2-4+@2-3,@1+@1+@1'}},
    {'[Superius]': {508.0: np.nan, 510.0: np.nan}, 'Altus': {508.0: np.nan, 510.0: np.nan},
     'Tenor': {508.0: np.nan, 510.0: '-1, 1'}, 'Bassus': {508.0: '1, -1', 510.0: np.nan},
     'ema': {508.0: '64-65/3-4,3-4/@2-4+@2-3,@1+@1', 510.0: '64-65/3-4,3-4/@2-4+@2-3,@1+@1'}}]


class ObservedPiece(ImportedPiece):
    """
    This class allows users to extract and evaluate observations within a piece
    """

    def __init__(self, scoreAddress):
        score = ScoreBase(scoreAddress).score
        ImportedPiece.__init__(self, score)
        self.scoreAddress = scoreAddress # keep the link to the score
        self.observationsAnalyses = {} # score the analysis regarding observations 
        self.stavesToVoices = {} # {int (staff number): str (voice)}
        with urlopen(self.scoreAddress) as fp:
            scoreData = BeautifulSoup(fp, 'xml')

        for voice in self._getPartNames():
            staff = scoreData.find('staffDef', label=voice)
            staffNum = int(staff['n'])
            self.stavesToVoices[staffNum] = voice

    def _getMeasureBeatM21ObjsNoTies(self):
        if not 'MeasureBeatM21ObjsNoTies' in self.observationsAnalyses:
            m21Objs = self._getM21ObjsNoTies().copy()
            m21Objs['offset'] = m21Objs.index.copy()
            m21Objs = self.detailIndex(df=m21Objs, measure=True, beat=True)
            self.observationsAnalyses['MeasureBeatM21ObjsNoTies'] = m21Objs
        return self.observationsAnalyses['MeasureBeatM21ObjsNoTies']

    def _processIntegerRange(rangeExpression):
        """Process range for measure and staves"""
        rangeExpression = rangeExpression.split("-")
        start = int(rangeExpression[0])
        end = int(rangeExpression[1])
        return list(range(start, end + 1))
    
    def _processMeasure(measureExpression):
        """
        Process the measures expression list of measures
        of numbers
        """
        result = []
        measureExpression = measureExpression.split(",")
        for item in measureExpression:
            if item.isdigit():
                result.append(int(item))
            else:
                result.extend(ObservedPiece._processIntegerRange(item))
        return result
    
    
    def _processStaffRange(staffExpression):
        result = []
        staffExpression = staffExpression.split("+")
        for item in staffExpression:
            if item.isdigit():
                result.append(int(item))
            else:
                result.extend(ObservedPiece._processIntegerRange(item))
        return result

    def _processBeat(self, measure, voice, staffBeat, chosenNotesDf):
        """From the measure, and the stave number, return the offsets of the notes of interest"""
        for beatExpression in staffBeat.split("@"):
            if beatExpression == '':
                continue
            else:
                measureBeatDf = self._getMeasureBeatM21ObjsNoTies()
                if beatExpression == 'all':
                    chosenNotesDf.loc[(measure, slice(None)), [voice, 'offset']] = \
                        measureBeatDf.loc[(measure, slice(None)), [voice, 'offset']]
                else:
                    beatExpression = beatExpression.split("-")
                    start = float(beatExpression[0])
                    if len(beatExpression) > 1:
                        end = float(beatExpression[1])
                        chosenNotesDf.loc[(measure, start):(measure, end), [voice, 'offset']] = \
                            measureBeatDf.loc[(measure, start):(measure, end), [voice, 'offset']]
                    else:
                        chosenNotesDf.loc[(measure, start), [voice, 'offset']] = measureBeatDf.loc[
                            (measure, start), [voice, 'offset']]
    
    
    def getNotesFromEma(self, ema):
        """
        Get dataframe of M21 notes objects that are included in the ema address.
        :param ema: ema address
        :return: dataframe with chosen notes.
        """

        # create an empty dataframe with the m21objects columns and index to later
        # fill it with chosen notes
        m21Objs = self._getMeasureBeatM21ObjsNoTies()
        chosenM21Objs = pd.DataFrame(index=m21Objs.index.copy(), columns=m21Objs.columns.copy())

        # first, split
        measure, staves, beats = ema.split("/")
    
        # select each staff in each measure
        measure = ObservedPiece._processMeasure(measure)
    
        # select each staff
        staves = staves.split(",")
        newStaff = []
        for staff in staves:
            newStaff.append(ObservedPiece._processStaffRange(staff))
    
        beats = beats.split(",")
        # select each beat
        for i in range(len(measure)):
            beat = beats[i].split("+")
            for j in range(len(newStaff[i])):
                measureNumber = measure[i]
                staff = newStaff[i][j]
                self._processBeat(measureNumber, self.stavesToVoices[staff], beat[j], chosenM21Objs)
        return chosenM21Objs
    
    def _getMelodicIntervals(self, m21objs, kind='z'):
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, True, True)
    
        df = m21objs.apply(ImportedPiece._melodifyPart)
        df = df.applymap(self._intervalMethods[settings])
        if kind == 'z':
            df = df.applymap(ImportedPiece._zeroIndexIntervals, na_action='ignore')
        
        return df

    def _getHarmonicIntervals(self, m21Objs, kind='z'):
        kind = kind[0].lower()
        kind = {'s': 'c'}.get(kind, kind)
        _kind = {'z': 'd'}.get(kind, kind)
        settings = (_kind, True, True)

        pairs = []
        combos = combinations(range(len(m21Objs.columns) - 1, -1, -1), 2)
        for combo in combos:
            df = m21Objs.iloc[:, list(combo)].dropna(how='all').ffill()
            ser = df.apply(ImportedPiece._harmonicIntervalHelper, axis=1)
            # name each column according to the voice names that make up the intervals, e.g. 'Bassus_Altus'
            ser.name = '_'.join((m21Objs.columns[combo[0]], m21Objs.columns[combo[1]]))
            pairs.append(ser)
        if pairs:
            dfHar = pd.concat(pairs, axis=1)
        else:
            dfHar = pd.DataFrame()

        dfHar = dfHar.applymap(self._intervalMethods[settings])
        if kind == 'z':
            dfHar= dfHar.applymap(ImportedPiece._zeroIndexIntervals, na_action='ignore')
        return dfHar

    def _createNgramsHelper(ser):
        ser.dropna(inplace=True)
        if len(ser) > 0:
            offset = ser.index[0]
            ngram = ", ".join(interval for interval in ser)
            return pd.Series([ngram], index=[offset], name=ser.name)
        else:
            return pd.Series(dtype='float64')
    
    def _createNgrams(chosenM21Objs):
        df = chosenM21Objs.apply(lambda ser: ObservedPiece._createNgramsHelper(ser))
        return df
    
    def getNgramsFromEma(self, ema, interval='m', kind='z'):
        """
        This method outputs a dataframe of ngrams in the ema address.
        :param ema: the ema address
        :param interval: the type of interval the users want the ngrams to be
        ('m' for melodic and 'h' for harmonic intervals)
        :param kind: the settings for the interval. Users could put in 'z'
        for directed, compound, zero-indexed diatonic intervals, or 'c' for
        directed, compound, chromatic intervals.
        :return: a dataframe of ngrams of intervals of the selected types.
        """
    
        chosenM21Objs = self.getNotesFromEma(ema).dropna(how='all')
    
        # turn chosen objects into ngrams intervals
        chosenM21Objs.reset_index(inplace=True)
        chosenM21Objs.set_index('offset', inplace=True)
        chosenM21Objs.drop(columns=['Measure', 'Beat'], inplace=True)
        if interval == 'm':
            chosenM21Objs = self._getMelodicIntervals(chosenM21Objs, kind=kind)
        elif interval == 'h':
            chosenM21Objs = self._getHarmonicIntervals(chosenM21Objs, kind=kind)
        else:
            raise Exception("Please put only 'm' or 'h' for `interval`.")

        chosenM21Objs = ObservedPiece._createNgrams(chosenM21Objs)

        # add a column to know which ema a ngram belongs to
        chosenM21Objs['ema'] = ema

        return chosenM21Objs


def test_pen_entries_csv():
    """Testing the objects with Richard's pen entries"""
    prefix = 'https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/'
    postfix = ".mei"
    fileName = "../CRIM_Intervals_Notebooks/PEN_Detail_2.csv"
    df = pd.read_csv(fileName)

    df_flex = df[df['mt_pe_strict']]
    algorithm = NormalizedLevenshtein()
    scores = []
    for i in df_flex.index:
        row = df_flex.loc[i]
        model = ObservedPiece(prefix + row['piece_id'] + postfix)
        # print(row['ema'])
        ema_df = model.getNgramsFromEma(row['ema'])
        score_df = viz.compute_levenshtein_similarity(ema_df.drop(["ema"], axis=1), algorithm.similarity)
        print(score_df.to_string())
        scores.append(score_df.mean())
    print(scores)


def clean_csv():
    """
    Add the piece url column into Pen csv
    """
    fileName = "../CRIM_Intervals_Notebooks/PEN_Detail.csv"
    df = pd.read_csv(fileName)
    data = []
    for cell in df['url']:
        data.append(pd.json_normalize(requests.get(cell).json()))

    dataDf = pd.concat(data, axis=0)
    dataDf.set_index('url', inplace=True)
    df['piece_id'] = df['url'].map(lambda cell: dataDf.loc[cell]['piece.piece_id'])
    df.to_csv("../CRIM_Intervals_Notebooks/PEN_Detail_2.csv")

# clean_csv()
