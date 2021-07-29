"""
This file contains the exploratory tests while I develop new methods
"""

# from test_main_objs import *
# from visualizations import *
# from visualizations import *
from main_objs import *
from bs4 import BeautifulSoup
from urllib.request import urlopen


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
    file_url = 'https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/CRIM_Model_0008.mei'
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
        res = soup.find('staffDef', label=voice)
        if res:
            voice_index = int(res['n'])
            staff_to_voice[voice_index] = voice
        else:
            print(voice)

    example = '33-38/3,3-4,3-5,1+5,1,2/@3-4.5,@1-2+@3-4.5,@1-4+@1-2+@2-4.5,@4+@1,@1-2,@2-4'
    try:
        res = from_ema_to_offsets(example, staff_to_voice, complete_nr, chosen_nr).dropna(how='all')
        for part in res:
            mel_intervals = ImportedPiece._melodifyPart(res[part].copy())
            if len(mel_intervals) > 0:
                # 'z', t, t
                mel_intervals = mel_intervals.map(
                    lambda cell: cell.directedName[1:] if hasattr(cell, 'directedName') else cell)
                mel_intervals = mel_intervals.map(ImportedPiece._zeroIndexIntervals, na_action='ignore')
                print(', '.join(str(item) for item in mel_intervals.to_list()))
    except ValueError:
        print("oop, ema address has problems.")


main()

""" 

hierachy: / , + -

normal
'1-6/1,1,1-2,1-2,2,2/@1,@1-3,@1-3+@1,@1-3+@1-3,@1-3,@1'
buggy
-6/1,1,1+3,1+3,3,3/@1-4,@1-3,@1-3+@1-4,@1-3+@1-3,@1-3,@1
float
33-38/3,3-4,3-5,1+5,1,2/@3-4.5,@1-2+@3-4.5,@1-4+@1-2+@2-4.5,@4+@1,@1-2,@2-4
multiple range
49-51,56-58/1+5,1+5,1,3+6,3+6,3/@3+@3,@1-4+@1,@1,@1+@1-3,@1-4+@1-3,@1

# rules: 
- means range
+ means or 
@ means at


<staffDef xml:id="m-a24a2183-b581-4e51-9fbf-703a0b95d2dd" clef.line="2" clef.shape="G" key.sig="0" label="[Superius]" lines="5" n="1">
    <!-- voice.female.soprano.ensemble.ah -->
    <instrDef xml:id="m-c13028b9-fcd9-47a9-9830-6f5b690aa767" midi.channel="1" midi.pan="26" midi.volume="100" />
</staffDef>
"""