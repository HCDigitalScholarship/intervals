from main_objs import *

def into_patterns_pd(df: list, interval_size):
    """Takes in a series of vector patterns with data attached and finds close matches

    Parameters
    ----------
    vectors_list : list of vectorized lists
        MUST be a list from calling generic_intervals or semitone_intervals on a VectorInterval object
    interval : int
        size of interval to be analyzed

    Returns
    -------
    patterns_data : list of tuples
        A list of vector patterns with additional information about notes attached
    """
    dflist = df.values.tolist()
    vectors_list = []
    for i in range(len(dflist[0])):
        for j in range(len(dflist)):
            vectors_list.append(dflist[j][i])
        vectors_list.append(float('nan'))
    pattern, patterns_data = [], []
    for h in range(len(vectors_list) - interval_size):
        pattern = []
        valid_pattern = True
        for num_notes in range(interval_size):
            if pd.isna(vectors_list[h + num_notes]):
                valid_pattern = False
            pattern.append(vectors_list[h + num_notes])
        if valid_pattern:
            # Here, with help from vectorize() you can jam in whatever more data you would like about the note
            patterns_data.append((pattern, vectors_list[i], vectors_list[i + num_notes]))
    return patterns_data

# sample usage
# a = into_patterns_pd(melodic, 5)
# a.sort()

# Helper for sort_matches
def sortFunc(pattern):
    """Helper function for sort_matches
    """
    return len(pattern.matches)

# Sorting based on the amount of matches each pattern has
def sort_matches(matches_list):
    """Sorts and returns a list of PatternMatch objects, ordering by size
    """
    matches_list.sort(reverse=True, key=sortFunc)
    return matches_list

# Generates a score from 0-1 based on how many patterns within a piece can be found in the other
def similarity_score(notes1, notes2):
    """Returns a score from 0-1 of the similarity between two note lists

    Parameters
    ----------
    notes1 : list of NoteListElement objects
        a note list from the CorpusBase or ScoreBase methods
    notes2 : list of NoteListElement objects
        a note list from the CorpusBase or ScoreBase methods

    Returns
    -------
    final_score : int
        a score of similarity from 0-1
    """
    vectors1 = IntervalBase(notes1).generic_intervals
    vectors2 = IntervalBase(notes2).generic_intervals
    interval = 3
    scores = []
    while interval <= 6:
        # For each piece create a list of all patterns and then a list of unique patterns to compare against it
        pattern, patterns1, patterns_nodup1, patterns2, patterns_nodup2 = [], [], [], [], []

        for i in range(len(vectors1) - interval):
            pattern = []
            valid_pattern = True
            for num_notes in range(interval):
                if vectors1[i + num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors1[i + num_notes].vector)
            if valid_pattern:
                patterns1.append(pattern)

        for j in range(len(vectors2) - interval):
            pattern = []
            valid_pattern = True
            for num_notes in range(interval):
                if vectors2[j + num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors2[j + num_notes].vector)
            if valid_pattern:
                patterns2.append(pattern)

        for pat in patterns1:
            if pat not in patterns_nodup1:
                patterns_nodup1.append(pat)
        for pat2 in patterns2:
            if pat2 not in patterns_nodup2:
                patterns_nodup2.append(pat2)

        # With lists assembled we can do an easy comparison
        score = 0
        for a in patterns_nodup1:
            if patterns2.count(a) > 3:
                score += 1
            if patterns2.count(a) > 0:
                score += 1
            else:
                for b in patterns2:
                    diff = 0
                    for c in range(interval):
                        diff += abs(a[c] - b[c])
                    if diff == 1 or diff == 2:
                        # score += 0.5
                        break
        for d in patterns_nodup2:
            if patterns1.count(d) > 3:
                score += 1
            if patterns1.count(d) > 0:
                score += 1
            else:
                for e in patterns1:
                    diff = 0
                    for f in range(interval):
                        diff += abs(d[f] - e[f])
                    if diff == 1 or diff == 2:
                        #score += 0.5
                        break
        interval += 1
        scores.append(score / (len(patterns_nodup2) + len(patterns_nodup1)))
    final_score = (scores[0] + scores[1] + scores[2] + scores[3]) / 4
    return final_score

# Find all occurences of a specified pattern within a corpus
def find_motif(pieces: CorpusBase, motif: list, generic: bool = True):
    """Prints out all occurences of a specified motif

    Parameters
    ----------
    pieces : CorpusBase
        a CorpusBase object with all scores to be searched
    motif : list
        the motif in vectors (e.g. [-2,-2,2,-2,2])
    generic : bool, optional
        True to use generic vectors, False for semitone vectors- default is generic
    """
    # Assemble into patterns
    vectors = IntervalBase(pieces.note_list)
    if generic:
        patterns = into_patterns([vectors.generic_intervals], len(motif))
    else:
        patterns = into_patterns([vectors.semitone_intervals], len(motif))
    print("Finding instances of pattern " + str(motif) + ": ")
    # Find all occurences of given motif, print out information associated
    occurences = 0
    for pat in patterns:
        if motif == pat[0]:
            print("Selected pattern occurs in " + str(pat[1].metadata.title) + " part " + str(
                pat[1].part) + " beginning in measure " + str(
                pat[1].note.measureNumber) + " and ending in measure " + str(
                pat[2].note.measureNumber) + ". Note durations: " + str(pat[3]))
            occurences += 1
    print("Selected pattern occurs " + str(occurences) + " times.")

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

# For more naive usage- allows for user interaction, has return value of list of matches
# All features incorporated except non-whole piece selection
def assisted_interface():
    """Activates the assisted interface for more naive use

    Returns
    ----------
    matches : list
        list of PatternMatches based on the users various inputs
    """
    print(
        "You can use ctrl-c to quit exit at any time. If you proceed through the entire process, the matches array will be returned from this function")
    urls = []
    url = input("Enter a url, or 'done' when finished: ")
    while url != 'done':
        urls.append(url)
        url = input("Enter a url, or 'done' when finished: ")
    corpus = CorpusBase(urls, [])
    vectors = IntervalBase(corpus.note_list)
    pattern_size = int(input("Enter the size of pattern you would like to analyze: "))
    interval_type = input("Enter 1 to match using generic intervals or enter 2 to match using semitone intervals: ")
    while interval_type != '1' and interval_type != '2':
        interval_type = input("Invalid input, enter 1 for generic intervals or 2 for semitone intervals: ")
    if interval_type == '1':
        patterns = into_patterns([vectors.generic_intervals], pattern_size)
    if interval_type == '2':
        patterns = into_patterns([vectors.semitone_intervals], pattern_size)
    min_matches = int(input("Enter the minimum number of matches needed to be displayed: "))
    close_or_exact = input("Enter 1 to include close matches or enter 2 for only exact matches: ")
    while close_or_exact != '1' and close_or_exact != '2':
        close_or_exact = input("Invalid input, enter 1 for close matches or 2 for only exact matches: ")
    if close_or_exact == '1':
        max_dif = int(input("Enter the maximum total distance threshold for a close match: "))
        matches = find_close_matches(patterns, min_matches, max_dif)
    if close_or_exact == '2':
        matches = find_exact_matches(patterns, min_matches)
    csv_results = input("Export results to CSV? (y/n): ").lower()
    if csv_results == 'y' or csv_results == 'yes':
        export_to_csv(matches)
    print_results = input("Print results? (y/n): ").lower()
    if print_results == 'y' or print_results == 'yes':
        if close_or_exact == '1':
            for item in matches:
                item.print_close_matches()
        if close_or_exact == '2':
            for item in matches:
                item.print_exact_matches()
    return matches

def compare_durations(durations1, durations2, threshold):
    """Helper for classify_matches

    works similarly to find_close_matches in terms of its comparison technique
    """
    total = 0
    durations1_sum, durations2_sum = 0, 0
    for i in range(len(durations1)):
        total += abs(durations1[i] - durations2[i])
        durations1_sum += durations1[i]
        durations2_sum += durations2[i]
    # if total <= threshold or durations1_sum == durations2_sum:
    if total <= threshold:
        return True
    else:
        return False

def sortMatches(match):
    """ Helper function for classify_matches
    """
    return match.first_note.offset


def classify_matches(exact_matches: list, durations_threshold=2):
    """Classifies groups of matches into periodic entries, imitative duos, and fuga

    Classifies through offset comparison of matching melodic patterns, prints out information gathered.
    Reliably accurate results only guaranteed if exact_matches is generated from ONE piece.

    Parameters
    ----------
    exact_matches : list
        return value from find_exact_matches
    durations_threshold : int, optional
        maximum cumulative difference between two duration lists before they are deemed not similar, defaults to 2

    Returns
    -------
    classified_tuple : tuple
        classified_tuple[0] : list of lists of Match objects
            list of periodic entries, which are lists of Match objects
        classified_tuple[1] : list of lists of Match objects
            list of imitative_duos, which are lists of Match objects
        classified_tuple[0] : list of lists of Match objects
            list of fuga, which are lists of Match objects
    """
    classified_matches = []
    for list_matches in exact_matches:
        offset_difs, offset_difs_info = [], []
        match_instance = list_matches.matches
        match_instance.sort(key=sortMatches)
        for index in range(len(match_instance) - 1):
            if compare_durations(match_instance[index + 1].durations, match_instance[index].durations,
                                 durations_threshold):
                offset_difs.append(
                    match_instance[index + 1].first_note.offset - match_instance[index].first_note.offset)
                offset_difs_info.append((match_instance[index], match_instance[index + 1]))
        i = 0
        while i < len(offset_difs) - 2:
            if offset_difs[i] > 64 or offset_difs[i + 1] > 64 or abs(
                    offset_difs_info[i][1].last_note.note.measureNumber - offset_difs_info[i + 1][
                        0].first_note.note.measureNumber) > 8:
                pass
            elif offset_difs[i] == offset_difs[i + 1] and offset_difs[i] == offset_difs[i + 2]:
                grouping = (
                offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1],
                offset_difs_info[i + 2][0], offset_difs_info[i + 2][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "periodic_entry")
                classified_matches.append(classified_obj)
            elif offset_difs[i] == offset_difs[i + 1]:
                grouping = (
                offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "periodic entry")
                classified_matches.append(classified_obj)
            elif offset_difs[i] == offset_difs[i + 2]:
                grouping = (
                offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 2][0], offset_difs_info[i + 2][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "imitative duo")
                classified_matches.append(classified_obj)
            else:
                grouping = (
                offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "fuga")
                classified_matches.append(classified_obj)
            i += 1

    for entry in classified_matches:
        print(str(entry.type) + ":")
        desc_str = "Pattern: " + str(entry.pattern) + ", Locations in entry: "
        for soggetti in entry.matches:
            desc_str += "\n- Measure " + str(soggetti.first_note.note.measureNumber) + " in voice " + str(
                soggetti.first_note.partNumber)
        print(desc_str)

    return classified_matches

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
    nr = piece.getNoteRest()
    di = piece.detailIndex(nr, offset=True)
    excerpt = ema2ex(ema, di)
    if len(excerpt.columns) != 2 or len(excerpt) == 0:
        return (False,)*4
    n = len(excerpt)
    ngrams = piece.getNgrams(n=n, how='modules', offsets='last')
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


