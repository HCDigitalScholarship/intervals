"""
This file contains unit tests for visualizations.
 pytest --cov visualizations test_vis.py --cov-report term-missing
"""

import altair as alt
import pandas as pd
import visualizations as viz

from fractions import Fraction
from main_objs import CorpusBase
from test_constants import EXAMPLE_CRIM_FILE, OBSERVATIONS_DICT_EXAMPLE, RELATIONSHIPS_DICT_EXAMPLE

def ngrams_heatmap_test_helper(model, notes):
    """
    This method tests out three different ways ngrams can be plotted
    without durations: plot all ngrams, filtered some specific patterns,
    filtered some specific voices.

    :param model: model
    :param notes: the main melody
    :return: a chart
    """
    # test no durations
    ngrams = model.getNgrams(df=notes, n=5)
    chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams)

    # retrieved two charts: one pattern bar chart
    # and one heatmap
    assert isinstance(chart, alt.VConcatChart)
    assert len(chart.vconcat) == 2

    # test no durations
    ngrams_multiple = model.getNgrams(df=notes, n=-1)
    chart_multiple = viz.plot_ngrams_heatmap(ngrams_df=ngrams_multiple)

    # retrieved two charts: one pattern bar chart
    # and one heatmap
    assert isinstance(chart_multiple, alt.VConcatChart)
    assert len(chart_multiple.vconcat) == 2

    # popular pattern
    popular_patterns = ngrams.stack().dropna().value_counts().head(10).index.to_list()
    selected_patterns_chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams, selected_patterns=popular_patterns)

    assert isinstance(selected_patterns_chart, alt.VConcatChart)
    assert len(selected_patterns_chart.vconcat) == 2

    # select all voices but the last one
    selected_voices = ngrams.columns.to_list()[:-1]
    selected_voices_chart = viz.plot_ngrams_heatmap(ngrams, voices=selected_voices)
    assert isinstance(selected_voices_chart, alt.VConcatChart)
    assert len(selected_voices_chart.vconcat) == 2

    # with duration!
    ngrams, ngrams_dur = viz.generate_ngrams_and_duration(model, df=notes, n=5)
    dur_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur)
    assert isinstance(dur_chart, alt.VConcatChart)
    assert len(dur_chart.vconcat) == 2

    ngrams_multiple, ngrams_dur_multiple = viz.generate_ngrams_and_duration(model, df=notes, n=5)
    dur_chart_multiple = viz.plot_ngrams_heatmap(ngrams_multiple, ngrams_duration=ngrams_dur_multiple)
    assert isinstance(dur_chart_multiple, alt.VConcatChart)
    assert len(dur_chart_multiple.vconcat) == 2

    # duration and filter voice
    dur_selected_voices_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur,
                                                        voices=selected_voices)
    assert isinstance(dur_selected_voices_chart, alt.VConcatChart)
    assert len(dur_selected_voices_chart.vconcat) == 2

    # duration and filter pattern
    dur_selected_patterns_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur,
                                                          selected_patterns=popular_patterns)
    assert isinstance(dur_selected_patterns_chart, alt.VConcatChart)
    assert len(dur_selected_patterns_chart.vconcat) == 2

    """
    # add when durations can handle n=-1
    # with multiple lengths ngrams
    ngrams_multiple, ngrams_dur_multiple = viz.generate_ngrams_and_duration(model, df=notes, n=-1)
    dur_chart_multiple = viz.plot_ngrams_heatmap(ngrams_multiple, ngrams_duration=ngrams_dur_multiple)
    assert isinstance(dur_chart_multiple, alt.VConcatChart)
    assert len(dur_chart_multiple.vconcat) == 2
    """


def test_plot_ngrams_heatmap():
    corpus = CorpusBase([EXAMPLE_CRIM_FILE])
    model = corpus.scores[0]

    # mel
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    ngrams_heatmap_test_helper(model, mel_notes)
    # diatonic
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    ngrams_heatmap_test_helper(model, mel_diatonic)


def helper_test_close_match_(model, notes):
    ngrams = model.getNgrams(df=notes, n=5)
    popular_patterns = ngrams.stack().dropna().value_counts().head(5).index.to_list()

    for i in range(5):
        chart = viz.plot_close_match_heatmap(ngrams, popular_patterns[i])


def test_plot_close_match_heatmap():
    corpus = CorpusBase([EXAMPLE_CRIM_FILE])
    model = corpus.scores[0]

    # detailed diatonic
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_notes)

    # ngrams in diatonics
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_diatonic)


def helper_test_generate_ngrams_and_dur(model, notes, n):
    # throw things into get ngrams and duration
    ngrams, ngrams_dur = viz.generate_ngrams_and_duration(model, df=notes, n=n)

    for row in ngrams.index:
        for col in ngrams.columns:
            # get the ngram and total duration
            ngram = ngrams.loc[row, col]
            if pd.isnull(ngram):
                continue
            ngram = ngram.split(', ')
            dur = ngrams_dur.loc[row, col]
            # check if those within the duration range match the ngrams notes
            ngram_notes = notes.loc[row:Fraction(row + dur), col].dropna().to_list()

            # check all of the notes in the notes dataframe against the ngrams
            assert len(ngram_notes) == len(ngram) or len(ngram_notes) - 1 == len(ngram)
            for i in range(len(ngram)):
                assert (ngram_notes[i] == ngram[i])


def test_generate_ngrams_and_dur():
    corpus = CorpusBase([EXAMPLE_CRIM_FILE])
    model = corpus.scores[0]

    # all of the n=-1 test would be added again when generate_ngrams_and_duration
    # works for this case

    # mel
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    helper_test_generate_ngrams_and_dur(model, mel_notes, 5)
    # helper_test_generate_ngrams_and_dur(model, mel_notes, -1)

    # diatonic
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    helper_test_generate_ngrams_and_dur(model, mel_diatonic, 5)
    # helper_test_generate_ngrams_and_dur(model, mel_diatonic, -1)

    # chromatic
    mel_chromatic = model.getMelodic(kind='c', directed=True, compound=True, unit=0)
    helper_test_generate_ngrams_and_dur(model, mel_chromatic, 5)
    # helper_test_generate_ngrams_and_dur(model, mel_chromatic, -1)


def test_comparisons_heatmap():
    # pieces
    df_relationships = pd.DataFrame(RELATIONSHIPS_DICT_EXAMPLE)
    relationships_chart = viz.plot_comparison_heatmap(df_relationships, 'model_observation.ema',
                                                      main_category='relationship_type', other_category='observer.name',
                                                      heat_map_width=800, heat_map_height=300)
    assert isinstance(relationships_chart, alt.VConcatChart)
    assert len(relationships_chart.vconcat) == 2

    df_observations = pd.DataFrame(OBSERVATIONS_DICT_EXAMPLE)
    observations_chart = viz.plot_comparison_heatmap(df_observations, 'ema',
                                                     main_category='musical_type', other_category='observer.name',
                                                     heat_map_width=800, heat_map_height=300)
    assert isinstance(observations_chart, alt.VConcatChart)
    assert len(observations_chart.vconcat) == 2


def test_generate_networks_and_interactive_df():
    df_observations = pd.DataFrame(OBSERVATIONS_DICT_EXAMPLE)

    # time, pe
    pen_networks, pen_widget = viz.create_comparisons_networks_and_interactive_df(df_observations, 'mt_pe_tint', 'time',
                                                                                  'ema')
    assert pen_networks
    assert pen_widget

    # melodic, fug
    fug_networks, fug_widget = viz.create_comparisons_networks_and_interactive_df(df_observations, 'mt_fg_int',
                                                                                  'melodic',
                                                                                  'ema')
    assert fug_networks
    assert fug_widget

    patterns = df_observations['mt_fg_int'].to_list()
    fug_networks_filtered, fug_widget_filtered = viz.create_comparisons_networks_and_interactive_df(df_observations,
                                                                                                    'mt_fg_int',
                                                                                                    'melodic', 'ema',
                                                                                                    patterns)

    assert fug_networks_filtered
    assert fug_widget_filtered
