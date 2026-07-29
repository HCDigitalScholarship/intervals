# variable orders.  These include the full chromatic range of possibilities

import pandas as pd

pitch_order = ['Rest','C2', 'D2', 'E-2', 'E2', 'F2', 'F#2', 'G-2', 'G2', 'G#2', 'A-2', 'A2', 'A#2','B-2', 'B2',
    'C3', 'C#3', 'D-3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3', 'G-3',  'G3', 'G#3', 'A-3', 'A3', 'A#3', 'B-3','B3', 'B#3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4', 'A#4', 'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5', 'A#5', 'B-5', 'B5',
    'C6']

recta_order = ['Rest','D2', 'E-2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'B-2', 'B2',
    'C3', 'C#3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3',  'G3', 'G#3', 'A-3', 'A3', 'B-3','B3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4',  'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5',  'B-5', 'B5',
    'C6']


pitch_class_order = ['C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F-', 'E#', 'F', 'F#', 'G-', 'F##', 'G', 'G#',
    'A-', 'A', 'A#', 'B-', 'B', 'B#', 'Rest']
pitch_class_order_no_rests = [item for item in pitch_class_order if item != 'Rest']
pitch_class_order_with_rests = pitch_class_order.copy()

# REST tokens as seen in CRIM Intervals output
REST_TOKENS = {'r', 'rest', 'Rest', '-', ''}

# Function to standardize note names
def standardize_note(note):
    if pd.isna(note):
        return note
    if '-' in str(note):
        return str(note).replace('-', 'b')
    return str(note)


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
    """Return a list of pitch values sorted according to a supplied order."""
    if values is None:
        return []
    if isinstance(values, pd.Series):
        values = values.tolist()
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
