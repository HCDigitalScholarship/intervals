"""
This file contains the exploratory tests while I develop new methods
"""

# from test_main_objs import *
# from visualizations import *
# from visualizations import *
from main_objs import *
from bs4 import BeautifulSoup
from urllib.request import urlopen

Model_0008 = 'https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/CRIM_Model_0008.mei'

RANDOM = ['54-65/1-2,1-2,1-2,1-2,1-2,1-3,1-4,3-4,3-4,3-4,3-4,3-4/@3+@3,@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3+@3,@1+@1+@1-4+@1-3,@1-3+@1-3,@1-4.5+@1-3,@1-4+@1-3,@1-4+@1-3,@1+@1',
                 '1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
                 '1/1/@1-3',
                 '44-46/1,1,1/@3,@1-3,@1',
                 '46-48/1+3-4,1+3-4,1+4/@3+@2-4+@4,@1-3+@1-4+@1-3,@1+@1',
                 '50-53/1,1,1+3,1+3/@4,@1.5-4,@1-4+@3,@1+@1',
                 '1/1/@1-3',
                 '1/1/@1-3',
                 '1/1/@3',
                 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1']

FUGA = ['23-29/2,2,1,1+3,1+3,1+4,4/@1,@1-3,@1,@1-3+@1,@1-3+@1-3,@1+@1,@1-3',
 '5-10/3-4,3-4,3-4,3-4,3-4,4/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '95-96,99-100,104-107/2,2,2,2,1+3,1+3,2,2/@1-3.5,@1,@1-3.5,@1,@1-3.5+@2-3.5,@1+@1-2,@1-3.5,@1',
 '1-4/1-2,1-2,1-2,1-2/@1-3+@all,@1-3+@all,@1-3+@1-3,@1+@1-3',
 '54-56/1-2,1-2,1-2/@3+@3,@1-4+@1-3,@1-3+@1-3',
 '54-64/1-2,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4,1-4/@3+@3,@1-4+@1-3+@all+@all,@1-3+@1-3+@all+@all,@1-4.5+@1-3+@all+@all,@1-4+@1-3+@all+@all,@1-4+@1-3+@1-3+@all,@1+@1-3+@1-4+@1-3,@all+@all+@1-3+@3,@all+@all+@1-4.5+@1-3,@all+@all+@1-4+@2.5-3,@1-3+@all+@1-2+@1-3',
 '44-48/3-4,3-4,3-4,3-4,3-4/@3-4+@4,@1-4+@1-3,@1-4+@1-4,@1-4+@1-3,@1+@1',
]


PEN = ['1-10/1,1-4,1-4,1-4,2-4,2-4,3-4,3-4,4,4/@1-3,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@1-3+@1-3+@all,@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,3-4,4/@all+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '8-17/1,1,1-3,1-4,1-4,2-4,2-4,2-4,2-4,4/@1-4,@1-3,@1-3+@1-4+@all,@1-3+@1-3+@all+@all,@1+@2.5-3+@1-4+@all,@1-3+@1-3+@all,@1+@1-3+@1-4,@all+@1-3+@1-3,@all+@1+@1-4,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,3-4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,3-4,3-4,3-4,4/@3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,3-4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1-4,1-4,1-4,1-4,1-4,1-4,1-4,3-4,3-4,4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1-3,@all+@1-3,@1',
 '1-8/1-4,1-4,1-4,1-4,1-4,1-4,1-4,1+3-4/@1-3+@all+@all+@all,@1-3+@all+@all+@all,@1-3+@1-3+@all+@all,@1+@1-3+@all+@all,@all+@1-3+@1-3+@all,@all+@1+@1-3+@all,@all+@all+@1-3+@1-3,@1+@1+@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '8-17/1,1,1-2,1-2,1-3,2-3,2-4,3-4,3-4,4/@1-4,@1-3,@1-3+@1-4,@1-3+@1-3,@1+@1-3+@1-4,@1-3+@1-3,@1+@1-3+@1-4,@1-3+@1-3,@1+@1-4,@1',
 '16-25/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@3,@1-3,@1-3+@3,@1+@1-3,@1-3+@3,@1+@1-3,@1-3+@3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1',
 '1-10/1,1,1-2,1-2,2-3,2-3,3-4,3-4,4,4/@1-3,@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3+@1-3,@1+@1-3,@1-3,@1']

def process_integer_range(range_expression):
    """Process range for measure and staves"""
    range_expression = range_expression.split("-")
    start = int(range_expression[0])
    end = int(range_expression[1])
    return list(range(start, end + 1))


def process_measure_ex(measure_ex):
    """
    Process the measures expression list of measures
    of numbers
    """
    result = []
    measure_ex = measure_ex.split(",")
    for item in measure_ex:
        if item.isdigit():
            result.append(int(item))
        else:
            result.extend(process_integer_range(item))
    return result


def process_staff_range(staff_ex):
    result = []
    staff_ex = staff_ex.split("+")
    for item in staff_ex:
        if item.isdigit():
            result.append(int(item))
        else:
            result.extend(process_integer_range(item))
    return result


def process_beat_helper(beat_expression):
    """Contain different possibility of a beat expression"""
    return None


def process_beat(measure, voice, beat_ex, notes_df, chosen_notes_df):
    """From the measure, and the stave number, return the offsets of the notes of interest"""
    assert beat_ex[0] == '@'
    if beat_ex == '@all':
        chosen_notes_df.loc[measure, :][voice] = notes_df.loc[measure, :][voice]
        return

    beat_ex = beat_ex[1:].split("-")
    start = float(beat_ex[0])
    if len(beat_ex) > 1:
        end = float(beat_ex[1])
        all_beats = notes_df.loc[measure].index
        for beat in all_beats:
            if start <= beat <= end:
                chosen_notes_df.loc[measure, beat][voice] = notes_df.loc[measure, beat][voice]
                # chosen_notes_df.loc[measure, beat][voice] = 1
    else:
        chosen_notes_df.loc[measure, start][voice] = notes_df.loc[measure, start][voice]
        # chosen_notes_df.loc[measure, start][voice] = 1


def from_ema_to_offsets(ema, staff_to_voice, notes_df, chosen_notes_df):
    # first, split
    measure, staves, beats = ema.split("/")

    # select each staff in each measure
    measure = process_measure_ex(measure)

    # select each staff
    staves = staves.split(",")
    new_staff = []
    for staff in staves:
        new_staff.append(process_staff_range(staff))

    beats = beats.split(",")
    # select each beat
    for i in range(len(measure)):
        beat = beats[i].split("+")
        for j in range(len(new_staff[i])):
            measure_num = measure[i]
            staff = new_staff[i][j]
            for beat_ex in beat:
                process_beat(measure_num, staff_to_voice[staff], beat_ex, notes_df, chosen_notes_df)
    return chosen_notes_df


def main():
    file_url = Model_0008
    corpus = CorpusBase([file_url])
    model = corpus.scores[0]
    nr = model._getM21ObjsNoTies()
    complete_nr = model.detailIndex(df=nr, measure=True, beat=True)
    chosen_nr = pd.DataFrame(index=complete_nr.index.copy(), columns=complete_nr.columns.copy())

    staff_to_voice = {}
    # get the staff number and voices!
    with urlopen(file_url) as fp:
        soup = BeautifulSoup(fp, 'xml')

    for voice in complete_nr.columns:
        staff = soup.find('staffDef', label=voice)
        staff_num = int(staff['n'])
        staff_to_voice[staff_num] = voice

    examples = FUGA

    for example in examples:
        try:
            res = from_ema_to_offsets(example, staff_to_voice, complete_nr, chosen_nr).dropna(how='all')
            # print(res)
            for part in res:
                mel_intervals = ImportedPiece._melodifyPart(res[part].copy())
                if len(mel_intervals) > 0:
                    # 'z', t, t
                    mel_intervals = mel_intervals.map(
                        lambda cell: cell.directedName[1:] if hasattr(cell, 'directedName') else cell)
                    mel_intervals = mel_intervals.map(ImportedPiece._zeroIndexIntervals, na_action='ignore')
                    print(part, ', '.join(str(item) for item in mel_intervals.to_list()), len(mel_intervals))
        except ValueError:
            print("oop, ema address has problems.")
        finally:
            print("-----")


main()

