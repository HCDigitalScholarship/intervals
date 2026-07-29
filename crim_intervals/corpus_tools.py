# these tools work with existing Crim Intervals classes and functions.

# each takes in a corpus object, along with various arguments

# typical usage:

#
# import crim_intervals.corpus_tools as corpus_tools
# corpus_tools.corpus_notes(corpus, combine_unisons_choice=True, combine_rests_choice=False)

# NB: the logic for all of these now lives on the CorpusBase class in main_objs.py
# (e.g. `corpus.notes(...)`); the functions below are thin backward-compatible
# wrappers kept so that existing notebooks that import corpus_tools directly
# keep working unchanged.

from crim_intervals import ImportedPiece
import pandas as pd
from collections import Counter
from .sorting_lists import (
    pitch_class_order_no_rests,
    pitch_class_order_with_rests,
    pitch_order,
    sort_pitch_values,
    standardize_note,
    extract_letter,
)


def corpus_notes(corpus, combine_unisons_choice=True, combine_rests_choice=False, key_sig=False):
    """Creates table of notes and rests in a corpus. See CorpusBase.notes."""
    return corpus.notes(combine_unisons_choice=combine_unisons_choice, combine_rests_choice=combine_rests_choice,
                         key_sig=key_sig)


def corpus_note_scaled(corpus, combine_unisons_choice=True, combine_rests_choice=False, key_sig=False):
    """Count occurrences of notes and rests in a corpus. See CorpusBase.note_scaled."""
    return corpus.note_scaled(combine_unisons_choice=combine_unisons_choice, combine_rests_choice=combine_rests_choice,
                               key_sig=key_sig)


def corpus_note_durs(corpus, pitch_class=True):
    """Calculate durations of notes in a corpus. See CorpusBase.note_durs."""
    return corpus.note_durs(pitch_class=pitch_class)


def corpus_note_weights(corpus, include_rests=True, key_sig=False):
    """Calculate pitch class weights by duration in a corpus. See CorpusBase.note_weights."""
    return corpus.note_weights(include_rests=include_rests, key_sig=key_sig)


def corpus_mel(corpus, kind_choice='d', compound_choice=True, directed_choice=True):
    """Generate melodic intervals in a corpus. See CorpusBase.mel."""
    return corpus.mel(kind_choice=kind_choice, compound_choice=compound_choice, directed_choice=directed_choice)


def corpus_har(corpus, kind_choice='d', compound_choice=True, directed_choice=True):
    """Generate harmonic intervals in a corpus. See CorpusBase.har."""
    return corpus.har(kind_choice=kind_choice, compound_choice=compound_choice, directed_choice=directed_choice)


def corpus_contrapuntal_ngrams(corpus, ngram_length=3):
    """Generate contrapuntal n-grams in a corpus. See CorpusBase.contrapuntal_ngrams."""
    return corpus.contrapuntal_ngrams(ngram_length=ngram_length)


def corpus_melodic_ngrams(corpus,
                          ngram_length=4,
                          kind_choice='d',
                          compound_choice=True,
                          directed_choice=True,
                          end_choice=False,
                          metadata_choice=True,
                          include_offset=False):
    """Generate melodic n-grams in a corpus. See CorpusBase.melodic_ngrams."""
    return corpus.melodic_ngrams(ngram_length=ngram_length, kind_choice=kind_choice,
                                  compound_choice=compound_choice, directed_choice=directed_choice,
                                  end_choice=end_choice, metadata_choice=metadata_choice,
                                  include_offset=include_offset)


def corpus_melodic_durational_ratios_ngrams(corpus, ngram_length=4,
                                            end_choice=False,
                                            kind_choice='d',
                                            compound_choice=True,
                                            directed_choice=True,
                                            metadata_choice=True,
                                            include_offset=False):
    """Generate melodic n-grams with durational ratios in a corpus. See CorpusBase.melodic_durational_ratios_ngrams."""
    return corpus.melodic_durational_ratios_ngrams(ngram_length=ngram_length, end_choice=end_choice,
                                                     kind_choice=kind_choice, compound_choice=compound_choice,
                                                     directed_choice=directed_choice, metadata_choice=metadata_choice,
                                                     include_offset=include_offset)


def corpus_harmonic_ngrams(corpus,
                           ngram_length=4,
                           kind_choice='d',
                           compound_choice=True,
                           directed_choice=True,
                           metadata_choice=True,
                           againstLow_choice=False,
                           include_offset=False):
    """Generate harmonic n-grams in a corpus. See CorpusBase.harmonic_ngrams."""
    return corpus.harmonic_ngrams(ngram_length=ngram_length, kind_choice=kind_choice,
                                   compound_choice=compound_choice, directed_choice=directed_choice,
                                   metadata_choice=metadata_choice, againstLow_choice=againstLow_choice,
                                   include_offset=include_offset)


def corpus_sonority_ngrams(corpus,
                           ngram_length=4,
                           metadata_choice=True,
                           include_offset=False,
                           include_progress=True,
                           compound=True,
                           sort=False,
                           minimum_beat_strength=0.0):
    """Generate sonority n-grams (plus bassline) in a corpus. See CorpusBase.sonority_ngrams."""
    return corpus.sonority_ngrams(ngram_length=ngram_length, metadata_choice=metadata_choice,
                                   include_offset=include_offset, include_progress=include_progress,
                                   compound=compound, sort=sort, minimum_beat_strength=minimum_beat_strength)


def corpus_cadences(corpus):
    """Return cadences for all pieces in the corpus. See CorpusBase.cadences."""
    return corpus.cadences()


def corpus_presentation_types(corpus,
                              limit_to_entries=True,
                              head_flex=1,
                              body_flex=0,
                              include_hidden_types=False,
                              combine_unisons=True,
                              melodic_ngram_length=4,
                              kind='d',
                              end=False):
    """Return presentation types for all pieces in the corpus. See CorpusBase.presentation_types."""
    return corpus.presentation_types(limit_to_entries=limit_to_entries, head_flex=head_flex, body_flex=body_flex,
                                      include_hidden_types=include_hidden_types, combine_unisons=combine_unisons,
                                      melodic_ngram_length=melodic_ngram_length, kind=kind, end=end)


def find_mode_range(df, top_n=7):
    """
    Finds the range of notes in a given voice, and thus helps us distinguish modal types.
    df:  corpus notes, with pitch classes, such as `corpus_note_durs(corpus, pitch_class=False)`
    the df will then be processed to include percentages for each pitch class in each voice in each piece

    final_value:  the final tone of each piece (which is key to determining the mode!)
    voice_value:  which voice you want to check
    top_n: the n highest percentage scoring notes (which are most likely to represent the core range of the voice
    """
    # no rests
    filtered_df = df[(df['Notes'] != 'Rest')]

    # Find top N durations for each Title
    top_durations = filtered_df.groupby(['CompTitle', 'Voice']).apply(
        lambda x: x.nlargest(top_n, 'Percentage')).reset_index(drop=True)

    # Position lookup based on the shared, octave-aware pitch_order (sorting_lists.py)
    pitch_position = {p: i for i, p in enumerate(pitch_order)}

    def get_note_position(note):
        note = str(note)
        if note in pitch_position:
            return pitch_position[note]
        # Alternative flat notation, e.g. "Bb4" instead of "B-4"
        alt = note.replace('b', '-')
        if alt in pitch_position:
            return pitch_position[alt]
        # If we can't determine the position, return a very low value
        print(f"Warning: Could not determine position for note: {note}")
        return -1000

    # Apply the position mapping
    top_durations['NotePosition'] = top_durations['Notes'].apply(get_note_position)

    # Find lowest and highest notes
    result = []
    for comptitle, group in top_durations.groupby(['CompTitle', 'Voice']):
        if len(group) > 0:
            sorted_group = group.sort_values('NotePosition')
            lowest_note = sorted_group.iloc[0]['Notes']
            highest_note = sorted_group.iloc[-1]['Notes']
            voice = sorted_group.iloc[0]['Voice']
            title = sorted_group.iloc[0]['Title']
            composer = sorted_group.iloc[0]['Composer']
            comptitle = comptitle
            final = sorted_group.iloc[0]['Final']
            result.append({
                'Composer': composer,
                'Title': title,
                'CompTitle': comptitle[0],
                'Voice': voice,
                'Final': final,
                'LowestNote': lowest_note,
                'HighestNote': highest_note,
                'Range': f"{lowest_note} to {highest_note}"
            })

    return pd.DataFrame(result)
