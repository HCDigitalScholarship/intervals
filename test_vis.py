"""
This file contains unit tests for visualizations.
 pytest --cov visualizations test_vis.py --cov-report term-missing


UNIT TESTING DOC GUIDE LINE
 what is being tested, the situation under test and the expected behavior.
"""

import altair as alt
import pandas as pd
import visualizations as viz

from main_objs import CorpusBase
from strsimpy.levenshtein import Levenshtein
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from test_constants import EXAMPLE_CRIM_FILE, OBSERVATIONS_DICT_EXAMPLE, RELATIONSHIPS_DICT_EXAMPLE


def ngrams_heatmap_chart(chart):
    """
    The assert step to testing viz.plot_ngrams_heatmap.
    With a normal or empty dataframe, makes sure that two
    charts are displayed.
    """
    # retrieved two charts: one pattern bar chart
    # and one heatmap
    assert isinstance(chart, alt.VConcatChart)
    assert len(chart.vconcat) == 2
    assert isinstance(chart.vconcat[0], alt.Chart)
    assert isinstance(chart.vconcat[1], alt.Chart)

def ngrams_heatmap_test_helper(model, notes):
    """
    Include the three steps to unit testing--arrange, act, and assert--for
    optional parameters in viz.plot_ngrams_heatmap (ngram_duration, selected_patterns,
    voices) in the case of fixed length ngram (n=5) and variable length ngrams (n=-1),
    we would receive the correct output with 2 charts.
    :param model: model arranged from the outer method
    :param notes: the main melody to create ngrams out of
    """
    # test no durations
    ngrams = model.getNgrams(df=notes, n=5)
    chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams)
    ngrams_heatmap_chart(chart)

    # test no durations
    ngrams_multiple = model.getNgrams(df=notes, n=-1)
    chart_multiple = viz.plot_ngrams_heatmap(ngrams_df=ngrams_multiple)
    ngrams_heatmap_chart(chart_multiple)

    # popular pattern
    popular_patterns = ngrams.stack().dropna().value_counts().head(10).index.to_list()
    selected_patterns_chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams, selected_patterns=popular_patterns)
    ngrams_heatmap_chart(selected_patterns_chart)

    # select all voices but the last one
    selected_voices = ngrams.columns.to_list()[:-1]
    selected_voices_chart = viz.plot_ngrams_heatmap(ngrams, voices = selected_voices)
    ngrams_heatmap_chart(selected_voices_chart)

    # with duration!
    ngrams_dur = model.getDuration(df=notes, mask_df=ngrams, n=5)
    dur_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur)
    ngrams_heatmap_chart(dur_chart)

    # duration and filter voice
    dur_selected_voices_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur,
                                                        voices=selected_voices)
    ngrams_heatmap_chart(dur_selected_voices_chart)

    # duration and filter pattern
    dur_selected_patterns_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur,
                                                          selected_patterns=popular_patterns)
    ngrams_heatmap_chart(dur_selected_patterns_chart)

    # chart not displayed because the selected pattern and selected voice do not exist.
    chart_not_displayed = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur,
                                                  selected_patterns=['-2, -2, 1, -4, 1'], voices=['Bassus'])
    ngrams_heatmap_chart(chart_not_displayed)

    # with multiple lengths ngrams
    duration = model.getDuration(df=notes, n=-1, mask_df=ngrams)
    dur_chart_multiple = viz.plot_ngrams_heatmap(ngrams_multiple, ngrams_duration=duration)
    ngrams_heatmap_chart(dur_chart_multiple)

def test_plot_ngrams_heatmap():
    """
    test viz.plot_ngrams_heatmap with two types of melodic intervals
    on fixed/variable lengths ngrams and different parameters of viz.plot_ngrams_heatmap
    being used with the help from ngrams_heatmap_test_helper().
    """
    corpus = CorpusBase([EXAMPLE_CRIM_FILE])
    model = corpus.scores[0]

    # mel
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    ngrams_heatmap_test_helper(model, mel_notes)
    # diatonic
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    ngrams_heatmap_test_helper(model, mel_diatonic)


def helper_test_close_match_(model, notes, n):
    """
    test viz.plot_close_match_heatmap on a model and a ngram by
    selecting the 5 most popular patterns, and for each of these patterns,
    plot other patterns' manhattan distances against it and
    confirm that a correct chart with 2 charts will be output.
    :param model: an ImportedPiece object
    :param notes: the intervals we wanted to create ngrams out of
    :param n: the length of ngrams for getNgrams
    :return:
    """

    # arrange the ngrams and select the patterns to evaluate similarity
    ngrams = model.getNgrams(df=notes, n=n)
    popular_patterns = ngrams.stack().dropna().value_counts().head(5).index.to_list()
    score_df = model.getDistance(df=ngrams)
    ngrams_dur = model.getDuration(df=notes, mask_df=ngrams, n=5)
    for i in range(5):
        # act
        chart = viz.plot_close_match_heatmap(ngrams, popular_patterns[i], score_df, 'd',
                                             ngrams_dur)

        # assert that a correct chart with a bar chart and a heatmap is output
        assert isinstance(chart, alt.VConcatChart)
        assert len(chart.vconcat) == 2
        assert isinstance(chart.vconcat[0], alt.Chart)
        assert isinstance(chart.vconcat[1], alt.Chart)


def test_plot_close_match_heatmap():
    """
    test viz.plot_close_match_heatmap generates 2 charts for the two
    modes that getDistance could be used upon ('z', directed, compound)
    and ('c', directed, compound) and two types of ngrams (fixed length, variable length)
    with the help of helper_test_close_match().
    """
    corpus = CorpusBase([EXAMPLE_CRIM_FILE])
    model = corpus.scores[0]

    # ngrams in diatonics, fixed length
    mel_diatonic = model.getMelodic(kind='z', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_diatonic, n=5)

    # ngrams in chromatics, variable length
    mel_chromatic = model.getMelodic(kind='c', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_chromatic, n=-1)


def test_comparisons_heatmap():
    """
    test viz.plot_comparisons_heatmap() by using this on a small hardcoded relationships
    and observations dataframes, and make sure that we receive the correct output
    with two charts.
    """
    # test this method with relationships json
    df_relationships = pd.DataFrame(RELATIONSHIPS_DICT_EXAMPLE)
    relationships_chart = viz.plot_comparison_heatmap(df_relationships, 'model_observation.ema',
                                                      main_category='relationship_type', other_category='observer.name',
                                heat_map_width=800, heat_map_height=300)
    assert isinstance(relationships_chart, alt.VConcatChart)
    assert len(relationships_chart.vconcat) == 2

    # test this method with observations json
    df_observations = pd.DataFrame(OBSERVATIONS_DICT_EXAMPLE)
    observations_chart = viz.plot_comparison_heatmap(df_observations, 'ema',
                                                     main_category='musical_type', other_category='observer.name',
                                                     heat_map_width=800, heat_map_height=300)
    assert isinstance(observations_chart, alt.VConcatChart)
    assert len(observations_chart.vconcat) == 2


def helper_substitution_cost(char_a, char_b):
    """Helper substitution method to weight substitution less than insertion
    or deletion"""
    return 0.5


def test_score_ngram():
    """
    This method test viz.score_ngram with fixed length ngrams and variable length
    ngrams, and two algorithms (Levenshtein and Weighted Levenshtein) by
    calculating the scores and comparing the results against some hardcoded scores.
    """
    model = CorpusBase([EXAMPLE_CRIM_FILE]).scores[0]
    # hardcoded Levenshtein distance scores for ngrams of length 5 in Model 17
    some_hardcoded_ngrams_fixed_score = {('P1, M2, M2, m2, -P4', 'P1, M2, M2, m2, -P4'): 0.0,
                                         ('P1, M2, M2, m2, -P4', 'M2, M2, m2, -P4, P8'): 2.0,
                                         ('-P4, P5, -P4, M2, m2', '-M2, -M2, -M2, -m2, m2'): 4.0,
                                         ('-m3, m2, -m3, M2, -M2', '-m3, m2, -m3, M2, -M2'): 0.0,
                                         ('M2, M2, -P5, P5, -M2', 'M2, M2, -P5, P5, -M2'): 0.0}
    # hardcoded Weighted Levenshtein distance score for nrgams of variable lengths
    # in model 17
    some_hardcoded_ngrams_variable_score = {('1, 2, 2, 2, -4, 8, -2, -2, 2, -3, -2, 2, 2, 2, 2, 2, -3, 2',
                                             '1, 2, 2, 2, -4, 8, -2, -2, 2, -3, -2, 2, 2, 2, 2, 2, -3, 2'): 0.0, (
                                                '1, 2, 2, 2, -4, 8, -2, -2, 2, -3, -2, 2, 2, 2, 2, 2, -3, 2',
                                                '1, 2, 1, 2, -3'): 13.5, (
                                                '2, -2, -2, -2, 2, 2, 2, 2, 2, 2, -3, 2, 3, -2, -2, -3, 3, -2, -2, -2, 2',
                                                '2, -2, -2, -2, 2, 2, 2, 2, 2, 2, -3, 2, 3, -2, -2, -3, 3, -2, -2, -2, 2'): 0.0,
                                            ('-4, 3, -4, 5', '-4, 3, -4, 5'): 0.0, (
                                                '2, -5, 2, 2, 2, 2, -5, 2, 2, 2, 2, -5, 5, -2',
                                                '2, -5, 2, 2, 2, 2, -5, 2, 2, 2, 2, -5, 5, -2'): 0.0}

    # ngrams fixed length length
    nl = Levenshtein()
    ngrams_fixed = model.getNgrams(df=model.getMelodic(), n=5)

    score_fixed = viz.score_ngram(ngrams_fixed, nl.distance)

    hardcoded_score_fixed = pd.Series(some_hardcoded_ngrams_fixed_score)
    for pattern, other in hardcoded_score_fixed.index:
        assert (score_fixed.loc[pattern, other] == hardcoded_score_fixed.loc[pattern, other])

    # ngram different lengths, weighted
    wl = WeightedLevenshtein(substitution_cost_fn=helper_substitution_cost)
    ngrams_variable = model.getNgrams(df=model.getMelodic(kind='d'), n=-1)

    score_variable = viz.score_ngram(ngrams_variable, wl.distance)

    hardcoded_score_variable = pd.Series(some_hardcoded_ngrams_variable_score)
    for pattern, other in hardcoded_score_variable.index:
        assert (score_variable.loc[pattern, other] ==
                hardcoded_score_variable.loc[pattern, other])


def test_generate_networks_and_interactive_df():
    """
    test viz.create_comparisons_networks_and_interactive_df by
    confirming that it would generate networks with correct number
    of nodes and edges and interactive widgets when two type of
    intervals (melodic/time) are selected.
    """
    df_observations = pd.DataFrame(OBSERVATIONS_DICT_EXAMPLE)

    # time, pe
    # hard coded based on the hardcoded observation's dict, columns 'mt_pe_tint', 'time', 'ema'
    # {key -> (num nodes, num edges)}
    pen_networks_hardcoded = {'all': (13, 14), 'S1': (10, 9), 'nan': (0, 0), 'S2': (1, 0), 'M1': (1, 0)}
    pen_networks, pen_widget = viz.create_comparisons_networks_and_interactive_df(df_observations, 'mt_pe_tint', 'time',
                                                                                  'ema')
    for key in pen_networks:
        assert len(pen_networks[key].nodes) == pen_networks_hardcoded[key][0]
        assert len(pen_networks[key].edges) == pen_networks_hardcoded[key][1]

    assert pen_widget

    # melodic, fug
    fug_networks, fug_widget = viz.create_comparisons_networks_and_interactive_df(df_observations, 'mt_fg_int',
                                                                                  'melodic',
                                                                                  'ema')
    # melodic, fg
    # hard coded based on the hardcoded observation's dict, columns 'mt_fg_int', 'melodic', 'ema'
    # {key -> (num nodes, num edges)}
    fug_networks_hardcoded = {'all': (5, 5), 'nan': (0, 0), '1+': (0, 0), '5-': (0, 0), '8-': (0, 0), '4+': (2, 1),
                              '12+': (1, 0), '2+': (1, 0), '5+': (0, 0)}

    for key in fug_networks:
        assert len(fug_networks[key].nodes) == fug_networks_hardcoded[key][0]
        assert len(fug_networks[key].edges) == fug_networks_hardcoded[key][1]
    assert fug_widget

    # melodic, fg, filtered
    # hard coded based on the hardcoded observation's dict, columns 'mt_fg_int', 'melodic', 'ema'
    # {key -> (num nodes, num edges)}
    patterns = df_observations['mt_fg_int'].to_list()
    fug_networks_filtered, fug_widget_filtered = viz.create_comparisons_networks_and_interactive_df(df_observations,
                                                                                                    'mt_fg_int',
                                                                                                    'melodic', 'ema',
                                                                                                    patterns)

    assert fug_networks_filtered
    fug_networks_filtered_hardcoded = {'all': (5, 5), 'nan': (0, 0), '1+': (0, 0), '5-': (0, 0), '8-': (0, 0),
                                       '4+': (2, 1), '12+': (1, 0), '2+': (1, 0), '5+': (0, 0)}
    for key in fug_networks_filtered:
        assert len(fug_networks_filtered[key].nodes) == fug_networks_filtered_hardcoded[key][0]
        assert len(fug_networks_filtered[key].edges) == fug_networks_filtered_hardcoded[key][1]
    assert fug_widget_filtered


def test_plot_relationship_network():
    """
    test viz.plot_relationship_network with different parameters (selected_relationship_types, selected_model_ids,
    selected_derivative_ids) and confirm that its output network matches the hardcoded number of nodes and edges
    """
    df = pd.DataFrame.from_dict(data=RELATIONSHIPS_DICT_EXAMPLE)

    # normal relationships (use the rela dict)
    hardcoded_nt = (53, 30)
    nt = viz.plot_relationship_network(df)
    assert len(nt.nodes) == hardcoded_nt[0]
    assert len(nt.edges) == hardcoded_nt[1]

    # rela type filter
    hardcoded_non_mechanical_nt = (34, 19)
    non_mechanical_nt = viz.plot_relationship_network(df, selected_relationship_types=['Non-mechanical transformation'])
    assert len(non_mechanical_nt.nodes) == hardcoded_non_mechanical_nt[0]
    assert len(non_mechanical_nt.edges) == hardcoded_non_mechanical_nt[1]

    # model ids
    hardcoded_selected_model_nt = (7, 4)
    selected_model_nt = viz.plot_relationship_network(df, selected_model_ids=['CRIM_Model_0011'])
    assert len(selected_model_nt.nodes) == hardcoded_selected_model_nt[0]
    assert len(selected_model_nt.edges) == hardcoded_selected_model_nt[1]

    # derivative ids
    hardcoded_selected_derivative_nt = (11, 7)
    selected_derivative_nt = viz.plot_relationship_network(df, selected_derivative_ids=['CRIM_Mass_0009_3',
                                                                                        'CRIM_Mass_0009_5',
                                                                                        'CRIM_Mass_0017_4'])
    assert len(selected_derivative_nt.nodes) == hardcoded_selected_derivative_nt[0]
    assert len(selected_derivative_nt.edges) == hardcoded_selected_derivative_nt[1]

    # families and color according to model
    hardcoded_selected_families_nt = (10, 6)
    selected_families_nt = viz.plot_relationship_network(df, selected_families=['CRIM_Model_0017', 'CRIM_Mass_0009_3',
                                                                                'CRIM_Mass_0009_5', 'CRIM_Mass_0017_4'],
                                                         color="model")
    assert len(selected_families_nt.nodes) == hardcoded_selected_families_nt[0]
    assert len(selected_families_nt.edges) == hardcoded_selected_families_nt[1]
