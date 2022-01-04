import numpy as np
#from main import *
from .main_objs import CorpusBase
import pandas as pd
import numpy as np
import re


# Converts lists to tuples
def lists_to_tuples(el):
    if isinstance(el, list):
        return tuple(el)
    else:
        return el


# Filters for the length of the Presentation Type in the Classifier
def limit_offset_size(array, limit):
    under_limit = np.cumsum(array) <= limit
    return array[: sum(under_limit)]


# Gets the the list of offset differences for each group


def get_offset_difference_list(group):
    # if we do sort values as part of the func call, then we don't need this first line
    group = group.sort_values("start_offset")
    group["next_offset"] = group.start_offset.shift(-1)
    offset_difference_list = (group.next_offset - group.start_offset).dropna().tolist()
    return offset_difference_list


# The classifications are done here
# be sure to have the offset difference limit set here and matched in gap check below  80 = ten bars
def classify_offsets(offset_difference_list, offset_difference_limit):
    """
    Put logic for classifying an offset list here
    """
    #
    offset_difference_list = limit_offset_size(offset_difference_list, offset_difference_limit)

    alt_list = offset_difference_list[::2]

    if len(set(offset_difference_list)) == 1 and len(offset_difference_list) > 1:
        return ("PEN", offset_difference_list)
    # elif (len(offset_difference_list) %2 != 0) and (len(set(alt_list)) == 1):
    elif (len(offset_difference_list) % 2 != 0) and (len(set(alt_list)) == 1) and (len(offset_difference_list) >= 3):
        return ("ID", offset_difference_list)
    elif len(offset_difference_list) >= 1:
        return ("Fuga", offset_difference_list)
    else:
        return ("Singleton", offset_difference_list)


def predict_type(group, offset_difference_limit):
    offset_differences = get_offset_difference_list(group)
    predicted_type, offsets = classify_offsets(offset_differences, offset_difference_limit)

    group["predicted_type"] = [predicted_type for i in range(len(group))]
    group["offset_diffs"] = [offsets for i in range(len(group))]
    group["entry_number"] = [i + 1 for i in range(len(group))]

    return group


def batch_classify(
    corpus_titles,
    duration_type="real",
    interval_type="generic",
    match_type="close",
    min_exact_matches=2,
    min_close_matches=3,
    close_distance=1,
    vector_size=4,
    increment_size=4,
    forward_gap_limit=40,
    backward_gap_limit=40,
    min_sum_durations=10,
    max_sum_durations=30,
    offset_difference_limit=500,
):

    # crim = "https://raw.githubusercontent.com/CRIM-Project/CRIM-online/master/crim/static/mei/MEI_3.0/"

    for title in corpus_titles:
        # path = f"{crim}{title}"
        path = f"{title}"
        clean_title = re.search("[a-zA-Z_\d]+", title).group()

    # for piece in corpus_titles:

        corpus = CorpusBase([path])

        if duration_type == "real":
            vectors = IntervalBase(corpus.note_list)

        elif duration_type == "incremental":
            vectors = IntervalBase(corpus.note_list_incremental_offset(increment_size))

        if interval_type == "generic":

            patterns = into_patterns([vectors.generic_intervals], vector_size)

        elif interval_type == "semitone":

            patterns = into_patterns([vectors.semitone_intervals], vector_size)

        if match_type == "exact":

            exact_matches = find_exact_matches(patterns, min_exact_matches)
            output_exact = export_pandas(exact_matches)
            df = output_exact

            df["note_durations"] = df["note_durations"].map(lambda x: pd.eval(x))
            df["start_offset"] = df["start_offset"].map(lambda x: pd.eval(x))
            df["end_offset"] = df["end_offset"].map(lambda x: pd.eval(x))
            df["pattern_generating_match"] = df["pattern_generating_match"].apply(tuple)
            df["pattern_matched"] = df["pattern_matched"].apply(tuple)
            df["sum_durs"] = df.note_durations.apply(sum)
            df = df.round(2)

        elif match_type == "close":

            close_matches = find_close_matches(patterns, min_close_matches, close_distance)
            output_close = export_pandas(close_matches)
            output_close["pattern_generating_match"] = output_close["pattern_generating_match"].apply(tuple)
            df = output_close
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            df["note_durations"] = df["note_durations"].map(lambda x: pd.eval(x))
            df["start_offset"] = df["start_offset"].map(lambda x: pd.eval(x))
            df["end_offset"] = df["end_offset"].map(lambda x: pd.eval(x))
            df["pattern_generating_match"] = df["pattern_generating_match"].apply(tuple)
            df["pattern_matched"] = df["pattern_matched"].apply(tuple)
            df["sum_durs"] = df.note_durations.apply(sum)
            df = df.round(2)

        df2 = df

        # Make Groups, Sort By Group and Offset, then and Add Previous/Next
        df2["group_number"] = df2.groupby("pattern_matched").ngroup()
        df2 = df2.sort_values(["group_number", "start_offset"])
        df2["prev_entry_off"] = df2["start_offset"].shift(1)
        df2["next_entry_off"] = df2["start_offset"].shift(-1)

        first_of_group = df2.drop_duplicates(subset=["pattern_matched"], keep="first").index
        df2["is_first"] = df2.index.isin(first_of_group)
        last_of_group = df2.drop_duplicates(subset=["pattern_matched"], keep="last").index
        df2["is_last"] = df2.index.isin(last_of_group)

        # Check Differences between Next and Last Offset

        df2["last_off_diff"] = df2["start_offset"] - df2["prev_entry_off"]
        df2["next_off_diff"] = df2["next_entry_off"] - df2["start_offset"]

        # Find Parallel Entries
        df2["parallel"] = df2["last_off_diff"] == 0

        # Set Gap Limits and Check Gaps Forward and Back
        df2["forward_gapped"] = df2["next_off_diff"] >= forward_gap_limit
        df2["back_gapped"] = df2["last_off_diff"] >= backward_gap_limit

        # Find Singletons and Split Groups with Gaps
        df2["singleton"] = (df2["forward_gapped"] == True) & (df2["back_gapped"] == True) | (
            df2["back_gapped"] == True
        ) & (df2["is_last"])
        df2["split_group"] = (df2["forward_gapped"] == False) & (df2["back_gapped"] == True)

        # Mask Out Parallels and Singletons
        df2 = df2[df2["parallel"] != True]
        df2 = df2[df2["singleton"] != True]
        df2["next_off_diff"] = df2["next_off_diff"].abs()
        df2["last_off_diff"] = df2["last_off_diff"].abs()

        # Find Final Groups
        df2["combined_group"] = df2.split_group | df2.is_first
        df2.loc[(df2["combined_group"]), "sub_group_id"] = range(df2.combined_group.sum())
        df2["sub_group_id"] = df2["sub_group_id"].ffill()

        ###
        ### FILTER SHORT OR LONG ENTRIES
        ###
        df2 = df2[df2["sum_durs"] >= min_sum_durations]
        df2 = df2[df2["sum_durs"] <= max_sum_durations]

        classified2 = (
            df2.applymap(lists_to_tuples)
            .groupby("sub_group_id")
            .apply(lambda x: predict_type(x, offset_difference_limit))
        )

        # OPTIONAL:  drop the new singletons

        classified2.drop(classified2[classified2["predicted_type"] == "Singleton"].index, inplace=True)

        # OPTIONAL:  select only certain presentation types

        # classified2 = classified2[classified2["predicted_type"] == "PEN"]

        classified2["start"] = classified2["start_measure"].astype(str) + "/" + classified2["start_beat"].astype(str)
        classified2.drop(columns=["start_measure", "start_beat", "offset_diffs"], inplace=True)

        # put things back in order by offset and group them again
        classified2.sort_values(by=["start_offset"], inplace=True)
        # return classified2
        # Now transform as Pivot Table
        pivot = classified2.pivot_table(
            index=["piece_title", "pattern_generating_match", "pattern_matched", "predicted_type", "sub_group_id"],
            columns="entry_number",
            values=["part", "start_offset", "start", "sum_durs"],
            aggfunc=lambda x: x,
        )
        pivot_sort = pivot.sort_values(by=[("start_offset", 1)])
        pivot_sort = pivot_sort.fillna("-")
        pivot_sort.reset_index(inplace=True)
        # pivot_sort = pivot_sort.drop(columns=["sub_group_id", "start_offset"], level=0)
        pivot_sort = pivot_sort.drop(columns=["sub_group_id"], level=0)
        return pivot_sort
