# corpus_tools (deprecated)

`corpus_tools` predates the `CorpusBase` class. It is kept only so that
existing notebooks which import it directly keep working; new code should
call the equivalent `CorpusBase` method on a corpus object directly (e.g.
`corpus.notes(...)`) instead of importing this module.

| Function | Docstring reference |
|---|---|
| `corpus_notes` | See `CorpusBase.notes` |
| `corpus_note_scaled` | See `CorpusBase.note_scaled` |
| `corpus_note_durs` | See `CorpusBase.note_durs` |
| `corpus_note_weights` | See `CorpusBase.note_weights` |
| `corpus_mel` | See `CorpusBase.mel` |
| `corpus_har` | See `CorpusBase.har` |
| `corpus_contrapuntal_ngrams` | See `CorpusBase.contrapuntal_ngrams` |
| `corpus_melodic_ngrams` | See `CorpusBase.melodic_ngrams` |
| `corpus_melodic_durational_ratios_ngrams` | See `CorpusBase.melodic_durational_ratios_ngrams` |
| `corpus_harmonic_ngrams` | See `CorpusBase.harmonic_ngrams` |
| `corpus_sonority_ngrams` | See `CorpusBase.sonority_ngrams` |
| `corpus_cadences` | See `CorpusBase.cadences` |
| `corpus_presentation_types` | See `CorpusBase.presentation_types` |
| `find_mode_range` | Finds the range of notes in a given voice, to help distinguish modal types |

See [main_objs.py](main_objs.md) for the current, maintained API.
