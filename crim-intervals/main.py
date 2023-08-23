from .main_objs import * 

# Given list of matches, write to csv in current working directory
def export_to_csv(matches: list):
    """Exports matches data to a csv in the current working directory

    Parameters
    ----------
    matches : list
        return value from either find_exact_matches or find_close_matches
    """
    proceed = input("This method will create a csv file in your current working directory. Continue? (y/n): ").lower()
    csv_name = input("Enter a name for your csv file (.csv will be appended): ")
    csv_name += '.csv'
    if proceed != 'y' and proceed != 'yes':
        print("Exiting...")
        return
    import csv
    with open(csv_name, mode='w') as matches_file:
        matches_writer = csv.writer(matches_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if type(matches[0]) == PatternMatches:
            matches_writer.writerow(
                ['Pattern Generating Match', 'Pattern matched', 'Piece Title', 'Part', 'First Note Measure Number',
                 'Last Note Measure Number', 'Note Durations', 'EMA', 'EMA url'])
            for match_series in matches:
                for match in match_series.matches:
                    matches_writer.writerow(
                        [match_series.pattern, match.pattern, match.first_note.metadata.title, match.first_note.part,
                         match.first_note.note.measureNumber, match.last_note.note.measureNumber, match.durations,
                         match.ema, match.ema_url])
        else:
            matches_writer.writerow(
                ['Pattern Generating Match', 'Classification Type', 'EMA', 'EMA url', 'Soggetti 1 Part',
                 'Soggetti 1 Measure', 'Soggetti 2 Part', 'Soggetti 2 Measure', 'Soggetti 3 Part', 'Soggetti 3 Measure',
                 'Soggetti 4 Part', 'Soggetti 4 Measure'])
            for classified_matches in matches:
                row_array = [classified_matches.pattern, classified_matches.type, classified_matches.ema,
                             classified_matches.ema_url]
                for soggetti in classified_matches.matches:
                    row_array.append(soggetti.first_note.part)
                    row_array.append(soggetti.first_note.note.measureNumber)
                matches_writer.writerow(row_array)

    print("CSV created in your current working directory.")

def _emaMeasureHelper(string):
    measures = []
    chunks = string.split(',')
    for chunk in chunks:
        spans = chunk.split('+')
        for span in spans:
            ends = tuple(int(m) for m in span.split('-'))
            for m in range(ends[0], ends[1] + 1):
                yield m

def _emaVoiceHelper(voiceStr, partNames):
    ret = []
    measures = voiceStr.split(',')
    for measure in measures:
        spans = measure.split('+')
        thisMeasure = []
        for span in spans:
            ends = [int(vox) for vox in span.split('-')]
            thisMeasure.extend(partNames[v] for v in range(ends[0] - 1, ends[-1]))
        ret.append(thisMeasure)
    return ret

def _emaBeatHelper(beatStr):
    ret = []
    measures = beatStr.split(',')
    for m in measures:
        voicesInMeasure = []
        voices = m.split('+')
        for voice in voices:
            beatsInVoice = []
            spans = voice[1:].split('@')
            for span in spans:
                ends = tuple(float(beat) for beat in span.split('-'))
                beatsInVoice.append((ends[0], ends[-1]))
            voicesInMeasure.append(beatsInVoice)
        ret.append(voicesInMeasure)
    return ret

def ema2ex(emaStr, df):
    """
    Return the excerpt from the df that is designated by the emaStr. The df 
    must have a Measure and Beat multiIndex as the index labels. You can get 
    this by passing a regular df of an ImportedPiece to 
    ImportedPiece.detailIndex().
    """
    # retrieve the measures from ema address and create start and end in place
    post = {}
    mStr, vStr, bStr = emaStr.split("/")
    voices = _emaVoiceHelper(vStr, df.columns)
    beats = _emaBeatHelper(bStr)
    for mi, measure in enumerate(_emaMeasureHelper(mStr)):
        voicesInMeasure = voices[mi]
        for vi, voice in enumerate(voicesInMeasure):
            beatsInVoice = beats[mi][vi]
            for beatRange in beatsInVoice:
                chunk = df.loc[(measure, beatRange[0]):(measure, beatRange[1]), voice]
                if voice in post:
                    post[voice].append(chunk)
                else:
                    post[voice] = [chunk]
    parts = [pd.concat(vox) for vox in post.values()]
    ret = pd.concat(parts, axis=1)
    ret.columns = post.keys()
    return ret

def _gatherNgram(row):
    ema, url, cz, tz = row  # cz/tz are for cantizans/tenorizans
    piece = importScore(url)
    nr = piece.notes()
    di = piece.detailIndex(nr, offset=True)
    excerpt = ema2ex(ema, di)
    if len(excerpt.columns) != 2 or len(excerpt) == 0:
        return (False,)*4
    n = len(excerpt)
    ngrams = piece.ngrams(n=n, how='modules', offsets='last')
    pair = '_'.join(excerpt.columns)
    if pair not in ngrams.columns:
        pair = '_'.join(reversed(excerpt.columns))
    if excerpt.index[-1][-1] not in ngrams.index:
        return (False,)*4
    ngram = ngrams.at[excerpt.index[-1][-1], pair]
    lower, upper = pair.split('_')
    lower_cvf, upper_cvf = '', ''
    if cz == lower:
        lower_cvf = 'Cantizans'
    elif tz == lower:
        lower_cvf = 'Tenorizans'
    if cz == upper:
        upper_cvf = 'Cantizans'
    elif tz == upper:
        upper_cvf = 'Tenorizans'
    return ngram, n, lower_cvf, upper_cvf

def gatherNgrams(df, ema_col='ema', piece_col='piece.piece_id', filename=''):
    url_root = 'https://crimproject.org/mei/'
    df2 = df.loc[:, [ema_col, piece_col, 'mt_cad_cantizans', 'mt_cad_tenorizans']].copy()
    df2[piece_col] = url_root + df2[piece_col] + '.mei'
    ngrams = df2.apply(_gatherNgram, axis=1, result_type='expand')
    ngrams.columns = ('Ngram', 'N', 'LowerCVF', 'UpperCVF')
    ngrams = ngrams[~ngrams.Ngram.isin((False, float('nan')))]
    if filename:
        if filename[-4:] != '.csv':
            filename += '.csv'
        path = './data/cadences/' + filename
        ngrams.to_csv(path, index=False)
    else:
        return ngrams


