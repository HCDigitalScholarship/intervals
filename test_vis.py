"""
This file contains unit tests for visualizations.
"""
from main_objs import CorpusBase

import altair as alt
import visualizations as viz

def ngrams_heatmap_test_helper(model, notes):
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

    mel_notes_str = mel_notes.applymap(str, na_action='ignore')
    helper_test_close_match_(model, mel_notes_str)

    # ngrams in diatonics
    mel_diatonic = model.getMelodic(kind='d', directed=True, compound=True, unit=0)
    helper_test_close_match_(model, mel_diatonic)

    mel_diatonic_str = mel_diatonic.applymap(str, na_action='ignore')
    helper_test_close_match_(model, mel_diatonic_str)

# test_plot_ngrams_heatmap()
# test_plot_close_match_heatmap()