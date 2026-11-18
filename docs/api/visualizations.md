# visualizations

Charting and network-visualization helpers (Altair, Plotly, pyvis) built on
top of ngram, cadence, and presentation-type results from `main_objs.py`.

The ready-made chart functions (`cadence_radar` through `plot_species_cadences`)
each take the result of a single piece or a whole corpus: run the method on
`piece` or `corpus`, then pass the result to the chart function, for example
`cadence_radar(corpus.cadences())`. Each returns a Plotly figure. See the
[Visualizations tutorial](https://github.com/HCDigitalScholarship/intervals/blob/main/tutorial/17_Visualizations_Summary.md)
for worked examples.

::: crim_intervals.visualizations
    options:
      show_root_heading: false
      members:
        - NgramColorManager
        - ColorManager
        - PatternStyleManager
        - create_bar_chart
        - create_heatmap
        - process_ngrams_df
        - generate_distinct_colors
        - ngrams_color_helper
        - plot_ngrams_heatmap
        - plot_ngrams_barchart
        - pre_register_patterns
        - plot_comparison_heatmap
        - plot_close_match_heatmap
        - generate_ngrams_and_duration
        - process_network_df
        - create_interval_networks
        - cadence_radar
        - cadence_progress
        - cadence_bar_chart
        - radar_note_plot
        - voice_range_chart
        - plot_species
        - plot_species_cadences
