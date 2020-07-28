from main_objs import *

# Standalone methods for match analysis
def find_exact_matches(patterns_data, min_matches):
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
            match = 0
            # Calculate the "difference" by comparing each vector with the matching on in the other pattern
            for v in range(len(a[0])):
                match += abs(p[v] - a[0][v])
            if match <= threshold:
                close_match = Match(a[0], a[1], a[2], a[3])
                matches_list.matches.append(close_match)
        if len(matches_list.matches) > min_matches:
            all_matches_list.append(matches_list)
    print(str(len(all_matches_list)) + " melodic intervals had more than " + str(min_matches) + " exact or close matches.\n")
    return all_matches_list

# Allows for the addition of non-moving-window pattern searching approaches
# Needs to be called before any matches can be made
def into_patterns(vectors_list, interval):
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

# Helper for sort_matches
def sortFunc(pattern):
    return len(pattern.matches)

# Sorting based on the amount of matches each pattern has
def sort_matches(matches_list):
    matches_list.sort(reverse=True, key=sortFunc)
    return matches_list

# Generates a score from 0-1 based on how many patterns within a piece can be found in the other
def similarity_score(notes1, notes2):
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
    return (scores[0] + scores[1] + scores[2] + scores[3]) / 4

# Find all occurences of a specified pattern within a corpus
def find_motif(pieces: CorpusBase, motif: list, generic: bool):
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
    proceed = input("This method will create a csv file in your current working directory. Continue? (y/n): ").lower()
    csv_name = input("Enter a name for your csv file (.csv will be appended): ")
    csv_name += '.csv'
    if proceed != 'y' and proceed != 'yes':
        print("Exiting...")
        return
    import csv
    with open(csv_name, mode='w') as matches_file:
        matches_writer = csv.writer(matches_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        matches_writer.writerow(['Pattern Generating Match', 'Pattern matched', 'Piece Title', 'Part', 'First Note Measure Number', 'Last Note Measure Number', 'Note Durations', 'EMA', 'EMA url'])
        for match_series in matches:
            for match in match_series.matches:
                matches_writer.writerow([match_series.pattern, match.pattern, match.first_note.metadata.title, match.first_note.part, match.first_note.note.measureNumber, match.last_note.note.measureNumber, match.durations, match.ema, match.ema_url])
    print("CSV created in your current working directory.")

# For more naive usage- allows for user interaction, has return value of list of matches
# All features incorporated except non-whole piece selection
def assisted_interface():
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

def sortMatches(match):
    return match.first_note.offset

def compare_durations(durations1, durations2, threshold):
    total = 0
    durations1_sum, durations2_sum = 0, 0
    for i in range(len(durations1)):
        total += abs(durations1[i]-durations2[i])
        durations1_sum += durations1[i]
        durations2_sum += durations2[i]
    if total <= threshold or durations1_sum == durations2_sum:
        return True
    else:
        return False

def classify_matches(exact_matches: list, duration_threshold):
    # TO-DO: add in factoring for durations, narrow 80 beats window
    periodic_entries, im_duos, fuga = [], [], []
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
            if offset_difs[i] > 64 or offset_difs[i + 1] > 64:
                pass
            elif offset_difs[i] == offset_difs[i + 1] and offset_difs[i] == offset_difs[i + 2]:
                periodic_entries.append((offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1], offset_difs_info[i + 2][0], offset_difs_info[i + 2][1]))
            elif offset_difs[i] == offset_difs[i + 1]:
                periodic_entries.append((offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1]))
            elif offset_difs[i] == offset_difs[i + 2]:
                im_duos.append((offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 2][0], offset_difs_info[i + 2][1]))
            else:
                fuga.append((offset_difs_info[i][0], offset_difs_info[i][1], offset_difs_info[i + 1][0], offset_difs_info[i + 1][1]))
            i += 1
    for entry in periodic_entries:
        print("Periodic Entry:")
        a = "Pattern: " + str(entry[0].pattern) + ", Locations in entry: "
        for b in entry:
            a += "\n- Measure " + str(b.first_note.note.measureNumber) + " in voice " + str(b.first_note.partNumber)
        print(a)
    for duo in im_duos:
        print("Imitative Duo:")
        a = "Pattern: " + str(entry[0].pattern) + ", Locations in entry: "
        for c in duo:
            a += "\n- Measure " + str(c.first_note.note.measureNumber) + " in voice " + str(c.first_note.partNumber)
        print(a)
    for f in fuga:
        print("Fuga:")
        a = "Pattern: " + str(entry[0].pattern) + ", Locations in entry: "
        for d in f:
            a += "\n- Measure " + str(d.first_note.note.measureNumber) + " in voice " + str(d.first_note.partNumber)
        print(a)
    return ((periodic_entries, im_duos, fuga))
