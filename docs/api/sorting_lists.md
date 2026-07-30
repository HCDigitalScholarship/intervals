# sorting_lists

Utilities for standardizing, extracting, and ordering pitch and interval
strings. These are used internally throughout `main_objs.py` to keep note
names and ngram tuples in a consistent, sortable form.

`sort_pitch_values` sorts against a reference ordering passed as its `order`
parameter. The module defines these options:

- `pitch_order` (default): full chromatic gamut across octaves 2-6,
  e.g. 'C2', 'C#2', 'D-2', ... 'C6'.
- `recta_order`: the same range restricted to musica recta pitches, omitting
  a handful of chromatic alterations found in `pitch_order` (e.g. 'C2',
  'G-2', 'A#2').
- `pitch_class_order`: pitch classes without octave, plus 'Rest',
  e.g. 'C', 'C#', 'D-', ... 'B#', 'Rest'.
- `pitch_class_order_no_rests`: `pitch_class_order` with 'Rest' removed.
- `pitch_class_order_with_rests`: alias for `pitch_class_order`, kept for
  symmetry with `pitch_class_order_no_rests`.

::: crim_intervals.sorting_lists
    options:
      show_root_heading: false
      members:
        - standardize_note
        - extract_letter
        - tuple_to_list
        - tuple_to_string
        - sort_pitch_values
