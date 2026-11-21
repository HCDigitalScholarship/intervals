"""
This script contains the method
"""

import altair as alt
import pandas as pd
import re
import warnings
import textdistance
import numpy as np 
from crim_intervals import ImportedPiece
import pandas as pd
import plotly.express as px

# from ipywidgets import interact, fixed
# remember to [skip ci] when you change this file to avoid running the tests for the whole package since this file is only for visualizations and doesn't have any logic that needs testing.
from pyvis.network import Network

import matplotlib as mplt # OY addition 6/12/24
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from music21 import pitch as m21_pitch
from .sorting_lists import (_MASS_MOVEMENTS, _RANGE_REFERENCE_BY_FINAL,
                            cadence_tone_orders, cadence_progress_tone_order,
                            cadence_type_order, cadence_type_colors,
                            species_octave_order, note_pitch_class_orders)

# Shared 20-color qualitative palette for all categorical plots (voices,
# patterns, species, etc.).  The first 12 are Paul Tol's qualitative palette
# (https://personal.sron.nl/~pault/), so ngram charts keep their existing
# colors.  The last 8 were chosen to be clearly distinct from the Tol set
# and readable on a white background (min. CIELAB distance ~24 to any other
# color here).
contrasting_colors = [
    # Paul Tol 12
    '#4477AA',  # blue
    '#CC6677',  # rose
    '#228833',  # green
    '#DDCC77',  # sand
    '#AA3377',  # purple
    '#66CCEE',  # cyan
    '#EE6633',  # orange
    '#BBBBBB',  # grey
    '#117733',  # forest
    '#332288',  # indigo
    '#882255',  # wine
    '#44AA99',  # teal
    # 8 additions
    '#C1272D',  # red
    '#F2B701',  # gold
    '#8C510A',  # brown
    '#8DB600',  # lime
    '#E7298A',  # magenta
    '#B39DDB',  # lavender
    '#555555',  # charcoal
    '#6B6B00',  # olive
]

class NgramColorManager:
    """
    Generates visually distinct color palettes for ngram/pattern charts.

    Uses a curated 12-color qualitative palette (Paul Tol's) for up to 12
    colors, then extends with golden-ratio HSV sampling for any additional
    colors needed.
    """
    # Paul Tol's qualitative palette: the first 12 entries of the shared
    # `contrasting_colors` palette above.
    CURATED_12 = contrasting_colors[:12]

    def generate_distinct_colors(self, n):
        """Return n distinct colors.

        Uses the curated 12-color palette for the first 12 entries, then
        extends with golden-ratio HSV sampling for any additional colors needed.
        """
        colors = list(self.CURATED_12[:n])
        if n > len(self.CURATED_12):
            golden_ratio_conjugate = 0.618033988749895
            h = 0.1
            for _ in range(n - len(self.CURATED_12)):
                h = (h + golden_ratio_conjugate) % 1.0
                # Alternate saturation between two levels to aid distinction
                s = 0.85 if len(colors) % 2 == 0 else 0.55
                v = 0.90
                colors.append(mplt.colors.to_hex(mplt.colors.hsv_to_rgb([h, s, v])))
        return colors

class ColorManager:
    """
    Assigns and caches a consistent color per pattern across a session.

    The first time a pattern string is seen it is assigned a color (via
    `NgramColorManager`'s palette generator); subsequent lookups for the
    same pattern return the same color, so a pattern keeps its color across
    multiple charts.
    """
    def __init__(self):
        self.pattern_colors = {}
        # Use the advanced color generator from NgramColorManager
        self.ngram_color_manager = NgramColorManager()
        self.color_index = 0
    
    def reset(self):
        """Reset the color manager state"""
        self.pattern_colors = {}
        self.color_index = 0
    
    def pre_register_patterns(self, patterns):
        """
        Pre-register patterns with the color manager to ensure consistency.
        
        Args:
            patterns: List of patterns (tuples, lists, or strings) to register
        """
        for pattern in patterns:
            if isinstance(pattern, (list, tuple)):
                pattern_str = ", ".join(str(item) for item in pattern)
            else:
                pattern_str = str(pattern)
            self.get_color_for_pattern(pattern_str)
    
    def get_color_for_pattern(self, pattern_str):
        """Get or assign a color for a pattern"""
        if pattern_str not in self.pattern_colors:
            # Get all unique patterns we need colors for
            all_patterns = list(self.pattern_colors.keys()) + [pattern_str]
            n_colors_needed = len(all_patterns)
            
            # Generate enough colors using the advanced color generator
            colors = self.ngram_color_manager.generate_distinct_colors(n_colors_needed)
            
            # Assign the new color to the new pattern
            self.pattern_colors[pattern_str] = colors[-1]
        
        return self.pattern_colors[pattern_str]
    
    def assign_colors_to_dataframe(self, df):
        """Assign colors to dataframe patterns"""
        df = df.copy()
        df['color'] = df['pattern'].apply(self.get_color_for_pattern)
        return df

# Initialize global color manager
color_manager = ColorManager()

class PatternStyleManager:
    """
    Assigns each unique pattern a distinct combination of a hatch shape and
    a grey shade, as a print/colorblind-safe alternative to ColorManager's
    color-based distinction. Shades are light-to-medium so a black hatch
    always reads clearly on top of them, and shape/shade are cycled with
    coprime step sizes so consecutive patterns don't repeat the same shade.
    """
    HATCH_SHAPES = ['/', '\\', 'x', '-', '|', '+', '.']
    GREY_SHADES = ['#e0e0e0', '#b8b8b8', '#8f8f8f', '#666666', '#cfcfcf', '#a3a3a3']

    def __init__(self):
        self.pattern_styles = {}

    def reset(self):
        """Reset the pattern style manager state"""
        self.pattern_styles = {}

    def get_style_for_pattern(self, pattern_str):
        """Get or assign a hatch shape + grey shade combination for a pattern"""
        if pattern_str not in self.pattern_styles:
            index = len(self.pattern_styles)
            shape = self.HATCH_SHAPES[index % len(self.HATCH_SHAPES)]
            shade = self.GREY_SHADES[index % len(self.GREY_SHADES)]
            self.pattern_styles[pattern_str] = {'shape': shape, 'color': shade}
        return self.pattern_styles[pattern_str]

# Initialize global pattern style manager
pattern_style_manager = PatternStyleManager()

def _hatch_marker(color, shape):
    """
    Build a high-contrast Plotly marker spec for a greyscale hatch segment:
    a black hatch drawn larger and denser than Plotly's defaults so the
    shape reads clearly even in small bars, plus a solid outline to keep
    adjacent segments visually separated.
    """
    return dict(
        color=color,
        pattern=dict(shape=shape, size=10, solidity=0.55, fgcolor='black', fgopacity=1),
        line=dict(color='black', width=1)
    )

def create_bar_chart(variable, count, color, data, condition, *selectors):
    """
    Create a bar chart using Altair.
    """
    color_scale = alt.Scale(
        domain=data['pattern'].unique(),
        range=data['color'].unique()
    )
    
    observer_chart = alt.Chart(data).mark_bar().encode(
        x=variable,
        y=count,
        color=alt.Color('pattern:N', scale=color_scale, legend=alt.Legend(title='Pattern')),
        opacity=alt.condition(condition, alt.value(1), alt.value(0.2))
    ).add_params(
        *selectors
    )
    return observer_chart

def create_heatmap(x, x2, y, color, data, heat_map_width, heat_map_height, selector_condition, *selectors, tooltip, style='color'):
    """
    Create a heatmap. By default (style='color') this is an interactive Altair
    chart that distinguishes segments by color. Pass style='greyscale' to get a
    Plotly chart that instead distinguishes segments using grey shades combined
    with hatch fills, for print or colorblind-safe use. The greyscale style does
    not support the Altair cross-filtering selection behavior.
    """
    if style == 'greyscale':
        return _create_greyscale_heatmap(x, x2, y, data, heat_map_width, heat_map_height, tooltip)

    color_scale = alt.Scale(
        domain=data['pattern'].unique(),
        range=data['color'].unique()
    )

    heatmap = alt.Chart(data).mark_bar().encode(
        x=x,
        x2=x2,
        y=y,
        color=alt.Color('pattern:N', scale=color_scale, legend=alt.Legend(title='Pattern')),
        opacity=alt.condition(selector_condition, alt.value(1), alt.value(0.2)),
        tooltip=tooltip
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_params(
        *selectors
    )
    return heatmap

def _create_greyscale_heatmap(x_field, x2_field, y_field, data, heat_map_width, heat_map_height, tooltip):
    """
    Build a greyscale, hatch-patterned heatmap with Plotly. Each unique value
    in the 'pattern' column gets a distinct grey shade + hatch shape
    combination (from PatternStyleManager) so segments stay distinguishable
    without relying on color.
    """
    y_col = y_field.shorthand if hasattr(y_field, 'shorthand') else y_field
    voice_order = list(pd.unique(data[y_col]))
    hover_cols = [col for col in tooltip if col in data.columns]

    fig = go.Figure()
    for pattern in pd.unique(data['pattern']):
        subset = data[data['pattern'] == pattern]
        pattern_style = pattern_style_manager.get_style_for_pattern(pattern)
        fig.add_trace(go.Bar(
            base=subset[x_field],
            x=subset[x2_field] - subset[x_field],
            y=subset[y_col],
            orientation='h',
            name=str(pattern),
            marker=_hatch_marker(pattern_style['color'], pattern_style['shape']),
            customdata=subset[hover_cols].values if hover_cols else None,
            hovertemplate=(
                "<br>".join(f"{col}: %{{customdata[{i}]}}" for i, col in enumerate(hover_cols))
                + "<extra></extra>"
            ) if hover_cols else None,
        ))

    fig.update_layout(
        width=heat_map_width,
        height=heat_map_height,
        barmode='overlay',
        legend_title_text='Pattern',
        xaxis_title=f"{x_field}, {x2_field}",
        yaxis_title=y_col,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    fig.update_xaxes(showgrid=True, gridcolor='#e6e6e6', zeroline=False)
    fig.update_yaxes(categoryorder='array', categoryarray=voice_order, autorange='reversed',
                     showgrid=True, gridcolor='#e6e6e6', zeroline=False)
    return fig

def _create_greyscale_barchart(data):
    """
    Grey/hatch-patterned bar chart of pattern counts, styled to match
    _create_greyscale_heatmap's pattern styling so the two stay consistent
    when shown together.
    """
    counts = data['pattern'].value_counts()
    patterns = list(counts.index)
    styles = [pattern_style_manager.get_style_for_pattern(p) for p in patterns]

    fig = go.Figure(go.Bar(
        x=patterns,
        y=counts.values,
        marker=dict(
            color=[s['color'] for s in styles],
            pattern=dict(shape=[s['shape'] for s in styles], size=10, solidity=0.55, fgcolor='black', fgopacity=1),
            line=dict(color='black', width=1)
        ),
        showlegend=False
    ))
    fig.update_layout(xaxis_title='pattern', yaxis_title='count', plot_bgcolor='white', paper_bgcolor='white')
    fig.update_xaxes(showgrid=True, gridcolor='#e6e6e6', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#e6e6e6', zeroline=False)
    return fig

def _process_ngrams_df_helper(ngrams_df, main_col):
    """
    The output from the getNgram is usually a table with
    four voices and ngram of notes properties (duration or
    pitch). This method stack this property onto one column
    and mark which voices they are from.
    """
    # copy to avoid changing original ngrams df
    ngrams_df = ngrams_df.copy()
    # add a start column containing offsets
    ngrams_df.index.name = "start"
    ngrams_df = ngrams_df.reset_index().melt(id_vars=["start"], value_name=main_col, var_name="voice")
    ngrams_df["start"] = ngrams_df["start"].astype(float)
    return ngrams_df

def process_ngrams_df(ngrams_df, ngrams_duration=None, selected_pattern=None, voices=None):
    """
    This method combines ngrams from all voices in different columns
    into one column and calculates the starts and end points of the
    patterns.

    Durations are matched to n-grams by offset and voice (not by row
    position), so `ngrams_duration` may cover more cells than `ngrams_df`.
    N-grams with no matching duration get no end point and are left out of
    the heatmap, with a warning.
    """
    ngrams_df = _process_ngrams_df_helper(ngrams_df, 'pattern')
    if ngrams_duration is not None:
        durations = _process_ngrams_df_helper(ngrams_duration, 'duration')
        durations = durations.dropna(subset=['duration']).drop_duplicates(['start', 'voice'])
        ngrams_df = ngrams_df.merge(durations, on=['start', 'voice'], how='left')
        ngrams_df['end'] = ngrams_df['start'] + ngrams_df.pop('duration').astype(float)
        unmatched = ngrams_df['pattern'].notna() & ngrams_df['end'].isna()
        if unmatched.any():
            warnings.warn(f"{unmatched.sum()} n-gram(s) have no matching duration in ngrams_duration "
                          "(same offset and voice) and will not be plotted. Make the durations with "
                          "piece.durations(df=..., n=..., mask_df=ngrams_df).")
    else:
        # make end=start+1 just to display offsets
        ngrams_df['end'] = ngrams_df['start'] + 1
    
    # filter according to voices and patterns (after computing durations for correct offsets)
    if voices:
        voice_condition = ngrams_df['voice'].isin(voices)
        ngrams_df = ngrams_df[voice_condition].dropna(how='all')
    if selected_pattern:
        pattern_condition = ngrams_df['pattern'].isin(selected_pattern)
        ngrams_df = ngrams_df[pattern_condition].dropna(how='all')
    return ngrams_df

def generate_distinct_colors(n):
    """Generate `n` distinct colors using the HSV color space"""
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.65  # Fixed saturation
        value = 0.9  # Fixed value
        color = mplt.colors.to_hex(mplt.colors.hsv_to_rgb((hue, saturation, value)))
        colors.append(color)
    return colors

def ngrams_color_helper(new_processed_ngrams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a Series to the dataframe that assigns a unique hex color to each unique pattern
    using the global color manager to ensure consistency across plots.
    """
    return color_manager.assign_colors_to_dataframe(new_processed_ngrams_df)

def _ngram_chart_settings(ngrams_df, selected_patterns=None, voices=None, extra=()):
    """Settings phrases for an n-gram chart: how the n-grams were made
    (recorded on ngrams_df), then the chart's own filters."""
    parts = _data_settings(ngrams_df)
    if selected_patterns:
        k = len(selected_patterns)
        parts.append(f"{k} selected pattern{'s' if k > 1 else ''}")
    if voices:
        parts.append('voices: ' + ', '.join(map(str, voices)))
    return parts + [p for p in extra if p]


def _altair_title(title, parts):
    """Altair title with the settings as a subtitle (None if neither)."""
    parts = [p for p in parts if p]
    if title is None and not parts:
        return None
    return alt.TitleParams(text=title or 'N-grams', subtitle=' · '.join(parts) if parts else alt.Undefined,
                           anchor='start')


def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300, includeCount=False, title=None, style='color',
                            settings=()):
    """
    Plot a heatmap for crim-intervals getNgram's processed output. Pass
    style='greyscale' for a hatch-patterned, grey-shaded Plotly chart instead
    of the default color-coded Altair chart (see create_heatmap).
    """
    processed_ngrams_df = processed_ngrams_df.dropna(how='any')
    selector = alt.selection_point(fields=['pattern'])
    y = alt.Y("voice", sort=None)

    # make a copy of the processed n_grams and turn them into Strings
    new_processed_ngrams_df = processed_ngrams_df.copy()
    new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
        lambda cell: ", ".join(str(item) for item in cell),
        na_action='ignore'
    )

    # Use the color manager to assign consistent colors
    new_processed_ngrams_df = ngrams_color_helper(new_processed_ngrams_df)

    heatmap = create_heatmap('start', 'end', y, 'pattern', new_processed_ngrams_df, heatmap_width, heatmap_height,
                            selector, selector, tooltip=['start', 'end', 'pattern'], style=style)

    if style == 'greyscale':
        if includeCount:
            # give the count bar chart its own fixed budget (it needs room for
            # rotated x-axis pattern labels), and enforce a minimum for the
            # heatmap panel itself, rather than squeezing both into a small
            # fraction of the raw heatmap_height
            bar_chart_height = 300
            heatmap_panel_height = max(heatmap_height, 400)
            total_height = bar_chart_height + heatmap_panel_height
            patterns_bar = _create_greyscale_barchart(new_processed_ngrams_df)
            chart = make_subplots(
                rows=2, cols=1,
                row_heights=[bar_chart_height / total_height, heatmap_panel_height / total_height],
                vertical_spacing=0.15
            )
            for trace in patterns_bar.data:
                chart.add_trace(trace, row=1, col=1)
            for trace in heatmap.data:
                chart.add_trace(trace, row=2, col=1)
            chart.update_layout(width=heatmap_width, height=total_height, legend_title_text='Pattern',
                              plot_bgcolor='white', paper_bgcolor='white')
            chart.update_xaxes(showgrid=True, gridcolor='#e6e6e6', zeroline=False)
            chart.update_yaxes(showgrid=True, gridcolor='#e6e6e6', zeroline=False)
            chart.update_xaxes(tickangle=-45, row=1, col=1)
            chart.update_yaxes(
                categoryorder='array',
                categoryarray=list(pd.unique(new_processed_ngrams_df['voice'])),
                autorange='reversed',
                row=2, col=1
            )
        else:
            chart = heatmap
        if title is not None or settings:
            chart.update_layout(title=_settings_title(title or 'N-grams', settings))
        return chart

    if includeCount:
        variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
        patterns_bar = create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)
        chart = alt.vconcat(patterns_bar, heatmap)
    else:
        chart = heatmap

    # title, with the settings as a subtitle
    alt_title = _altair_title(title, settings)
    if alt_title is not None:
        chart = chart.properties(title=alt_title)

    return chart

def plot_ngrams_heatmap(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[],
                       heatmap_width=800, heatmap_height=300, includeCount=False, title=None, style='color'):
    """
    Plot a heatmap for crim-intervals getNgram's output. Pass style='greyscale'
    for a hatch-patterned, grey-shaded Plotly chart instead of the default
    color-coded Altair chart (see create_heatmap).

    The settings used to make the n-grams (recorded on `ngrams_df` by
    melodic/harmonic/ngrams, see `get_settings`) and the patterns and voices
    selected here are shown below the title.

    `ngrams_duration` (optional) gives each bar its length. Make it with
    `piece.durations(df=mel, n=n, mask_df=ngrams_df)`, using the same `df`
    and `n` as the n-grams. Durations are matched by offset and voice; any
    n-gram without one is left out, with a warning.
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
                                          selected_pattern=selected_patterns, voices=voices)
    return _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=heatmap_width,
                                 heatmap_height=heatmap_height, includeCount=includeCount, title=title, style=style,
                                 settings=_ngram_chart_settings(ngrams_df, selected_patterns, voices))

def plot_ngrams_barchart(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], chart_width=800,
                        chart_height=300, title=None):
    """
    Plot a bar chart for crim-intervals getNgram's output. The settings used
    to make the n-grams, and the patterns and voices selected, are shown below
    the title.
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
                                          selected_pattern=selected_patterns,
                                          voices=voices)
    chart = _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=chart_width, chart_height=chart_height)
    alt_title = _altair_title(title, _ngram_chart_settings(ngrams_df, selected_patterns, voices))
    return chart.properties(title=alt_title) if alt_title is not None else chart

def _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=800, chart_height=300):
    """
    Plot a bar chart for crim-intervals getNgram's processed output.
    """
    processed_ngrams_df = processed_ngrams_df.dropna(how='any')
    selector = alt.selection_point(fields=['pattern'])
    
    # make a copy of the processed n_grams and turn them into Strings
    new_processed_ngrams_df = processed_ngrams_df.copy()
    new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
        lambda cell: ", ".join(str(item) for item in cell),
        na_action='ignore'
    )
    
    # Add color assignment for consistency
    new_processed_ngrams_df = ngrams_color_helper(new_processed_ngrams_df)
    
    variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
    return create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)


# Helper function for your analysis code
def pre_register_patterns(shared_entries):
    """Pre-register patterns with the color manager to ensure consistency"""
    for pattern in shared_entries:
        if isinstance(pattern, (list, tuple)):
            pattern_str = ", ".join(str(item) for item in pattern)
        else:
            pattern_str = str(pattern)
        color_manager.get_color_for_pattern(pattern_str)
# 2025 version
# FIXED: Updated bar chart function to include color consistency
def _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=800, chart_height=300):
    """
    Plot a bar chart for crim-intervals getNgram's processed output.
    """
    processed_ngrams_df = processed_ngrams_df.dropna(how='any')
    selector = alt.selection_point(fields=['pattern'])
    
    # make a copy of the processed n_grams and turn them into Strings
    new_processed_ngrams_df = processed_ngrams_df.copy()
    new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
        lambda cell: ", ".join(str(item) for item in cell), 
        na_action='ignore'
    )
    
    # FIXED: Add color assignment for consistency
    new_processed_ngrams_df = ngrams_color_helper(new_processed_ngrams_df)
    
    variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
    return create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)

# unchanged
def _from_ema_to_offsets(df, ema_column):
    """
    This method adds a columns of start and end measure of patterns into
    the relationship dataframe using the column with the ema address.

    :param df: dataframe containing relationships between patterns retrieved
    from CRIM relationship json
    :param ema_column: the name of the column storing ema address.
    :return: the processed dataframe with two new columns start and end
    """
    # retrieve the measures from ema address and create start and end in place
    df['locations'] = df[ema_column].str.split("/", n=1, expand=True)[0]
    df['locations'] = df['locations'].str.split(",")
    df = df.explode('locations')
    df[['start', 'end']] = df['locations'].str.split("-", expand=True).ffill()

    df['start'] = df['start'].astype(float)
    df['end'] = df['end'].astype(float)
    return df


def _process_crim_json_url(url_column):
    # remove 'data' from http://crimproject.org/data/observations/1/ or http://crimproject.org/data/relationships/5/
    url_column = url_column.map(lambda cell: cell.replace('data/', ''))
    return url_column


def plot_comparison_heatmap(df, ema_col, main_category='musical_type', other_category='observer.name', option=1,
                            heat_map_width=800, heat_map_height=300):
    """
    This method plots a chart for relationships/observations dataframe retrieved from their
    corresponding json files. This chart has two bar charts displaying the count of variables
    the users selected, and a heatmap displaying the locations of the relationship.
    :param df: relationships or observations dataframe
    :param ema_col: name of the ema column
    :param main_category: name of the main category for the first bar chart.
    The chart would be colored accordingly (default='musical_type').
    :param other_category: name of the other category for the zeroth bar chart.
    (default='observer.name')
    :param heat_map_width: the width of the final heatmap (default=800)
    :param heat_map_height: the height of the final heatmap (default =300)
    :return: a big chart containing two smaller bar chart and a heatmap
    """

    df = df.copy()  # create a deep copy of the selected observations to protect the original dataframe
    df = _from_ema_to_offsets(df, ema_col)

    # sort by id
    df.sort_values(by=main_category, inplace=True)

    df = _from_ema_to_offsets(df, ema_col)
    df['website_url'] = _process_crim_json_url(df['url'])

    df['id'] = df['id'].astype(str)

    # because altair doesn't work when the categories' names have periods,
    # a period is replaced with a hyphen.

    new_other_category = other_category.replace(".", "_")
    new_main_category = main_category.replace(".", "_")

    df.rename(columns={other_category: new_other_category, main_category: new_main_category}, inplace=True)

    other_selector = alt.selection_point(fields=[new_other_category])
    main_selector = alt.selection_point(fields=[new_main_category])

    other_category = new_other_category
    main_category = new_main_category

    bar1 = create_bar_chart(main_category, str('count(' + main_category + ')'), main_category, df,
                            other_selector | main_selector, main_selector)
    bar0 = create_bar_chart(other_category, str('count(' + other_category + ')'), main_category, df,
                            other_selector | main_selector, other_selector)

    heatmap = alt.Chart(df).mark_bar().encode(
        x='start',
        x2='end',
        y='id',
        href='website_url',
        color=main_category,
        opacity=alt.condition(other_selector | main_selector, alt.value(1), alt.value(0.2)),
        tooltip=['website_url', main_category, other_category, 'start', 'end', 'id']
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_params(
        main_selector
    ).interactive()

    chart = alt.vconcat(
        alt.hconcat(
            bar1,
            bar0
        ),
        heatmap
    )

    return chart


def _recognize_integers(num_str):
    if num_str[0] == '-':
        return num_str[1:].isdigit()
    else:
        return num_str.isdigit()


def _close_match_helper(cell):
    # process each cell into an interator of *floats* for easy comparisons
    if type(cell) == str:
        cell = cell.split(",")

    if _recognize_integers(cell[0]):
        cell = tuple(int(item) for item in cell)

    return cell


def _close_match(ngrams_df, key_pattern):
    ngrams_df['pattern'] = ngrams_df['pattern'].map(lambda cell: _close_match_helper(cell), na_action='ignore')
    # making sure that key pattern and other patterns are tuple of string or ints
    if not (type(ngrams_df.iloc[0, :]['pattern']) == type(key_pattern) == tuple
            or type(ngrams_df.iloc[0, :]['pattern'][0]) == type(key_pattern[0])):
        raise Exception("Input patterns and patterns inside dataframe aren't tuple of strings/ints")

    ngrams_df['score'] = ngrams_df['pattern'].map(
        lambda cell: 100 * textdistance.levenshtein.normalized_similarity(key_pattern, cell), na_action='ignore')
    return ngrams_df


def plot_close_match_heatmap(ngrams_df, key_pattern, ngrams_duration=None, selected_patterns=[], voices=[],
                             heatmap_width=800, heatmap_height=300, title=None):
    """
    Plot how closely the other vectors match a selected vector.
    The settings used to make the n-grams and the key pattern are shown below
    the title.
    Uses the Levenshtein distance.
    :param ngrams_df: crim-intervals getNgram's output
    :param key_pattern: a pattern the users selected to compare other patterns with (tuple of floats)
    :param selected_pattern: the specific other vectors the users selected
    :param ngrams_duration: if None, simply output the offsets. If the users input a
    list of durations, caculate the end by adding durations with offsets and
    display the end on the heatmap accordingly.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """

    ngrams = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration, selected_pattern=selected_patterns,
                               voices=voices)

    ngrams.dropna(subset=['pattern'], inplace=True)
    # dropping the NAs in pattern
    # calculate the score

    key_pattern = _close_match_helper(key_pattern)
    score_ngrams = _close_match(ngrams, key_pattern)

    slider = alt.binding_range(min=0, max=100, step=1, name='cutoff:')
    selector = alt.selection_single(name="SelectorName", fields=['cutoff'],
                                    bind=slider, init={'cutoff': 50})

    # sort voices
    if voices != None:
        if len(voices) == 0:
            voices = None
    y = alt.Y("voice", sort=voices)

    chart = create_heatmap('start', 'end', y, 'score', score_ngrams, heatmap_width, heatmap_height,
                           alt.datum.score > selector.cutoff, selector, tooltip=['start', 'end', 'pattern', 'score'])
    settings = _ngram_chart_settings(ngrams_df, selected_patterns, voices,
                                     extra=['compared with ' + ', '.join(str(x) for x in key_pattern)])
    return chart.properties(title=_altair_title(title or 'Close Matches', settings))


def generate_ngrams_and_duration(piece, df, n=3, exclude=['Rest'],
                                 interval_settings=('d', True, True), offsets='first'):
    """
    This method accept a model and a dataframe with the melody or notes
    and rests and generate an ngram (in columnwise and unit=0 setting)
    and a corresponding duration ngram
    :param model: an Imported Piece object.
    :param df: dataframe containing consecutive notes.
    :param n: accept any positive integers and would output ngrams of the corresponding sizes
    can't handle the n=-1 option (refer to getNgrams documentation for more)
    :param exclude: (refer to getNgrams documentation)
    :param interval_settings: (refer to getNgrams documentation)
    :param offsets: (refer to getNgrams documentation)
    :return: ngram and corresponding duration dataframe!
    """
    if n == -1:
        raise Exception("Cannot calculate the duration for this type of ngrams")

    # compute dur for the ngrams
    dur = piece.getDuration(df)
    dur = dur.reindex_like(df).map(str, na_action='ignore')
    # combine them and generate ngrams and duration at the same time
    notes_dur = pd.concat([df, dur])
    ngrams = piece.ngrams(df=df, n=n, exclude=exclude,
                             interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = piece.ngrams(df=dur, n=n, exclude=exclude,
                                 interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = dur_ngrams.reindex_like(ngrams)

    # sum up durations!
    dur_ngrams = dur_ngrams.map(lambda cell: sum([float(element) for element in cell]), na_action='ignore')

    return ngrams, dur_ngrams


# Network visualizations from CRIM Django Data
def process_network_df(df, interval_column_name, ema_column_name):
    """
    Create a small dataframe containing network
    """
    result_df = pd.DataFrame()
    result_df[['piece.piece_id', 'url', interval_column_name]] = \
        df[['piece.piece_id', 'url', interval_column_name]].copy()
    result_df[['segments']] = \
        df[ema_column_name].astype(str).str.split("/", 1, expand=True)[0]
    result_df['segments'] = result_df['segments'].str.split(",")
    return result_df


# add nodes to graph
def create_interval_networks(interval_column, interval_type):
    """
    Helper method to create networks for observations' intervals
    :param interval_column: column containing the intervals users want to
    examine
    :param interval_type: 'melodic' or 'time'
    :return: a dictionary of networks describing the intervals
    """
    # dictionary maps the first time/melodic interval to its corresponding
    # network
    networks_dict = {'all': Network(directed=True, notebook=True)}
    interval_column = interval_column.astype(str)
    networks_dict['all'].add_node('all', color='red', shape='circle', level=0)

    # create nodes from the patterns
    for node in interval_column:
        # create nodes according to the interval types
        if interval_type == 'melodic':
            nodes = re.sub(r'([+-])(?!$)', r'\1,', node).split(",")
            separator = ''
        elif interval_type == 'time':
            nodes = node.split("/")
            separator = '/'
        else:
            raise Exception("Please put either 'time' or 'melodic' for `type_interval`")

        # nodes would be grouped according to the first interval
        group = nodes[0]

        if not group in networks_dict:
            networks_dict[group] = Network(directed=True, notebook=True)

        prev_node = 'all'
        for i in range(1, len(nodes)):
            node_id = separator.join(node for node in nodes[:i])
            # add to its own family network
            networks_dict[group].add_node(node_id, group=group, physics=False, level=i)
            if prev_node != "all":
                networks_dict[group].add_edge(prev_node, node_id)

            # add to the big network
            networks_dict['all'].add_node(node_id, group=group, physics=False, level=i)
            networks_dict['all'].add_edge(prev_node, node_id)
            prev_node = node_id

    return networks_dict


def _manipulate_processed_network_df(df, interval_column, search_pattern_starts_with):
    """
    This method helps to generate interactive widget in create_interactive_compare_df
    :param search_pattern_starts_with:
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :return: A filtered and colored dataframe based on the option the user selected.
    """
    mask = df[interval_column].astype(str).str.startswith(pat=search_pattern_starts_with)
    filtered_df = df[mask].copy()
    return filtered_df.fillna("-").style.map(
        lambda x: "background: #ccebc5" if search_pattern_starts_with in x else "")

# new cadence visualization functions

def _ordered_with_extras(order, values):
    """Return `order` plus any values not in it (sorted, at the end), so a
    custom order never silently drops data."""
    present = [v for v in pd.unique(pd.Series(values).dropna())]
    extras = sorted(str(v) for v in present if v not in order)
    return list(order) + extras


def _voice_sort_key(v):
    v = str(v)
    return (0, int(v), v) if v.isdigit() else (1, 0, v)


def _single_piece_label(df):
    """'Composer: Title' when df holds one piece, else None."""
    if 'Title' not in df.columns or df['Title'].nunique() != 1:
        return None
    title = df['Title'].iloc[0]
    if 'Composer' in df.columns and pd.notna(df['Composer'].iloc[0]):
        return f"{df['Composer'].iloc[0]}: {title}"
    return str(title)


def _piece_label(df, title_col='Title', composer_col='Composer'):
    """'Composer: Title' for one piece, 'Corpus' for several, None if unknown."""
    if title_col not in df.columns:
        return None
    if df[title_col].nunique() > 1:
        return 'Corpus'
    return _single_piece_label(df.rename(columns={title_col: 'Title', composer_col: 'Composer'}))


def _n_pieces(df, title_col='Title'):
    n = df[title_col].nunique() if title_col in df.columns else 1
    return f'{n} pieces' if n > 1 else None


_KIND_LABELS = {'q': 'with quality', 'd': 'diatonic', 'c': 'chromatic', 's': 'chromatic',
                'z': 'zero-based'}


def _interval_label(s):
    kind = str(s.get('kind', 'q'))[:1].lower()
    compound = s.get('compound', True)
    return ', '.join([_KIND_LABELS.get(kind, kind),
                      'directed' if s.get('directed', True) else 'undirected',
                      'simple' if compound in (False, 'simple') else 'compound'])


def _data_settings(df):
    """
    Describe the analysis settings recorded on a CRIM Intervals result
    (see main_objs.get_settings) as short phrases for a chart's settings line.
    """
    s = getattr(df, 'attrs', {}).get('crim_settings', {})
    parts = []
    notes = s.get('notes', {})
    if notes.get('combineUnisons'):
        parts.append('unisons combined')
    if 'melodic' in s:
        m = s['melodic']
        parts.append('melodic: ' + _interval_label(m) + (f", unit {m['unit']}" if m.get('unit') else ''))
    if 'harmonic' in s:
        h = s['harmonic']
        parts.append('harmonic: ' + _interval_label(h) + (', against lowest voice' if h.get('againstLow') else ''))
    if 'sonorities' in s:
        so = s['sonorities']
        parts.append('sonorities: ' + ('simple' if so.get('compound') in (False, 'simple') else 'compound')
                     + (', sorted' if so.get('sort') else ', unsorted'))
    if 'ngrams' in s:
        n = s['ngrams'].get('n')
        parts.append('longest n-grams' if n == -1 else f'n = {n}')
    if 'entries' in s:
        e = s['entries']
        if e.get('n') is not None and 'ngrams' not in s:
            parts.append(f"n = {e['n']}")
        if e.get('anywhere'):
            # anywhere=True returns every occurrence of an entry pattern,
            # not just the ones that follow a rest or fermata
            parts.append(('thematic ' if e.get('thematic') else '') + 'entry patterns, all occurrences')
        else:
            parts.append('thematic entries' if e.get('thematic') else 'entries only')
    if 'sonority_ngrams' in s:
        g = s['sonority_ngrams']
        parts += [f"n = {g['ngram_length']}", f"min. beat strength = {g['minimum_beat_strength']}",
                  'compound' if g['compound'] else 'simple', 'sorted' if g['sort'] else 'unsorted']
    if 'melodic_species' in s:
        parts.append('entries only' if s['melodic_species'].get('limit_to_entries') else 'all leaps')
    if 'voice_ranges' in s:
        v = s['voice_ranges']
        parts.append(f"range of top {v.get('top_n')} pitches")
        if v.get('final') is not None:
            parts.append(f"final: {v['final']}")
    return parts


def _settings_title(title, parts):
    """Plotly title with a second, smaller line listing the settings."""
    parts = [p for p in parts if p]
    return f"{title}<br><sup>{' · '.join(parts)}</sup>" if parts else title


def _category_yaxis(fig, categories, **kwargs):
    """Fix a categorical y axis to show every category (bottom to top in the
    given order). Without an explicit range, Plotly sizes shared facet axes
    from the first panel only and clips categories found in other pieces."""
    kwargs.setdefault('title', None)
    fig.update_yaxes(categoryorder='array', categoryarray=categories,
                     range=[-0.5, len(categories) - 0.5], **kwargs)


def _facet_by_title(fig, n_titles, row_height):
    """Tidy a figure faceted with facet_row='Title': show each piece's title
    (without 'Title=') above its row, left-aligned, and size the figure."""
    centers = {round((ax.domain[0] + ax.domain[1]) / 2, 3): ax.domain[1] for ax in fig.select_yaxes()}
    for a in fig.layout.annotations:
        if isinstance(a.text, str) and a.text.startswith('Title='):
            top = centers.get(round(a.y, 3), a.y)
            a.update(text='<b>' + a.text.split('=', 1)[1] + '</b>', textangle=0,
                     x=0, xanchor='left', y=top, yanchor='bottom', font_size=13)
    # extra top margin: room for a settings line above the first panel title
    fig.update_layout(height=max(450, row_height * n_titles + 150), margin=dict(t=130))
    return fig


# cadence radar
def cadence_radar(cadences, groupby_column='Title', tone_ordering='Diatonic',
                  limit_to_active=True, chart_title=None):
    """
    Radar plot of the relative distribution of cadence tones: for each group
    (piece, composer, ...), the percentage of its cadences on each tone.

    Works with `piece.cadences()` or `corpus.cadences()`.

    Parameters
    ----------
    cadences : pandas.DataFrame
        Output of ImportedPiece.cadences or CorpusBase.cadences. Needs a
        'Tone' column and the `groupby_column`.
    groupby_column : str, optional (default 'Title')
        One polygon per value of this column, e.g. 'Title' or 'Composer'.
    tone_ordering : str or list, optional (default 'Diatonic')
        Order of tones around the circle: 'Diatonic', 'Fifths', 'Thirds',
        'Chromatic' (see `sorting_lists.cadence_tone_orders`), or your own list
        (music21 spelling, e.g. 'B-'). Tones in the data but not in the order
        are added at the end.
    limit_to_active : bool, optional (default True)
        If True, show only tones that occur in the data. If False, show every
        tone in the ordering.
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> cadence_radar(piece.cadences()).show()
    >>> cadence_radar(corpus.cadences(), groupby_column='Composer', tone_ordering='Fifths')
    """
    if groupby_column not in cadences.columns:
        raise ValueError(f"cadences has no '{groupby_column}' column; "
                         f"choose one of {list(cadences.columns)}")
    order = cadence_tone_orders[tone_ordering] if isinstance(tone_ordering, str) else list(tone_ordering)
    cads = cadences.dropna(subset=['Tone'])
    if cads.empty:
        raise ValueError('No cadences with a Tone to plot.')

    grouped = cads.groupby([groupby_column, 'Tone']).size().rename('count')
    tones = _ordered_with_extras(order, cads['Tone'])
    if limit_to_active:
        tones = [t for t in tones if t in set(cads['Tone'])]
    groups = list(dict.fromkeys(cads[groupby_column]))
    # fill missing (group, tone) pairs with 0 so each polygon is complete
    full = pd.MultiIndex.from_product([groups, tones], names=[groupby_column, 'Tone'])
    grouped = grouped.reindex(full, fill_value=0).reset_index()
    totals = grouped.groupby(groupby_column)['count'].transform('sum')
    grouped['Percentage'] = (grouped['count'] / totals * 100).round(1)

    if chart_title is None:
        label = _piece_label(cadences)
        chart_title = f'Cadence Tones in {label}' if label else 'Cadence Tones'
    chart_title = _settings_title(chart_title, [
        f'{len(cads)} cadences',
        f'tone order: {tone_ordering}' if isinstance(tone_ordering, str) else 'custom tone order',
        'all tones' if not limit_to_active else None,
        f'grouped by {groupby_column}' if groupby_column != 'Title' else None,
        _n_pieces(cadences)])

    fig = px.line_polar(grouped, r='Percentage', theta='Tone', line_close=True,
                        color=groupby_column, markers=True,
                        hover_data={'count': True},
                        color_discrete_sequence=contrasting_colors,
                        category_orders={'Tone': tones, groupby_column: groups})
    fig.update_traces(fill='toself', line=dict(width=2))
    fig.update_layout(
        width=800, height=650,
        legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5,
                    title=dict(text=groupby_column, side='top', font_size=12),
                    bordercolor='black', borderwidth=1, bgcolor='rgba(255,255,255,0.8)'),
        title=dict(text=chart_title, x=0.5),
        polar=dict(radialaxis=dict(visible=True, ticksuffix='%')),
        margin=dict(b=150, t=130),
        showlegend=len(groups) > 1)
    return fig


# cadence progress viz
def cadence_progress(cadences, chart_title=None):
    """
    Scatter plot of cadences across the course of a piece: Progress (0 = start,
    1 = end) on the x axis, cadence tone on the y axis, colored by cadence type.

    Works with `piece.cadences()` or `corpus.cadences()`. For a corpus each
    piece gets its own row, since Progress is measured within each piece.

    Parameters
    ----------
    cadences : pandas.DataFrame
        Output of ImportedPiece.cadences or CorpusBase.cadences. Needs
        'Progress', 'Tone' and 'CadType' columns ('Title' for several pieces).
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> cadence_progress(piece.cadences()).show()
    >>> cadence_progress(corpus.cadences()).show()   # one row per piece
    """
    df = cadences.dropna(subset=['Tone']).copy()   # never alter the caller's data
    if df.empty:
        raise ValueError('No cadences with a Tone to plot.')
    tones = _ordered_with_extras(cadence_progress_tone_order, df['Tone'])
    tones = [t for t in tones if t in set(df['Tone'])]
    cad_types = _ordered_with_extras(cadence_type_order, df['CadType'])
    cad_types = [c for c in cad_types if c in set(df['CadType'])]
    n_titles = df['Title'].nunique() if 'Title' in df.columns else 1

    hover = {c: True for c in ['Composer', 'Title', 'Measure', 'Beat'] if c in df.columns}
    fig = px.scatter(df, x='Progress', y='Tone', color='CadType',
                     facet_row='Title' if n_titles > 1 else None,
                     facet_row_spacing=0.25 / n_titles if n_titles > 1 else None,
                     hover_data=hover,
                     color_discrete_map=cadence_type_colors,
                     category_orders={'Tone': tones, 'CadType': cad_types,
                                      'Title': list(dict.fromkeys(df['Title'])) if n_titles > 1 else []})
    fig.update_traces(marker=dict(size=18 if n_titles > 1 else 25, opacity=0.85,
                                  line=dict(width=1, color='white')))
    # categories run bottom-to-top in the order given (flats at the bottom)
    _category_yaxis(fig, tones, title='Tone')
    fig.update_xaxes(range=[-0.02, 1.02])

    if chart_title is None:
        label = _piece_label(df)
        chart_title = f'Progress of Cadences in {label}' if label else 'Progress of Cadences'
    chart_title = _settings_title(chart_title, [f'{len(df)} cadences', _n_pieces(df)])
    fig.update_layout(title=chart_title, width=900, height=500,
                      legend=dict(title_text='Cadence Type', orientation='v'))
    if n_titles > 1:
        fig.update_yaxes(title='')
        _facet_by_title(fig, n_titles, row_height=220)
    return fig


# sonority ngram progress viz
def sonority_ngram_progress(son_ngrams, min_count=1, max_count=None, top_n=None,
                            patterns=None, order='first', facet=False, height=None,
                            show_labels=None, chart_title=None):
    """
    Scatter plot of sonority n-grams across the course of a piece: Progress
    (0 = start, 1 = end) on the x axis, each n-gram pattern (Low_Sonority) on
    the y axis, colored by piece. Each pattern has its own row, so a pattern
    that recurs shows up as several dots on one horizontal line.

    Works with the output of `corpus.sonority_ngrams()` for one piece
    (`CorpusBase([path])`) or many.

    Parameters
    ----------
    son_ngrams : pandas.DataFrame
        Output of CorpusBase.sonority_ngrams (with include_progress=True, the
        default). Needs 'Progress' and 'Low_Sonority' columns.
    min_count, max_count : int, optional
        Keep only patterns whose total count (across all pieces given) is in
        this range. max_count=None means no upper limit.
    top_n : int, optional
        After the count filter, keep only the N most frequent patterns.
    patterns : list of str, optional
        Keep only these Low_Sonority patterns (applied before the count filter).
    order : {'first', 'count', 'alpha'}, optional (default 'first')
        How the patterns (rows) are stacked on the y axis, bottom to top:
        'first' - order of first appearance (piece order, then Progress). New
                  material climbs diagonally; a return to an earlier pattern
                  falls back to that pattern's lower row.
        'count' - least to most frequent, so the most frequent patterns are at
                  the top; ties are in order of first appearance.
        'alpha' - alphabetical.
    facet : bool, optional (default False)
        If True and there are several pieces, give each piece its own row
        instead of overlaying them.
    height : int, optional
        Figure height in pixels. Defaults to 600 (or 300 per piece with
        facet=True), however many patterns there are, so the overall flow
        stays visible; markers shrink to fit.
    show_labels : bool, optional
        Show the n-gram labels on the y axis. By default they are shown only
        for 40 patterns or fewer; hover over a point to see its n-gram.
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> son = corpus.sonority_ngrams(ngram_length=4)
    >>> sonority_ngram_progress(son, min_count=3).show()
    >>> sonority_ngram_progress(son, top_n=20, order='count').show()
    >>> sonority_ngram_progress(son, min_count=2, facet=True).show()
    """
    missing = [c for c in ['Progress', 'Low_Sonority'] if c not in son_ngrams.columns]
    if missing:
        raise ValueError(f"son_ngrams is missing {missing}; use the output of "
                         "corpus.sonority_ngrams(include_progress=True)")
    if order not in ('first', 'count', 'alpha'):
        raise ValueError("order must be 'first', 'count' or 'alpha'")
    df = son_ngrams.dropna(subset=['Low_Sonority']).copy()   # never alter the caller's data
    df = df[df['Low_Sonority'].astype(str) != '']
    if patterns is not None:
        df = df[df['Low_Sonority'].isin(list(patterns))]

    totals = df['Low_Sonority'].value_counts()
    keep = totals[totals >= min_count]
    if max_count is not None:
        keep = keep[keep <= max_count]
    if top_n is not None:
        keep = keep.head(top_n)
    if keep.empty:
        raise ValueError('No sonority n-grams match these filters '
                         f'(pattern counts range from {totals.min() if len(totals) else 0} '
                         f'to {totals.max() if len(totals) else 0}).')
    df = df[df['Low_Sonority'].isin(keep.index)]
    df['Count'] = df['Low_Sonority'].map(keep)

    # y-axis categories run bottom-to-top in this order
    first_seen = list(dict.fromkeys(df['Low_Sonority']))
    if order == 'first':
        pattern_order = first_seen
    elif order == 'alpha':
        pattern_order = sorted(first_seen, key=str)
    else:
        rank = {p: i for i, p in enumerate(first_seen)}
        pattern_order = sorted(first_seen, key=lambda p: (keep[p], rank[p]))

    has_title = 'Title' in df.columns
    titles = list(dict.fromkeys(df['Title'])) if has_title else []
    n_titles = len(titles) if has_title else 1
    do_facet = facet and n_titles > 1

    hover = {c: True for c in ['Composer', 'Title', 'Measure', 'Beat', 'Count'] if c in df.columns}
    fig = px.scatter(df, x='Progress', y='Low_Sonority',
                     color='Title' if has_title else None,
                     facet_row='Title' if do_facet else None,
                     facet_row_spacing=0.25 / n_titles if do_facet else None,
                     hover_data=hover,
                     color_discrete_sequence=contrasting_colors,
                     category_orders={'Low_Sonority': pattern_order, 'Title': titles})
    # compact: fixed height, so markers shrink as rows multiply
    n_patterns = len(pattern_order)
    row_height = 300 if do_facet else (height or 600) - 150
    marker_size = max(4, min(12, row_height / max(n_patterns, 1) * 1.5))
    show_labels = n_patterns <= 40 if show_labels is None else show_labels
    fig.update_traces(marker=dict(size=marker_size, opacity=0.8, line=dict(width=0.5, color='white')))
    _category_yaxis(fig, pattern_order, title='Sonority N-gram' if not do_facet else '',
                    showticklabels=show_labels, showgrid=show_labels)
    fig.update_xaxes(range=[-0.02, 1.02])

    # piece vs corpus is judged from the input, not what survives the filters
    n_input = son_ngrams['Title'].nunique() if 'Title' in son_ngrams.columns else 1
    if chart_title is None:
        label = _single_piece_label(son_ngrams)
        chart_title = f'Sonority N-grams in {label}' if label else 'Sonority N-grams in Corpus'
    # second title line: the settings that produced this plot
    settings = _data_settings(son_ngrams)
    if not settings:   # settings lost (e.g. read from CSV): infer n from 'LowInterval_Sonority' events
        settings = [f"n = {len(str(pattern_order[0]).split('_')) // 2}"]
    count_txt = f'count {min_count}–{max_count}' if max_count is not None else f'count ≥ {min_count}'
    settings.append(count_txt)
    if top_n is not None:
        settings.append(f'top {top_n}')
    if patterns is not None:
        settings.append(f'{len(list(patterns))} selected patterns')
    settings.append(f'order: {order}')
    if n_input > 1:
        settings.append(f'{n_input} pieces')
    chart_title = _settings_title(chart_title, settings)
    fig.update_layout(title=chart_title, width=1200, height=height or 600,
                      legend=dict(title_text='Title'),
                      showlegend=has_title and n_input > 1)
    if do_facet:
        _facet_by_title(fig, n_titles, row_height=row_height)
        if height:
            fig.update_layout(height=height)
    return fig


def cadence_bar_chart(cadences, by='CadType', percent=True, groupby_column='Title',
                      tone_ordering='Diatonic', chart_title=None):
    """
    Grouped bar chart of cadence types or cadence tones, one bar per group
    (piece, composer, ...) in each category.

    Works with `piece.cadences()` or `corpus.cadences()`.

    Parameters
    ----------
    cadences : pandas.DataFrame
        Output of ImportedPiece.cadences or CorpusBase.cadences.
    by : str, optional (default 'CadType')
        'CadType' for cadence types or 'Tone' for cadence tones. Evaded and
        abandoned cadences have no Tone, so they are counted for 'CadType' but
        left out (with a printed note) for 'Tone'.
    percent : bool, optional (default True)
        True: each bar is a percentage of its group's cadences, so pieces of
        different lengths can be compared. False: raw counts.
    groupby_column : str, optional (default 'Title')
        One bar color per value of this column, e.g. 'Title' or 'Composer'.
    tone_ordering : str or list, optional (default 'Diatonic')
        Order of tones on the x axis when by='Tone' (as in `cadence_radar`).
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> cadence_bar_chart(corpus.cadences()).show()
    >>> cadence_bar_chart(corpus.cadences(), by='Tone', groupby_column='Composer')
    """
    if by not in ('CadType', 'Tone'):
        raise ValueError("by must be 'CadType' or 'Tone'.")
    if groupby_column not in cadences.columns:
        raise ValueError(f"cadences has no '{groupby_column}' column; "
                         f"choose one of {list(cadences.columns)}")
    cads = cadences.dropna(subset=['CadType'])
    if by == 'Tone':
        missing = cads['Tone'].isna().sum()
        if missing:
            print(f'Note: {missing} cadence(s) without a Tone (evaded/abandoned) are not shown.')
        cads = cads.dropna(subset=['Tone'])
        order = cadence_tone_orders[tone_ordering] if isinstance(tone_ordering, str) else list(tone_ordering)
    else:
        order = cadence_type_order
    if cads.empty:
        raise ValueError('No cadences to plot.')

    categories = [c for c in _ordered_with_extras(order, cads[by]) if c in set(cads[by])]
    groups = list(dict.fromkeys(cads[groupby_column]))
    counts = cads.groupby([groupby_column, by]).size().rename('Count')
    full = pd.MultiIndex.from_product([groups, categories], names=[groupby_column, by])
    counts = counts.reindex(full, fill_value=0).reset_index()
    counts['Percentage'] = (counts['Count'] / counts.groupby(groupby_column)['Count'].transform('sum') * 100).round(1)
    y = 'Percentage' if percent else 'Count'

    single = len(groups) == 1
    label = _single_piece_label(cadences) if groupby_column == 'Title' else None
    if single and by == 'CadType':
        # one piece: color each bar by cadence type, as in cadence_progress
        fig = px.bar(counts, x=by, y=y, color=by, hover_data=['Count', 'Percentage'],
                     color_discrete_map=cadence_type_colors,
                     category_orders={by: categories})
    else:
        fig = px.bar(counts, x=by, y=y, color=groupby_column, barmode='group',
                     hover_data=['Count', 'Percentage'],
                     color_discrete_sequence=contrasting_colors,
                     category_orders={by: categories, groupby_column: groups})

    what = 'Cadence Types' if by == 'CadType' else 'Cadence Tones'
    if chart_title is None:
        chart_title = what + (f' in {label}' if label and single else f' by {groupby_column}')
    chart_title = _settings_title(chart_title, [
        'percent of each group\'s cadences' if percent else 'number of cadences',
        f'{len(cads)} cadences',
        (f'tone order: {tone_ordering}' if isinstance(tone_ordering, str) else 'custom tone order')
        if by == 'Tone' else None,
        _n_pieces(cadences)])
    fig.update_layout(title=chart_title, width=1000, height=550,
                      xaxis_title='Cadence Type' if by == 'CadType' else 'Tone',
                      yaxis_title='Percent of cadences' if percent else 'Number of cadences',
                      legend_title=groupby_column, showlegend=not single, bargap=0.2)
    if percent:
        fig.update_yaxes(ticksuffix='%')
    fig.update_xaxes(tickangle=-30 if by == 'CadType' else 0)
    return fig


def radar_note_plot(weighted_notes_df, pitch_class_order='Fifths', exclude_rests=True,
                    limit_to_active=True, color_grouping='title', chart_title=None):
    """
    Radar plot of how much of each piece's time is spent on each pitch class
    (duration-weighted), one polygon per piece (or per composer, final, ...).

    Works with `piece.note_weights()` or `corpus.note_weights()`.

    Parameters
    ----------
    weighted_notes_df : pandas.DataFrame
        Output of ImportedPiece.note_weights or CorpusBase.note_weights
        (columns 'pitch_class', 'count', 'scaled', 'composer', 'title', ...).
    pitch_class_order : str or list, optional (default 'Fifths')
        Order of pitch classes around the circle: 'Fifths', 'Diatonic',
        'Chromatic' (see `sorting_lists.note_pitch_class_orders`), or your own
        list (music21 spelling, e.g. 'B-'). Pitch classes in the data but not
        in the order are added at the end.
    exclude_rests : bool, optional (default True)
        Leave out 'Rest' and show each pitch class as a share of sounding time.
    limit_to_active : bool, optional (default True)
        If True, show only pitch classes that occur in the data. If False, show
        every pitch class in the ordering.
    color_grouping : str, optional (default 'title')
        One polygon per value of this column, e.g. 'title', 'composer' or
        'final'. Durations are summed within each group.
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> radar_note_plot(piece.note_weights()).show()
    >>> radar_note_plot(corpus.note_weights(include_final=True), color_grouping='final')
    """
    df = weighted_notes_df.copy()
    df['pitch_class'] = df['pitch_class'].astype(str)
    if color_grouping not in df.columns:
        # accept 'Title' for 'title', etc. (note_weights uses lower-case names)
        matches = [c for c in df.columns if c.lower() == color_grouping.lower()]
        if not matches:
            raise ValueError(f"No '{color_grouping}' column; choose one of {list(df.columns)}")
        color_grouping = matches[0]
    if exclude_rests:
        df = df[df['pitch_class'] != 'Rest']
    df = df[df['count'] > 0]
    if df.empty:
        raise ValueError('No notes to plot.')

    order = (note_pitch_class_orders[pitch_class_order] if isinstance(pitch_class_order, str)
             else list(pitch_class_order))
    if not exclude_rests:
        order = order + ['Rest']
    pcs = _ordered_with_extras(order, df['pitch_class'])
    if limit_to_active:
        pcs = [p for p in pcs if p in set(df['pitch_class'])]
    groups = list(dict.fromkeys(df[color_grouping]))

    # sum durations per group and pitch class, fill gaps with 0 so every
    # polygon is complete, then take percentages within each group
    grouped = df.groupby([color_grouping, 'pitch_class'])['count'].sum()
    full = pd.MultiIndex.from_product([groups, pcs], names=[color_grouping, 'pitch_class'])
    grouped = grouped.reindex(full, fill_value=0).reset_index()
    totals = grouped.groupby(color_grouping)['count'].transform('sum')
    grouped['Percentage'] = (grouped['count'] / totals * 100).round(1)

    if chart_title is None:
        label = _piece_label(df, title_col='title', composer_col='composer')
        chart_title = f'Weighted Pitch Classes in {label}' if label else 'Weighted Pitch Classes'
    chart_title = _settings_title(chart_title, [
        (f'pitch-class order: {pitch_class_order}' if isinstance(pitch_class_order, str)
         else 'custom pitch-class order'),
        'rests excluded' if exclude_rests else 'rests included',
        'all pitch classes' if not limit_to_active else None,
        f'grouped by {color_grouping}' if color_grouping.lower() != 'title' else None,
        _n_pieces(df, title_col='title')])

    fig = px.line_polar(grouped, r='Percentage', theta='pitch_class', line_close=True,
                        color=color_grouping, markers=True,
                        hover_data={'count': ':.1f'},
                        labels={'pitch_class': 'Pitch class', 'count': 'Duration (quarter notes)'},
                        color_discrete_sequence=contrasting_colors,
                        category_orders={'pitch_class': pcs, color_grouping: groups})
    fig.update_traces(fill='toself', line=dict(width=2), opacity=0.8)
    fig.update_layout(
        width=800, height=650,
        legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5,
                    title=dict(text=color_grouping.capitalize(), side='top', font_size=12),
                    bordercolor='black', borderwidth=1, bgcolor='rgba(255,255,255,0.8)'),
        title=dict(text=chart_title, x=0.5),
        polar=dict(radialaxis=dict(visible=True, ticksuffix='%')),
        margin=dict(b=150, t=130),
        showlegend=len(groups) > 1)
    return fig


def voice_range_chart(voice_ranges_df, final=None, piece_order='mass', sort_voice='2', title=None):
    """
    Plot voice ranges (from `piece.voice_ranges()` or `corpus.voice_ranges()`)
    as horizontal bars, one row per piece and voice, with dotted reference
    lines at the modally significant pitches for the final.

    Parameters
    ----------
    voice_ranges_df : pandas.DataFrame
        Output of ImportedPiece.voice_ranges or CorpusBase.voice_ranges.
    final : str, optional
        Plot only pieces with this final. If omitted and the data contain a
        single final, that final's reference lines are drawn; if they contain
        several, no reference lines are drawn.
    piece_order : str or list, optional (default 'mass')
        How to order the pieces (top to bottom). Voices within each piece
        are always shown from highest staff (V1) down.

        * 'mass': models (titles without a Mass movement name) first, then
          Mass movements in liturgical order (Kyrie, Gloria, Credo, Sanctus,
          Agnus Dei); within each group, by `sort_voice`'s lowest note.
        * 'range': by `sort_voice`'s lowest note only, with no model/Mass
          grouping. Useful for pieces not related as model and Mass.
        * 'alpha': alphabetically by title.
        * 'given': the order in which titles first appear in `voice_ranges_df`,
          so you can sort the DataFrame yourself (e.g. by date or composer).
        * a list of titles: exactly that order. Titles not in the list are
          added at the end, in 'given' order, with a printed note.
    sort_voice : str, optional (default '2')
        The voice whose lowest note orders pieces for 'mass' and 'range'.
        Pieces without this voice fall back to their overall lowest note.
    title : str, optional
        Chart title. A default naming the final is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure
        Call `.show()` to display it, or `.write_html(path)` to save it.

    Examples
    --------
    ```python
    voice_ranges_df = corpus.voice_ranges(top_n=7)
    fig = voice_range_chart(voice_ranges_df, final='G')
    fig.show()

    # unrelated pieces, ordered by date (sort the DataFrame first)
    # note you will need dates_df produced separately!
    voice_ranges_df = voice_ranges_df.merge(dates_df, on='Title').sort_values('Date')
    voice_range_chart(voice_ranges_df, piece_order='given').show()

    # a custom order
    voice_range_chart(voice_ranges_df, piece_order=['Veni speciosam', 'Je suis déshéritée'])
    ```
    """
    df = voice_ranges_df.copy()
    if 'Title' not in df.columns:
        df['Title'] = ''
    df['Title'] = df['Title'].astype(str)
    df['Voice'] = df['Voice'].astype(str)
    if final is not None:
        df = df[df['Final'] == final]
    if df.empty:
        raise ValueError('No voice ranges to plot (check the `final` filter).')

    def ps(n):
        return m21_pitch.Pitch(n).ps

    df['Low_ps'] = df['LowestNote'].map(ps)
    df['Span'] = df['HighestNote'].map(ps) - df['Low_ps']

    def title_rank(t):
        # titles without a Mass movement name (e.g. models) sort first
        return next((i + 1 for i, m in enumerate(_MASS_MOVEMENTS) if m in t), 0)

    def anchor_low(t):
        rows = df[df['Title'] == t]
        anchor = rows[rows['Voice'] == str(sort_voice)]
        return (anchor if len(anchor) else rows)['Low_ps'].min()

    given = list(dict.fromkeys(df['Title']))      # first-appearance order
    if isinstance(piece_order, (list, tuple)):
        custom = [str(t) for t in piece_order]
        unknown = [t for t in custom if t not in given]
        if unknown:
            print('piece_order titles not in the data (ignored): {}'.format(', '.join(unknown)))
        rest = [t for t in given if t not in custom]
        if rest:
            print('Titles not in piece_order, added at the end: {}'.format(', '.join(rest)))
        titles = [t for t in custom if t in given] + rest
    elif piece_order == 'mass':
        titles = sorted(given, key=lambda t: (title_rank(t), anchor_low(t)))
    elif piece_order == 'range':
        titles = sorted(given, key=anchor_low)
    elif piece_order == 'alpha':
        titles = sorted(given)
    elif piece_order == 'given':
        titles = given
    else:
        raise ValueError("piece_order must be 'mass', 'range', 'alpha', 'given', or a list of titles.")

    def voice_key(v):
        return (0, int(v), v) if v.isdigit() else (1, 0, v)

    df['Title_Voice'] = (df['Title'] + '  [V' + df['Voice'] + ']').str.strip()
    labels = []
    for t in titles:
        for v in sorted(df.loc[df['Title'] == t, 'Voice'].unique(), key=voice_key):
            labels.append(f'{t}  [V{v}]'.strip())

    voices = sorted(df['Voice'].unique(), key=voice_key)
    palette = contrasting_colors
    fig = px.bar(df, x='Span', y='Title_Voice', base='Low_ps', orientation='h',
                 color='Voice', opacity=0.75,
                 color_discrete_map={v: palette[i % len(palette)] for i, v in enumerate(voices)},
                 category_orders={'Title_Voice': labels, 'Voice': voices},
                 hover_data={'Title': True, 'Voice': True, 'Range': True,
                             'Span': False, 'Low_ps': False, 'Title_Voice': False},
                 labels={'Title_Voice': 'Piece / Voice'})

    finals = df['Final'].dropna().unique() if 'Final' in df.columns else []
    the_final = finals[0] if len(finals) == 1 else None
    for point in _RANGE_REFERENCE_BY_FINAL.get(the_final, []):
        fig.add_vline(x=ps(point), line_dash='dot', line_color='gray', line_width=1,
                      annotation_text=point, annotation_position='top')

    lo = int(df['Low_ps'].min()) - 2
    hi = int((df['Low_ps'] + df['Span']).max()) + 2
    ticks = [p for p in range(lo, hi + 1) if m21_pitch.Pitch(ps=p).accidental is None]
    if title is None:
        title = (f'Voice Ranges in Pieces with Final {the_final}' if the_final
                 else 'Voice Ranges (several finals; filter by final for reference lines)')
    settings = [p for p in _data_settings(voice_ranges_df) if not p.startswith('final:')]
    title = _settings_title(title, settings + [
        f'final: {final}' if final is not None else None,
        {'mass': 'models, then Mass movements', 'range': 'pieces by range', 'alpha': 'pieces alphabetical',
         'given': 'pieces as given'}.get(piece_order, f'piece order: {piece_order}')
        if isinstance(piece_order, str) else 'custom piece order',
        _n_pieces(df)])
    fig.update_layout(
        title=title,
        xaxis=dict(title='Note Range', tickmode='array', tickvals=ticks,
                   ticktext=[m21_pitch.Pitch(ps=p).nameWithOctave for p in ticks],
                   tickangle=45),
        # set the order explicitly: px reverses category_orders for horizontal
        # bars, so combining it with autorange='reversed' alone would flip it
        yaxis=dict(title='', autorange='reversed',
                   categoryorder='array', categoryarray=labels),
        height=max(400, 28 * len(labels) + 180), width=1000,
        bargap=0.3, margin=dict(l=250, r=100, t=100, b=50))
    return fig


# melodic species visualizations

def _species_plot_df(species_df):
    """Drop (and report) intervals with no Octave species."""
    unmapped = species_df['Octave'].isna()
    if unmapped.any():
        print(f"Note: {unmapped.sum()} interval(s) have no Octave species and are not plotted:")
        print(species_df.loc[unmapped, 'Interval'].value_counts().to_string())
    df = species_df[~unmapped].copy()
    if df.empty:
        raise ValueError('No melodic species to plot.')
    df['Voice'] = df['Voice'].astype(str)
    return df


def plot_species(species_df, octave_order=species_octave_order, show_voice_detail=True,
                 progress_bins=5, chart_title=None):
    """
    Plot the octave species articulated by melodic leaps across the course of
    a piece (Progress 0 = start, 1 = end).

    Works with `piece.melodic_species()` or `corpus.melodic_species()`. For a
    corpus each piece gets its own row, since Progress is measured within each
    piece.

    Parameters
    ----------
    species_df : pandas.DataFrame
        Output of ImportedPiece.melodic_species or CorpusBase.melodic_species.
    octave_order : list of str, optional (default sorting_lists.species_octave_order)
        Bottom-to-top order of octave species on the y axis. Octaves found in
        the data but not in the list are added at the end.
    show_voice_detail : bool, optional (default True)
        True: one dot per interval, colored by voice. False: the piece is cut
        into `progress_bins` equal sections (e.g. 0–20%, 20–40%, ... of the
        piece) and each dot's size shows how many
        intervals articulate that octave in that section.
    progress_bins : int, optional (default 5)
        Number of sections when `show_voice_detail=False`.
    chart_title : str, optional
        A default naming the piece (for a single piece) is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> plot_species(piece.melodic_species()).show()
    >>> plot_species(corpus.melodic_species(), show_voice_detail=False).show()
    """
    df = _species_plot_df(species_df)
    octaves = [o for o in _ordered_with_extras(octave_order, df['Octave']) if o in set(df['Octave'])]
    n_titles = df['Title'].nunique() if 'Title' in df.columns else 1
    titles = list(dict.fromkeys(df['Title'])) if n_titles > 1 else []
    facet = dict(facet_row='Title' if n_titles > 1 else None,
                 facet_row_spacing=0.25 / n_titles if n_titles > 1 else None)

    if show_voice_detail:
        voices = sorted(df['Voice'].unique(), key=_voice_sort_key)
        hover = [c for c in ['Composer', 'Title', 'Measure', 'Beat', 'Interval', 'Species'] if c in df.columns]
        fig = px.scatter(df, x='Progress', y='Octave', color='Voice', hover_data=hover,
                         color_discrete_sequence=contrasting_colors,
                         category_orders={'Octave': octaves, 'Voice': voices, 'Title': titles},
                         **facet)
        fig.update_traces(marker=dict(size=12, opacity=0.8))
        fig.update_xaxes(range=[-0.02, 1.02])
        legend_title = 'Voice'
    else:
        # equal sections of the whole piece (0 to 1), labeled e.g. '0–20%'
        edges = np.linspace(0, 1, progress_bins + 1)
        sections = [f'{lo:.0%}–{hi:.0%}' for lo, hi in zip(edges[:-1], edges[1:])]
        df['Section'] = pd.cut(df['Progress'].clip(0, 1), bins=edges, labels=sections,
                               include_lowest=True)
        keys = (['Title'] if n_titles > 1 else []) + ['Section', 'Octave']
        counts = (df.groupby(keys, observed=True)
                    .agg(Count=('Interval', 'size'),
                         Intervals=('Interval', lambda s: ', '.join(sorted(s.unique()))),
                         Measures=('Measure', lambda s: ', '.join(str(int(m)) if float(m).is_integer() else str(m)
                                                                   for m in sorted(s.unique()))))
                    .reset_index())
        counts['Section'] = counts['Section'].astype(str)
        fig = px.scatter(counts, x='Section', y='Octave', size='Count', size_max=40,
                         hover_data=['Count', 'Intervals', 'Measures'],
                         color_discrete_sequence=contrasting_colors,
                         category_orders={'Octave': octaves, 'Section': sections, 'Title': titles},
                         **facet)
        fig.update_xaxes(categoryorder='array', categoryarray=sections, title_text=None)
        fig.update_layout(xaxis_title='Section of piece')   # bottom row only
        legend_title = None

    _category_yaxis(fig, octaves, title='Octave')
    if chart_title is None:
        label = _piece_label(df)
        chart_title = f'Melodic Species in {label}' if label else 'Melodic Species'
    chart_title = _settings_title(chart_title, _data_settings(species_df) + [
        'by voice' if show_voice_detail else f'{progress_bins} sections',
        f'{len(df)} leaps',
        _n_pieces(df)])
    fig.update_layout(title=chart_title, width=900, height=500, legend_title=legend_title)
    if n_titles > 1:
        fig.update_yaxes(title='')
        _facet_by_title(fig, n_titles, row_height=260)
    return fig


def plot_species_cadences(species_df, cadences_df, title=None, octave_order=species_octave_order,
                          chart_title=None):
    """
    Melodic species (colored by voice) and cadences (colored by cadence type)
    on a shared Progress axis, to compare where octave species and cadence
    tones fall in a piece.

    Each piece gets two stacked panels: species above, cadences below. With
    corpus results (several Titles) every piece is stacked in one tall
    figure, two rows per piece, unless `title` names just one of them. For a
    large corpus the figure gets long: pass `title=`, or filter the
    DataFrames first, to plot fewer pieces.

    Parameters
    ----------
    species_df : pandas.DataFrame
        Output of `piece.melodic_species()` or `corpus.melodic_species()`.
    cadences_df : pandas.DataFrame
        Output of `piece.cadences()` or `corpus.cadences()`.
    title : str, optional
        Plot only this piece, when the DataFrames hold several (corpus
        results). If omitted, every piece in `species_df` is plotted.
    octave_order : list of str, optional (default sorting_lists.species_octave_order)
        Bottom-to-top order of octave species in the species panels.
    chart_title : str, optional
        A default naming the piece (or 'Corpus') is used if omitted.

    Returns
    -------
    plotly.graph_objects.Figure

    Examples
    --------
    >>> plot_species_cadences(piece.melodic_species(), piece.cadences()).show()

    >>> species, cads = corpus.melodic_species(), corpus.cadences()
    >>> plot_species_cadences(species, cads).show()          # every piece, stacked
    >>> plot_species_cadences(species, cads, title=species['Title'].iloc[0]).show()
    """
    has_titles = 'Title' in species_df.columns and 'Title' in cadences_df.columns
    sp_all, cads_all = species_df, cadences_df
    if title is not None:
        if not has_titles:
            raise ValueError("title= needs a 'Title' column in both DataFrames.")
        sp_all = species_df[species_df['Title'] == title]
        cads_all = cadences_df[cadences_df['Title'] == title]
        if sp_all.empty:
            raise ValueError(f"No species_df rows for title {title!r}.")

    sp = _species_plot_df(sp_all)
    cads = cads_all.dropna(subset=['Tone'])

    # one (species, cadences) pair of rows per piece, in order of appearance
    if has_titles and sp['Title'].nunique() > 1:
        pieces = list(sp['Title'].dropna().unique())
        missing = set(cads['Title'].dropna()) - set(pieces)
        if missing:
            print('Titles with cadences but no species (not plotted): '
                  + ', '.join(map(repr, sorted(missing))))
        cads = cads[cads['Title'].isin(pieces)]
        parts = [(t, sp[sp['Title'] == t], cads[cads['Title'] == t]) for t in pieces]
    else:
        parts = [(None, sp, cads)]
    n = len(parts)

    # shared categories and colors, so every piece reads the same way
    octaves = [o for o in _ordered_with_extras(octave_order, sp['Octave']) if o in set(sp['Octave'])]
    tones = [t for t in _ordered_with_extras(cadence_progress_tone_order, cads['Tone']) if t in set(cads['Tone'])]
    voices = sorted(sp['Voice'].unique(), key=_voice_sort_key)
    voice_colors = {v: contrasting_colors[i % len(contrasting_colors)] for i, v in enumerate(voices)}
    cad_types = [c for c in _ordered_with_extras(cadence_type_order, cads['CadType']) if c in set(cads['CadType'])]

    if n == 1:
        subplot_titles = ('Melodic species by voice', 'Cadences by type')
    else:
        subplot_titles = []
        for t, sp_one, _ in parts:
            label = _single_piece_label(sp_one) or str(t)
            subplot_titles += [f'{label}: melodic species', f'{label}: cadences']
    fig = make_subplots(rows=2 * n, cols=1, vertical_spacing=min(0.1, 0.25 / n),
                        subplot_titles=subplot_titles)

    sp_hover = [c for c in ['Measure', 'Beat', 'Interval', 'Species'] if c in sp.columns]
    cad_hover = [c for c in ['Measure', 'Beat', 'CadType'] if c in cads.columns]
    shown = set()

    def _add(traces, row, kind, order, header, rank_base):
        # one legend entry per voice / cadence type (toggling it in every
        # piece), ranked so voices list first, then cadence types
        for trace in traces:
            key = (kind, trace.name)
            pos = order.index(trace.name) if trace.name in order else len(order)
            trace.update(legendgroup=f'{kind}:{trace.name}', showlegend=key not in shown,
                         legendrank=rank_base + pos)
            if key not in shown and pos == 0:
                trace.update(legendgrouptitle_text=header)
            shown.add(key)
            fig.add_trace(trace, row=row, col=1)

    for i, (_, sp_one, cads_one) in enumerate(parts):
        sp_row, cad_row = 2 * i + 1, 2 * i + 2
        fig_sp = px.scatter(sp_one, x='Progress', y='Octave', color='Voice', hover_data=sp_hover,
                            color_discrete_map=voice_colors,
                            category_orders={'Octave': octaves, 'Voice': voices})
        fig_sp.update_traces(marker=dict(size=11, opacity=0.8))
        _add(fig_sp.data, sp_row, 'voice', voices, 'Voice', 1)
        if not cads_one.empty:
            fig_cad = px.scatter(cads_one, x='Progress', y='Tone', color='CadType', hover_data=cad_hover,
                                 color_discrete_map=cadence_type_colors,
                                 category_orders={'Tone': tones, 'CadType': cad_types})
            fig_cad.update_traces(marker=dict(size=14, symbol='diamond', opacity=0.85,
                                              line=dict(width=1, color='white')))
            _add(fig_cad.data, cad_row, 'cadence', cad_types, 'Cadence Type', 1000)
        _category_yaxis(fig, octaves, title='Octave', row=sp_row, col=1)
        _category_yaxis(fig, tones, title='Tone', row=cad_row, col=1)
        fig.update_xaxes(title_text='Progress', row=cad_row, col=1)
    fig.update_xaxes(range=[-0.02, 1.02], matches='x')   # zoom all panels together
    fig.layout.xaxis.matches = None

    if chart_title is None:
        label = _piece_label(sp) or _piece_label(cads)
        chart_title = f'Melodic Species and Cadences in {label}' if label else 'Melodic Species and Cadences'
    chart_title = _settings_title(chart_title, _data_settings(species_df) + [
        f'{len(sp)} leaps', f'{len(cads)} cadences', _n_pieces(sp)])
    fig.update_layout(title=chart_title, height=700 if n == 1 else 150 + 560 * n, width=950,
                      legend=dict(x=1.02, y=1.0, xanchor='left', yanchor='top',
                                  groupclick='togglegroup', tracegroupgap=0),
                      margin=dict(r=220))
    return fig
