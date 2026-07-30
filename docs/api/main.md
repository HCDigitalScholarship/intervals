# main

Batch-processing helpers built on top of `ImportedPiece`: exporting match
results to CSV, converting EMA addresses into note-level score excerpts, and
gathering ngram tables across pattern-matching results.

::: crim_intervals.main
    options:
      show_root_heading: false
      members:
        - export_to_csv
        - ema2ex
        - gatherNgrams
