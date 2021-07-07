"""
This file contains unit tests for visualizations.
"""
from main_objs import CorpusBase

import altair as alt
import pandas as pd
import visualizations as viz

from fractions import Fraction

def ngrams_heatmap_test_helper(model, notes):
    """
    This method tests out three different ways ngrams can be plotted
    without durations: plot all ngrams, filtered some specific patterns,
    filtered some specific voices.

    :param model:
    :param notes:
    :return:
    """
    # test no durations
    ngrams = model.getNgrams(df=notes, n=5)
    chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams)

    # retrieved two charts: one pattern bar chart
    # and one heatmap
    assert isinstance(chart, alt.VConcatChart)
    assert len(chart.vconcat) == 2

    # popular pattern
    popular_patterns = ngrams.stack().dropna().value_counts().head(10).index.to_list()
    selected_patterns_chart = viz.plot_ngrams_heatmap(ngrams_df=ngrams, selected_patterns=popular_patterns)

    assert isinstance(selected_patterns_chart, alt.VConcatChart)
    assert len(selected_patterns_chart.vconcat) == 2

    # select all voices but the last one
    selected_voices = ngrams.columns.to_list()[:-1]
    selected_voices_chart = viz.plot_ngrams_heatmap(ngrams, voices = selected_voices)
    assert isinstance(selected_voices_chart, alt.VConcatChart)
    assert len(selected_voices_chart.vconcat) == 2

    # with duration!
    ngrams, ngrams_dur = viz.generate_ngrams_and_dur(model, df=notes, n=5)
    dur_chart = viz.plot_ngrams_heatmap(ngrams, ngrams_duration=ngrams_dur)
    assert isinstance(dur_chart, alt.VConcatChart)
    assert len(dur_chart.vconcat) == 2

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

def test_plot_ngrams_heatmap():
    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0017.mei'])
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
    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0017.mei'])
    model = corpus.scores[0]

    # detailed diatonic
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_notes)

    # ngrams in diatonics
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_diatonic)

def helper_test_generate_ngrams_and_dur(model, notes):

    # throw things into get ngrams and duration
    ngrams, ngrams_dur = viz.generate_ngrams_and_dur(model, df=notes, n=5)

    for row in ngrams.index:
        for col in ngrams.columns:
            # get the ngram and total duration
            ngram = ngrams.loc[row, col]
            if pd.isnull(ngram):
                continue
            ngram = ngram.split(', ')
            dur = ngrams_dur.loc[row, col]
            # check if those within the duration range match the ngrams notes
            ngram_notes = notes.loc[row:Fraction(row+dur), col].dropna().to_list()

            # check all of the notes in the notes dataframe against the ngrams
            assert len(ngram_notes) == 5 or len(ngram_notes) == 6
            for i in range(len(ngram)):
                assert(ngram_notes[i] == ngram[i])

def test_generate_ngrams_and_dur():
    corpus = CorpusBase(['https://crimproject.org/mei/CRIM_Model_0017.mei'])
    model = corpus.scores[0]

    # mel
    mel_notes = model.getMelodic(kind='q', directed=True, compound=True, unit=0)
    helper_test_generate_ngrams_and_dur(model, mel_notes)

    # diatonic
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    helper_test_generate_ngrams_and_dur(model, mel_diatonic)



# test_plot_ngrams_heatmap()
# test_plot_close_match_heatmap()
# test_generate_ngrams_and_dur()
