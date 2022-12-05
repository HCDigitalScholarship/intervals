import intervals
from intervals.main_objs import *
import time
from glob import glob
import pdb

import requests
import re


# piece_list = []
# raw_prefix = "https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_4.0/"
# URL = "https://api.github.com/repos/CRIM-Project/CRIM-online/git/trees/990f5eb3ff1e9623711514d6609da4076257816c"
# piece_json = requests.get(URL).json()
# mono_list = ['CRIM_Model_0003.mei', 'CRIM_Model_0004.mei', 'CRIM_Model_0005.mei', 'CRIM_Model_0006.mei', 'CRIM_Model_0007.mei',
#             'CRIM_Model_0022.mei', 'CRIM_Model_0028.mei', 'CRIM_Model_0035.mei', 'CRIM_Mass_0029_4.mei', 'CRIM_Mass_0049_2.mei',
#             'CRIM_Mass_0049_5.mei']
# pattern = 'CRIM_Mass_([0-9]{4}).mei'
# for p in piece_json["tree"]:
#     p_name = p["path"]
#     if re.search(pattern, p_name):
#         pass
#     elif p_name in mono_list:
#         pass
#     else:
#         piece_list.append(raw_prefix + p["path"])

# print(piece_list)
# piece = importScore("/Users/amor/Desktop/Code/intervals/Plaine_1567_75_2.sib.mei_msg.mei")
# piece = importScore("/Users/amor/Dqesktop/Code/intervals/CRIM_Model_0023.mei")
# piece = importScore("/Users/amor/Desktop/Code/intervals/Que es de ti desconsolado Encina.mxl")
# t0 = time.time()
# res = piece.ic('7_1:-2, 6_-2:2, 8')
# res2 = piece.ic('7_1:-2, 6_-2:2, 8', True)
# df = pd.concat([stk.stack() for stk in [res, res2]], axis=1)


# ptypes = piece.presentationTypes(include_hidden_types=True, limit_to_entries=True)
# t1 = time.time()
# print('Runtime:', t1-t0)
# pdb.set_trace()
# piece = importScore("/Users/amor/Desktop/Code/intervals/E17 Horwood, Salve Regina MEI.mxl")
# pm = piece.patientMelodies()
# ic = piece.ic('7_1:-2, 6_-2:2, 8')
# ents = piece.entries(thematic=False, anywhere=True, n=4)

# print('************* In Sandbox **************')
# pdb.set_trace()
# models = CorpusBase([
#                     "/Users/amor/Desktop/Code/intervals/Mi libertad en sosiego Encina.mxl",
#                     "/Users/amor/Desktop/Code/intervals/Yo me estaba reposando Encina.mxl",
#                     "/Users/amor/Desktop/Code/intervals/Que es de ti desconsolado Encina.mxl",
#                     "https://crimproject.org/mei/CRIM_Model_0020.mei",
#                      "/Users/amor/Desktop/Code/intervals/CRIM_Model_0023.mei",
#                     ])

piece = importScore("https://crimproject.org/mei/CRIM_Model_0008.mei")
pt = piece.presentationTypes()
ng3 = piece.ngrams(n=3, show_both=True, exclude=[], interval_settings=('d', True, False))
mask = ng3.apply(lambda ser: ser.str.fullmatch('[^_]*_[^:]*:-2, 3_(-5|4):2, (1|8)'))
result = ng3[mask]

pdb.set_trace()
t0 = time.time()
old = models.moduleFinder()
t1 = time.time()
print('Old runtime:', t1-t0)
t2 = time.time()
new = models.moduleFinder(ic=True)
t3 = time.time()
print('New runtime:', t3-t2)
pdb.set_trace()


masses = CorpusBase([
                     "https://crimproject.org/mei/CRIM_Mass_0020_1.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0020_2.mei",
                    #  "https://crimproject.org/mei/CRIM_Mass_0020_3.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0020_4.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0020_5.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0032_1.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0032_2.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0032_3.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0032_4.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0032_5.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0050_1.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0050_2.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0050_3.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0050_4.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0050_5.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0015_1.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0015_2.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0015_3.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0015_4.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0015_5.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0018_1.mei",
                     "https://crimproject.org/mei/CRIM_Mass_0018_2.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0018_3.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0018_4.mei",
#                      "https://crimproject.org/mei/CRIM_Mass_0018_5.mei",
                    ] 
#                     + piece_list[:15]
                    )
# mf = models.modelFinder(masses=masses)



# gx45hRqQZF  morgan_alexander
