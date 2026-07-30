# visualizations

Charting and network-visualization helpers (Altair, Plotly, pyvis) built on
top of ngram, cadence, and presentation-type results from `main_objs.py`.

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
