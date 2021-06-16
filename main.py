from main_objs import *

# Potential redesign needed due to unstable nature of having user give over patterns_data
# Potential fix is reincorporating into_patterns back into this method
def find_exact_matches(patterns_data, min_matches=5):
    """Takes in a series of vector patterns with data attached and finds exact matches

    Parameters
    ----------
    patterns_data : return value from into_patterns
        MUST be return value from into_patterns
    min_matches : int, optional
        Minimum number of matches needed to be deemed relevant, defaults to 5

    Returns
    -------
    all_matches_list : list
        A list of PatternMatches objects
    """
    # A series of arrays are needed to keep track of various data associated with each pattern
    print("Finding exact matches...")
    patterns_nodup, patterns = [], []
    p = 0
    for pattern in patterns_data:
        patterns.append(pattern[0])
        if pattern[0] not in patterns_nodup:
            patterns_nodup.append(pattern[0])
    m = 0
    # Go through each individual pattern and count up its occurences
    all_matches_list = []
    for p in patterns_nodup:
        amt = patterns.count(p)
        # If a pattern occurs more than the designated threshold, we add it to our list of matches
        if amt > min_matches:
            matches_list = PatternMatches(p, [])
            m += 1
            for a in patterns_data:
                if p == a[0]:
                    exact_match = Match(p, a[1], a[2], a[3])
                    matches_list.matches.append(exact_match)
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact matches.\n")
    # all_matches_list has a nested structure- it contains a list of PatternMatches objects, which contain a list of individual Match objects
    return all_matches_list

# Finds matches based on a cumulative distance difference between two patterns
def find_close_matches(patterns_data, min_matches, threshold):
    """Takes in a series of vector patterns with data attached and finds close matches

    Parameters
    ----------
    patterns_data : return value from into_patterns
        MUST be return value from into_patterns
    min_matches : int, optional
        Minimum number of matches needed to be deemed relevant, defaults to 5
    threshold : int
        Cumulative variance allowed between vector patterns before they are deemed not similar

    Returns
    -------
    all_matches_list : list
        A list of PatternMatches objects
    """
    # A series of arrays are needed to keep track of various data associated with each pattern
    print("Finding close matches...")
    patterns_nodup = []
    for pat in patterns_data:
        # Build up a list of patterns without duplicates
        if pat[0] not in patterns_nodup:
            patterns_nodup.append(pat[0])
    # Go through each individual pattern and count up its occurences
    all_matches_list = []
    for p in patterns_nodup:
        matches_list = PatternMatches(p, [])
        # If a pattern occurs more than the designated threshold
        for a in patterns_data:
            rhytmic_match = 0
            # Calculate the "difference" by comparing each vector with the matching one in the other pattern
            for v in range(len(a[0])):
                rhytmic_match += abs(p[v] - a[0][v])
            if rhytmic_match <= threshold:
                close_match = Match(a[0], a[1], a[2], a[3])
                matches_list.matches.append(close_match)
        if len(matches_list.matches) > min_matches:
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact or close matches.\n")
    return all_matches_list

# Allows for the addition of non-moving-window pattern searching approaches
# Needs to be called before any matches can be made
def into_patterns(vectors_list, interval):
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
    pattern, patterns_data = [], []
    for vectors in vectors_list:
        for i in range(len(vectors)-interval):
            pattern = []
            durations = []
            valid_pattern = True
            durations.append(vectors[i].note1.duration)
            for num_notes in range(interval):
                if vectors[i+num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors[i+num_notes].vector)
                durations.append(vectors[i+num_notes].note2.duration)
            if valid_pattern:
            # Here, with help from vectorize() you can jam in whatever more data you would like about the note
                patterns_data.append((pattern, vectors[i].note1, vectors[i+num_notes].note2, durations))
    return patterns_data

def into_patterns_pd(df:list, interval_size):
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
        vectors_list.append(float('nan'));
    pattern, patterns_data = [], []
    for h in range(len(vectors_list)-interval_size):
        pattern = []
        valid_pattern = True
        for num_notes in range(interval_size):
            if pd.isna(vectors_list[h+num_notes]):
                valid_pattern = False
            pattern.append(vectors_list[h+num_notes])
        if valid_pattern:
        # Here, with help from vectorize() you can jam in whatever more data you would like about the note
            patterns_data.append((pattern, vectors_list[i], vectors_list[i+num_notes]))
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

        for i in range(len(vectors1)-interval):
            pattern = []
            valid_pattern = True
            for num_notes in range(interval):
                if vectors1[i+num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors1[i+num_notes].vector)
            if valid_pattern:
                patterns1.append(pattern)

        for j in range(len(vectors2)-interval):
            pattern = []
            valid_pattern = True
            for num_notes in range(interval):
                if vectors2[j+num_notes].vector == 'Rest':
                    valid_pattern = False
                pattern.append(vectors2[j+num_notes].vector)
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
                        #score += 0.5
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
            print("Selected pattern occurs in " + str(pat[1].metadata.title) + " part " + str(pat[1].part) + " beginning in measure " + str(pat[1].note.measureNumber) + " and ending in measure " + str(pat[2].note.measureNumber) + ". Note durations: " + str(pat[3]))
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
            matches_writer.writerow(['Pattern Generating Match', 'Pattern matched', 'Piece Title', 'Part', 'First Note Measure Number', 'Last Note Measure Number', 'Note Durations', 'EMA', 'EMA url'])
            for match_series in matches:
                for match in match_series.matches:
                    matches_writer.writerow([match_series.pattern, match.pattern, match.first_note.metadata.title, match.first_note.part, match.first_note.note.measureNumber, match.last_note.note.measureNumber, match.durations, match.ema, match.ema_url])
        else:
            matches_writer.writerow(['Pattern Generating Match', 'Classification Type', 'EMA', 'EMA url', 'Soggetti 1 Part', 'Soggetti 1 Measure', 'Soggetti 2 Part', 'Soggetti 2 Measure', 'Soggetti 3 Part', 'Soggetti 3 Measure', 'Soggetti 4 Part', 'Soggetti 4 Measure'])
            for classified_matches in matches:
                row_array = [classified_matches.pattern, classified_matches.type, classified_matches.ema, classified_matches.ema_url]
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
    print("You can use ctrl-c to quit exit at any time. If you proceed through the entire process, the matches array will be returned from this function")
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
        total += abs(durations1[i]-durations2[i])
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


def classify_matches(exact_matches: list, durations_threshold = 2):
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
        match_instance.sort(key = sortMatches)
        for index in range(len(match_instance) - 1):
            if compare_durations(match_instance[index + 1].durations, match_instance[index].durations, durations_threshold):
                offset_difs.append(match_instance[index + 1].first_note.offset -  match_instance[index].first_note.offset)
                offset_difs_info.append((match_instance[index], match_instance[index + 1]))
        i = 0
        while i < len(offset_difs) - 2:
            if offset_difs[i] > 64 or offset_difs[i + 1] > 64 or abs(offset_difs_info[i][1].last_note.note.measureNumber - offset_difs_info[i + 1][0].first_note.note.measureNumber) > 8:
                pass
            elif offset_difs[i] == offset_difs[i + 1] and offset_difs[i] == offset_difs[i + 2]:
                grouping = (offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1], offset_difs_info[i + 2][0], offset_difs_info[i + 2][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "periodic_entry")
                classified_matches.append(classified_obj)
            elif offset_difs[i] == offset_difs[i + 1]:
                grouping = (offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "periodic entry")
                classified_matches.append(classified_obj)
            elif offset_difs[i] == offset_difs[i + 2]:
                grouping = (offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 2][0], offset_difs_info[i + 2][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "imitative duo")
                classified_matches.append(classified_obj)
            else:
                grouping = (offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1])
                grouping = list(dict.fromkeys(grouping))
                classified_obj = ClassifiedMatch(grouping, "fuga")
                classified_matches.append(classified_obj)
            i += 1

    for entry in classified_matches:
        print(str(entry.type) + ":")
        desc_str = "Pattern: " + str(entry.pattern) + ", Locations in entry: "
        for soggetti in entry.matches:
            desc_str += "\n- Measure " + str(soggetti.first_note.note.measureNumber) + " in voice " + str(soggetti.first_note.partNumber)
        print(desc_str)

    return classified_matches

def export_pandas(matches):
    match_data = []
    for match_series in matches:
        for match in match_series.matches:
            match_dict = {
              "pattern_generating_match": match_series.pattern,
              "pattern_matched": match.pattern,
              "piece_title": match.first_note.metadata.title,
              "part": match.first_note.part,
              "start_measure": match.first_note.note.measureNumber,
              "start_beat": match.first_note.note.beat,
              "end_measure": match.last_note.note.measureNumber,
              "end_beat": match.last_note.note.beat,
              "start_offset": match.first_note.offset,
              "end_offset": match.last_note.offset,
              "note_durations": match.durations,
              "ema": match.ema,
              "ema_url": match.ema_url
            }
            match_data.append(match_dict)
    return pd.DataFrame(match_data)
