# variable orders.  These include the full chromatic range of possibilities

import re
import numpy as np
import pandas as pd

# pitch order for sorting, including all chromatic alterations and octaves 2-6, but no double shartps or flats
pitch_order = ['Rest','C2', 'D2', 'E-2', 'E2', 'F2', 'F#2', 'G-2', 'G2', 'G#2', 'A-2', 'A2', 'A#2','B-2', 'B2',
    'C3', 'C#3', 'D-3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3', 'G-3',  'G3', 'G#3', 'A-3', 'A3', 'A#3', 'B-3','B3', 'B#3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4', 'A#4', 'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5', 'A#5', 'B-5', 'B5',
    'C6']

# musica recta pitch order for sorting, including only the pitches used in musica recta
recta_order = ['Rest','D2', 'E-2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'B-2', 'B2',
    'C3', 'C#3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3',  'G3', 'G#3', 'A-3', 'A3', 'B-3','B3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4',  'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5',  'B-5', 'B5',
    'C6']

# only pitch classes, no octaves, no double sharps or flats, plus 'Rest'
pitch_class_order = ['C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F-', 'E#', 'F', 'F#', 'G-', 'F##', 'G', 'G#',
    'A-', 'A', 'A#', 'B-', 'B', 'B#', 'Rest']

pitch_class_order_no_rests = [item for item in pitch_class_order if item != 'Rest']

pitch_class_order_with_rests = pitch_class_order.copy()

# custom interval order for mel and har charts

interval_order_quality = ["-P8", "-M7", "-m7", "-M6", "-m6", "-P5", "-P4", "-M3", 
                          "-m3", "-M2", "-m2", "P1", "m2", "M2", "m3", "M3",
                          "P4", "P5", "m6", "M6", "m7", "M7", "P8"]

# Mass movements in liturgical order, for sorting titles (titles without a
# movement name, such as models, sort first)
_MASS_MOVEMENTS = ['Kyrie', 'Gloria', 'Credo', 'Sanctus', 'Agnus Dei']

# modally significant reference pitches for each final, used as guide lines
# in voice range charts (see visualizations.voice_range_chart)
_RANGE_REFERENCE_BY_FINAL = {
    'D': ['D3', 'G3', 'D4', 'G4', 'D5', 'G5'],
    'E': ['E3', 'C3', 'E4', 'C4', 'E5', 'C5'],
    'F': ['C3', 'F3', 'C4', 'F4', 'C5', 'F5'],
    'G': ['D3', 'G3', 'D4', 'G4', 'D5', 'G5'],
    'A': ['E3', 'A3', 'E4', 'A4', 'E5', 'A5'],
    'C': ['C3', 'G3', 'C4', 'G4', 'C5', 'G5'],
}

# dictionaries to map tone+intervals strings to relevant pair of tones
# used by Species functions

species_four_five_dict = {
    'C_5':'C/G', 'C_-5':'C/F', 'C_4':'C/F', 'C_-4':'C/G',
    'D_5':'D/A', 'D_-5':'D/G', 'D_4':'D/G', 'D_-4':'D/A',
    'E_5':'E/B', 'E_-5':'E/A', 'E_4':'E/A', 'E_-4':'E/B',
    'F_5':'F/C', 'F_-5':'F/B-', 'F_4':'F/B-', 'F_-4':'F/C',
    'G_5':'G/D', 'G_-5':'G/C', 'G_4':'G/C', 'G_-4':'G/D',
    'A_5':'A/E', 'A_-5':'A/D', 'A_4':'A/D', 'A_-4':'A/E',
    'B_5':'B/F#', 'B_-5':'B/E', 'B_4':'B/E', 'B_-4':'B/F#',
    'B-_5':'B-/F', 'B-_-5':'B-/E-', 'B-_4':'B-/E-', 'B-_-4':'B-/F',
}

# dictionary to map leaps to relevant octave types
species_octave_dict = {
    'C/G':'CGC', 'C/F':'FCF', 'D/A':'DAD', 'D/G':'GDG',
    'E/B':'EBE', 'E/A':'AEA', 'F/C':'FCF', 'F/B-':'BbFBb',
    'G/D':'GDG', 'G/C':'CGC', 'A/E':'AEA', 'A/D':'DAD',
    'B/F#':'BF#B', 'B/E':'EBE', 'B-/F':'BbFBb', 'B-/E-':'EbBbEb'
}

# intervals to catch as species
species_intervals_list = ['5', '-5', '4', '-4']


# octave order for species PLOT
species_octave_order = ['EbBbEb', 'BbFBb', 'FCF', 'CGC', 'GDG', 'DAD', 'AEA', 'EBE', 'BF#B']


# cadence tone orders for visualizations.cadence_radar (music21 spelling).
# Tones found in the data but missing from the chosen list are added at the end.
cadence_tone_orders = {
    'Diatonic':  ['C', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A', 'B-', 'B', 'C#', 'G#', 'A-', 'D-'],
    'Fifths':    ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'A-', 'E-', 'B-', 'F'],
    'Thirds':    ['C', 'E', 'G', 'B-', 'D', 'F', 'A', 'C#', 'E-', 'B', 'F#'],
    'Chromatic': ['C', 'C#', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G-', 'G', 'G#', 'A-', 'A', 'B-', 'B'],
}

# pitch-class orders for visualizations.radar_note_plot (music21 spelling).
# Pitch classes found in the data but missing from the chosen list are added at the end.
note_pitch_class_orders = {
    'Chromatic': ['C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F-', 'E#', 'F', 'F#', 'G-', 'F##',
                  'G', 'G#', 'A-', 'A', 'A#', 'B-', 'B', 'B#'],
    'Fifths':    ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'E#', 'B#', 'F##',
                  'D-', 'A-', 'E-', 'B-', 'F', 'G-', 'F-'],
    'Diatonic':  ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'B-', 'E-', 'A-', 'D-', 'C#', 'F#', 'G#',
                  'D#', 'A#', 'G-', 'F-', 'E#', 'F##', 'B#'],
}

# cadence tones from bottom to top on the y axis of cadence_progress and
# plot_species_cadences (a circle of fifths, flats at the bottom)
cadence_progress_tone_order = ['E-', 'B-', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#']

# cadence types in legend order, and their colors: evaded types are lighter
# and abandoned types lighter still than the corresponding realized type
cadence_type_order = ['Authentic', 'Evaded Authentic', 'Abandoned Authentic',
    'Clausula Vera', 'Evaded Clausula Vera', 'Abandoned Clausula Vera',
    'Phrygian Clausula Vera', 'Evaded Phrygian Clausula Vera', 'Abandoned Phrygian Clausula Vera',
    'Double Leading Tone', 'Evaded Double Leading Tone', 'Abandoned Double Leading Tone',
    'Altizans Only', 'Evaded Altizans Only', 'Phrygian Altizans',
    'Phrygian', 'Evaded Phrygian', 'Abandoned Phrygian',
    'Reinterpreted', 'Evaded Reinterpreted', 'Quince', 'Evaded Quince', 'Leaping Contratenor']

# One color per cadence family, from the same Paul Tol palette as
# visualizations.contrasting_colors, so cadence charts match the others.
_cadence_family_colors = {
    'Authentic': '#4477AA',               # blue
    'Clausula Vera': '#CC6677',           # rose
    'Phrygian Clausula Vera': '#AA3377',  # purple
    'Double Leading Tone': '#228833',     # green
    'Altizans Only': '#EE6633',           # orange
    'Phrygian Altizans': '#DDAA33',       # ochre (a deeper Tol sand, readable on white)
    'Phrygian': '#332288',                # indigo
    'Reinterpreted': '#44AA99',           # teal
    'Quince': '#8C510A',                  # brown
    'Leaping Contratenor': '#555555',     # charcoal
}


def _tint(hex_color, amount):
    """Mix a '#RRGGBB' color with white; amount 0 = unchanged, 1 = white."""
    rgb = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(c + (255 - c) * amount):02X}' for c in rgb)


cadence_type_colors = {}
for _family, _color in _cadence_family_colors.items():
    cadence_type_colors[_family] = _color
    cadence_type_colors['Evaded ' + _family] = _tint(_color, 0.4)
    cadence_type_colors['Abandoned ' + _family] = _tint(_color, 0.65)


# REST tokens as seen in CRIM Intervals output
REST_TOKENS = {'r', 'rest', 'Rest', '-', ''}

# Function to standardize note names
def standardize_note(note):
    if pd.isna(note):
        return note
    if '-' in str(note):
        return str(note).replace('-', 'b')
    return str(note)

# this is used by final() and note_durs()
def extract_letter(value, include_rests=True):
    """Extract pitch class from a note string.

    Returns 'Rest' for rest tokens (if include_rests=True),
    None for rest tokens (if include_rests=False),
    or the pitch class letter+accidental for pitched notes.
    """
    if pd.isna(value):
        return None
    s = str(value).strip()
    if s.lower() in REST_TOKENS:
        return 'Rest' if include_rests else None
    # Strip octave digit(s) from end to get pitch class
    return s.rstrip('0123456789')

#
def tuple_to_list(value, separator=None, cast=None):
    """Convert tuple-like values to a Python list.

    `cast`, if given, is applied to each element (e.g. `cast=int` to parse a
    string of the form "1, -2, 1, -2" into `[1, -2, 1, -2]`).
    """
    if value is None:
        return []
    if isinstance(value, pd.Series):
        value = value.tolist()
    if isinstance(value, (list, tuple, set)):
        result = [item for item in value]
    elif isinstance(value, str):
        if separator is None:
            stripped = value.strip()
            if stripped.startswith('(') and stripped.endswith(')'):
                stripped = stripped[1:-1]
            if not stripped:
                return []
            result = [item.strip() for item in stripped.split(',') if item.strip()]
        else:
            result = [item.strip() for item in value.split(separator) if item.strip()]
    else:
        result = [value]
    if cast is not None:
        result = [cast(item) for item in result]
    return result


def tuple_to_string(value, separator=', '):
    """Convert tuple-like values to a delimited string."""
    if value is None:
        return ''
    if isinstance(value, pd.Series):
        value = value.tolist()
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set)):
        return separator.join(str(item) for item in value)
    return str(value)


def sort_pitch_values(values, order=None, include_rests=True):
    """
    Return a list of pitch values sorted according to a supplied order.

    Parameters
    ----------
    values : list, tuple, set, pandas.Series, or scalar
        The pitch values to sort.
    order : list, optional
        The reference ordering to sort `values` against. Defaults to
        `pitch_order` if not passed. Available options defined in this
        module:

        - `pitch_order` (default): full chromatic gamut across octaves 2-6,
          e.g. 'C2', 'C#2', 'D-2', ... 'C6'.
        - `recta_order`: the same range restricted to musica recta pitches,
          omitting a handful of chromatic alterations found in `pitch_order`
          (e.g. 'C2', 'G-2', 'A#2').
        - `pitch_class_order`: pitch classes without octave, plus 'Rest',
          e.g. 'C', 'C#', 'D-', ... 'B#', 'Rest'.
        - `pitch_class_order_no_rests`: `pitch_class_order` with 'Rest'
          removed.
        - `pitch_class_order_with_rests`: alias for `pitch_class_order`,
          kept for symmetry with `pitch_class_order_no_rests`.
    include_rests : bool, optional (default True)
        Whether rest tokens ('Rest', 'r', '-', etc.) sort in place (True) or
        are pushed after all pitched values (False).

    Returns
    -------
    list
        `values` sorted according to `order`, with NaNs dropped.
    """
    if values is None:
        return []
    if isinstance(values, (pd.Series, pd.Index, np.ndarray)):
        values = list(values)
    elif isinstance(values, str):
        values = [values]
    elif not isinstance(values, (list, tuple, set)):
        values = [values]

    if order is None:
        order = pitch_order
    order_lookup = {item: index for index, item in enumerate(order)}

    def _sort_key(value):
        if pd.isna(value):
            return (1, len(order_lookup), '')
        text = str(value).strip()
        if not text:
            return (1, len(order_lookup), '')
        if text.lower() in {'r', 'rest', '-', ''}:
            if include_rests:
                return (0, order_lookup.get('Rest', len(order_lookup)), 'Rest')
            return (1, len(order_lookup), 'Rest')
        if text in order_lookup:
            return (0, order_lookup[text], text)
        if text.replace('-', 'b') in order_lookup:
            return (0, order_lookup[text.replace('-', 'b')], text)
        return (1, len(order_lookup), text)

    return [value for value in sorted(values, key=_sort_key) if not pd.isna(value)]


_INTERVAL_QUALITY_RANK = {'d': 0, 'm': 1, 'P': 2, 'M': 3, 'A': 4}


def interval_sort_key(label):
    """
    Sort key for interval labels, from the largest descending interval through
    the unison to the largest ascending one (e.g. '-P8', ..., '-m2', 'P1',
    'm2', ..., 'M10').

    Works for diatonic ('-2', '3') and quality ('-m3', 'P5', 'd5', 'A4')
    labels, simple or compound.  Within one size, smaller qualities come first
    when ascending (m3 before M3) and last when descending (-M3 before -m3),
    matching `interval_order_quality`.  Rests and unrecognized labels sort
    after all intervals.
    """
    match = re.fullmatch(r'(-?)([A-Za-z]*)(\d+)', str(label).strip())
    if not match:
        return (1, 0, 0, str(label))
    sign, quality, size = match.groups()
    size = int(size)
    rank = _INTERVAL_QUALITY_RANK.get(quality[:1], 2)
    if sign:
        return (0, -size, -rank, '')
    return (0, size, rank, '')


def sort_interval_values(values, include_rests=False):
    """
    Return the distinct interval labels in `values`, ordered with
    `interval_sort_key` (largest descending ... unison ... largest ascending).

    Parameters
    ----------
    values : list, tuple, set, pandas.Series, or scalar
        Interval labels, e.g. from `piece.melodic()` or `piece.harmonic()`.
    include_rests : bool, optional (default False)
        Keep 'Rest' (placed after all intervals) or drop it.

    Returns
    -------
    list
        Unique labels in sorted order, with NaNs and empty placeholders
        ('' or '-', as left by `fillna('-')`) dropped.
    """
    if values is None:
        return []
    if isinstance(values, (pd.Series, pd.Index, np.ndarray)):
        values = list(values)
    elif isinstance(values, str) or not isinstance(values, (list, tuple, set)):
        values = [values]
    unique = []
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text in {'', '-'}:      # fillna placeholders, not intervals
            continue
        if text.lower() in {'r', 'rest'} and not include_rests:
            continue
        if text not in unique:
            unique.append(text)
    return sorted(unique, key=interval_sort_key)
