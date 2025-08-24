"""
This script contains the method
"""

import altair as alt
import pandas as pd
import re
import textdistance
import numpy as np 
from crim_intervals import ImportedPiece
import pandas as pd
import plotly.express as px

# from ipywidgets import interact, fixed
from pyvis.network import Network

import matplotlib as mplt # OY addition 6/12/24

class NgramColorManager:
    def __init__(self):
        self.color_map = {}  # Dictionary to store pattern -> color mappings
        
        # Use Matplotlib's qualitative colormaps
        self.qualitative_cmaps = ['tab10', 'tab20', 'Set1', 'Set2', 'Set3', 'Accent', 'Dark2', 'Paired']
    
    def generate_distinct_colors(self, n):
        """Generate n distinct colors using Matplotlib's qualitative colormaps"""
        colors = []
        
        # First try to use the most distinct colormap (tab10)
        cmap = mplt.cm.get_cmap('tab10')
        colors.extend([mplt.colors.to_hex(cmap(i)) for i in range(min(10, n))])
        
        # If we need more colors, use other qualitative colormaps
        if n > 10:
            remaining = n - 10
            for cmap_name in self.qualitative_cmaps[1:]:
                if len(colors) >= n:
                    break
                    
                cmap = mplt.cm.get_cmap(cmap_name)
                # Get the number of colors in this colormap
                if cmap_name == 'tab20':
                    cmap_colors = 20
                elif cmap_name in ['Set1', 'Set3']:
                    cmap_colors = 9
                elif cmap_name in ['Set2', 'Dark2', 'Accent']:
                    cmap_colors = 8
                elif cmap_name == 'Paired':
                    cmap_colors = 12
                else:
                    cmap_colors = 10
                
                # Add colors from this colormap
                for i in range(min(cmap_colors, remaining)):
                    color = mplt.colors.to_hex(cmap(i))
                    if color not in colors:  # Avoid duplicates
                        colors.append(color)
                
                remaining = n - len(colors)
        
        # If we still need more colors, use HSV space with golden ratio
        if len(colors) < n:
            remaining = n - len(colors)
            golden_ratio_conjugate = 0.618033988749895
            h = 0.1  # Starting hue
            
            for _ in range(remaining):
                h = (h + golden_ratio_conjugate) % 1.0
                s = 0.85  # High saturation for vibrant colors
                v = 0.95  # High value for brightness
                rgb = mplt.colors.hsv_to_rgb([h, s, v])
                colors.append(mplt.colors.to_hex(rgb))
        
        return colors[:n]
# 2024
    # def get_color_for_pattern(self, pattern):
    #     """Get a color for a pattern, creating a new one if it doesn't exist"""
    #     pattern_str = pattern
    #     if not isinstance(pattern, str):
    #         pattern_str = ", ".join(str(item) for item in pattern)
            
    #     if pattern_str not in self.color_map:
    #         # We'll assign colors in order as new patterns are encountered
    #         n = len(self.color_map) + 1
    #         colors = self.generate_distinct_colors(n)
    #         self.color_map[pattern_str] = colors[-1]
            
    #     return self.color_map[pattern_str]
    
    # def assign_colors_to_dataframe(self, df, pattern_column='pattern'):
    #     """Assign colors to a dataframe based on patterns"""
    #     # Check if dataframe is not empty
    #     if len(df) > 0:
    #         # Convert patterns to strings if they're not already
    #         if not isinstance(df[pattern_column].iloc[0], str):
    #             df = df.copy()
    #             df[pattern_column] = df[pattern_column].map(
    #                 lambda cell: ", ".join(str(item) for item in cell), 
    #                 na_action='ignore'
    #             )
            
    #         # Assign colors
    #         df['color'] = df[pattern_column].apply(self.get_color_for_pattern)
        
    #     return df

    # 2025
    def get_color_for_pattern(self, pattern):
        """Get a color for a pattern, creating a new one if it doesn't exist"""
        # Add this single line to handle NaN values
        if pd.isna(pattern):
            pattern = "Missing Pattern"
        
        pattern_str = pattern
        if not isinstance(pattern, str):
            pattern_str = ", ".join(str(item) for item in pattern)
        
        if pattern_str not in self.color_map:
            # We'll assign colors in order as new patterns are encountered
            n = len(self.color_map) + 1
            colors = self.generate_distinct_colors(n)
            self.color_map[pattern_str] = colors[-1]
        
        return self.color_map[pattern_str]

    def assign_colors_to_dataframe(self, df, pattern_column='pattern'):
        """Assign colors to a dataframe based on patterns"""
        # Check if dataframe is not empty
        if len(df) > 0:
            # Convert patterns to strings if they're not already
            if not isinstance(df[pattern_column].iloc[0], str):
                df = df.copy()
                # Replace the map with apply to handle NaN values properly
                df[pattern_column] = df[pattern_column].apply(
                    lambda cell: ", ".join(str(item) for item in cell) if pd.notna(cell) else "Missing Pattern"
                )
            
            # Assign colors
            df['color'] = df[pattern_column].apply(self.get_color_for_pattern)
        
        return df

# Create a global instance of the color manager
color_manager = NgramColorManager()


def create_bar_chart(variable, count, color, data, condition, *selectors):
    color_scale = alt.Scale(
        domain = data['pattern'].unique(),
        range = data['color'].unique()
    ) # OY addition 6/12/24

    observer_chart = alt.Chart(data).mark_bar().encode(
        x=variable,
        y=count,
        color=alt.Color('pattern:N', scale=color_scale, legend=alt.Legend(title='Pattern')), # OY change 6/12/24
        opacity=alt.condition(condition, alt.value(1), alt.value(0.2))
    ).add_params(
        *selectors
    )
    return observer_chart


def create_heatmap(x, x2, y, color, data, heat_map_width, heat_map_height, selector_condition, *selectors, tooltip):
    color_scale = alt.Scale(
        domain = data['pattern'].unique(),
        range = data['color'].unique()
    ) # OY addition 6/12/24

    heatmap = alt.Chart(data).mark_bar().encode(
        x=x,
        x2=x2,
        y=y,
        color=alt.Color('pattern:N', scale=color_scale, legend=alt.Legend(title='Pattern')), # OY change 6/12/24
        opacity=alt.condition(selector_condition, alt.value(1), alt.value(0.2)),
        tooltip=tooltip
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_params(
        *selectors
    )
    return heatmap


def _process_ngrams_df_helper(ngrams_df, main_col):
    """
    The output from the getNgram is usually a table with
    four voices and ngram of notes properties (duration or
    pitch). This method stack this property onto one column
    and mark which voices they are from.
    :param ngrams_df: direct output from getNgram with 1 columns
    for each voices and ngrams of notes' properties.
    :param main_col: the name of the property
    :return: a dataframe with ['start', main_col, 'voice'] as columns
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
    patterns. It could also filter out specific voices or patterns
    for the users to analyze.

    :param ngrams_df: dataframe we got from getNgram in crim-interval
    :param ngrams_duration: if not None, simply output the offsets of the
    ngrams. If we have durations, calculate the end by adding the offsets and
    the durations.
    :param selected_pattern: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :return a new, processed dataframe with only desired patterns from desired voices
    combined into one column with start and end points
    """

    ngrams_df = _process_ngrams_df_helper(ngrams_df, 'pattern')
    if ngrams_duration is not None:
        ngrams_duration = _process_ngrams_df_helper(ngrams_duration, 'duration')
        ngrams_df['end'] = ngrams_df['start'] + ngrams_duration['duration']
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

# OY addition - new function for generating distinct colors 6/12/24
def generate_distinct_colors(n):
    # Generate `n` distinct colors using the HSV color space
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.65  # Fixed saturation
        value = 0.9  # Fixed value
        color = mplt.colors.to_hex(mplt.colors.hsv_to_rgb((hue, saturation, value)))
        colors.append(color)
    return colors

# OY addition - new function for adding colors 6/12/24
# def ngrams_color_helper(new_processed_ngrams_df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Add a Series to the dataframe that assigns a unique hex color to each unique pattern
#     :param new_processed_ngrams_df: processed crim-intervals getNgram's output where tuples have been converted to strings
#     :return: a dataframe containing a new column with hex color values
#     """

#     # Calculate the number of unique values in 'pattern_str'
#     num_unique_values = new_processed_ngrams_df['pattern'].nunique() #  Function to count unique values in 'pattern_str' column
#     # # Generate enough hex colors
#     hex_colors = generate_distinct_colors(num_unique_values)   
#     # # Step 2: Assign colors to unique values
#     color_map = dict(zip(new_processed_ngrams_df['pattern'].unique(), hex_colors)) 
#     # # Add a new column 'color' to the DataFrame
#     new_processed_ngrams_df['color'] = new_processed_ngrams_df['pattern'].map(color_map)

#     return new_processed_ngrams_df

# def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300, includeCount=False):
#     """
#     Plot a heatmap for crim-intervals getNgram's processed output.
#     :param ngrams_df: processed crim-intervals getNgram's output.
#     :param selected_pattern: list of specific patterns the users want (optional)
#     :param voices: list of specific voices the users want (optional)
#     :param heatmap_width: the width of the final heatmap (optional)
#     :param heatmap_height: the height of the final heatmap (optional)
#     :return: a bar chart that displays the different patterns and their counts,
#     and a heatmap with the start offsets of chosen voices / patterns
#     """

#     processed_ngrams_df = processed_ngrams_df.dropna(how='any')
#     selector = alt.selection_point(fields=['pattern'])
#     y = alt.Y("voice", sort=None)

#     # make a copy of the processed n_grams and turn them into Strings
#     new_processed_ngrams_df = processed_ngrams_df.copy()
#     new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(lambda cell: ", ".join(str(item) for item in cell), na_action='ignore')

#     new_processed_ngrams_df = ngrams_color_helper(new_processed_ngrams_df) # OY addition 6/12/24
    
#     heatmap = create_heatmap('start', 'end', y, 'pattern', new_processed_ngrams_df, heatmap_width, heatmap_height,
#                              selector, selector, tooltip=['start', 'end', 'pattern'])
#     if includeCount:
#         variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
#         patterns_bar = create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)
#         return alt.vconcat(patterns_bar, heatmap)
#     else:
#         return heatmap

# Modified version of your ngrams_color_helper function
def ngrams_color_helper(new_processed_ngrams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a Series to the dataframe that assigns a unique hex color to each unique pattern
    using the global color manager to ensure consistency across plots.
    
    :param new_processed_ngrams_df: processed crim-intervals getNgram's output where tuples have been converted to strings
    :return: a dataframe containing a new column with hex color values
    """
    return color_manager.assign_colors_to_dataframe(new_processed_ngrams_df)

# 2024 version.  To not edit!
# def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300, includeCount=False, title=None):
#     """
#     Plot a heatmap for crim-intervals getNgram's processed output.
#     :param ngrams_df: processed crim-intervals getNgram's output.
#     :param selected_pattern: list of specific patterns the users want (optional)
#     :param voices: list of specific voices the users want (optional)
#     :param heatmap_width: the width of the final heatmap (optional)
#     :param heatmap_height: the height of the final heatmap (optional)
#     :param includeCount: whether to include count bar chart (optional)
#     :param title: title for the chart, defaults to None (optional)
#     :return: a bar chart that displays the different patterns and their counts,
#     and a heatmap with the start offsets of chosen voices / patterns
#     """
#     processed_ngrams_df = processed_ngrams_df.dropna(how='any')
#     selector = alt.selection_point(fields=['pattern'])
#     y = alt.Y("voice", sort=None)

#     # make a copy of the processed n_grams and turn them into Strings
#     new_processed_ngrams_df = processed_ngrams_df.copy()
#     new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
#         lambda cell: ", ".join(str(item) for item in cell), 
#         na_action='ignore'
#     )

#     # Use the color manager to assign consistent colors
#     new_processed_ngrams_df = ngrams_color_helper(new_processed_ngrams_df)
    
#     heatmap = create_heatmap('start', 'end', y, 'pattern', new_processed_ngrams_df, heatmap_width, heatmap_height,
#                              selector, selector, tooltip=['start', 'end', 'pattern'])
    
#     if includeCount:
#         variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
#         patterns_bar = create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)
#         chart = alt.vconcat(patterns_bar, heatmap)
#     else:
#         chart = heatmap
    
#     # Apply title if provided
#     if title is not None:
#         chart = chart.properties(title=title)
    
#     return chart

# def plot_ngrams_heatmap(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], heatmap_width=800,
#                         heatmap_height=300, includeCount=False, title=None):
#     """
#     Plot a heatmap for crim-intervals getNgram's output.
#     :param ngrams_df: crim-intervals getNgram's output
#     :param ngrams_duration: if not None, rely on durations in the
#     df to calculate the durations of the ngrams.
#     :param selected_patterns: list of specific patterns the users want (optional)
#     :param voices: list of specific voices the users want (optional)
#     :param heatmap_width: the width of the final heatmap (optional)
#     :param heatmap_height: the height of the final heatmap (optional)
#     :param includeCount: whether to include count bar chart (optional)
#     :param title: title for the chart, defaults to None (optional)
#     :return: a bar chart that displays the different patterns and their counts,
#     and a heatmap with the start offsets of chosen voices / patterns
#     """
#     processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
#                                             selected_pattern=selected_patterns,
#                                             voices=voices)
#     return _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=heatmap_width, 
#                                    heatmap_height=heatmap_height, includeCount=includeCount, title=title)


# 2025 with compare mode for color matching

def plot_ngrams_heatmap(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], compare_mode=False, heatmap_width=800, heatmap_height=300, includeCount=False, title=None):
    """
    Plot a heatmap for crim-intervals getNgram's output.
    :param ngrams_df: crim-intervals getNgram's output
    :param ngrams_duration: if not None, rely on durations in the
    df to calculate the durations of the ngrams.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param compare_mode: whether to compare two dataframes (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :param includeCount: whether to include count bar chart (optional)
    :param title: title for the chart, defaults to None (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
                                            selected_pattern=selected_patterns,
                                            voices=voices)
    
    return _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=heatmap_width, 
                                   heatmap_height=heatmap_height, includeCount=includeCount, title=title, compare_mode=compare_mode)

def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300, includeCount=False, title=None, compare_mode=False):
    """
    Plot a heatmap for crim-intervals getNgram's processed output.
    :param processed_ngrams_df: processed crim-intervals getNgram's output
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :param includeCount: whether to include count bar chart (optional)
    :param title: title for the chart, defaults to None (optional)
    :param compare_mode: whether to compare two dataframes (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """
    # Convert tuples to strings FIRST, before any other processing
    processed_ngrams_df = processed_ngrams_df.copy()
    processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
        lambda cell: ", ".join(map(str, cell)) if isinstance(cell, (tuple, list)) else str(cell),
        na_action='ignore'
    )
    
    color_manager = NgramColorManager()
    processed_ngrams_df = color_manager.assign_colors_to_dataframe(processed_ngrams_df)
    
    if compare_mode:
        # Handle comparison mode - also convert tuples to strings here
        if processed_ngrams_df is not None:
            processed_ngrams_df = processed_ngrams_df.copy()
            processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
                lambda cell: ", ".join(map(str, cell)) if isinstance(cell, (tuple, list)) else str(cell),
                na_action='ignore'
            )
            processed_ngrams_df = color_manager.assign_colors_to_dataframe(processed_ngrams_df)
        
        # Find shared patterns between both dataframes (now using string patterns)
        shared_patterns = set(processed_ngrams_df['pattern']).intersection(
            set(processed_ngrams_df['pattern']) if processed_ngrams_df is not None else set()
        )
        
        # Update colors for shared patterns
        for pattern in shared_patterns:
            processed_ngrams_df.loc[processed_ngrams_df['pattern'] == pattern, 'color'] = color_manager.get_color_for_pattern(pattern)
            if processed_ngrams_df is not None:
                processed_ngrams_df.loc[processed_ngrams_df['pattern'] == pattern, 'color'] = color_manager.get_color_for_pattern(pattern)
    
    # Sort by id
    # processed_ngrams_df = processed_ngrams_df.sort_values(by='id')
    # if compare_mode and processed_ngrams_duration_df is not None:
    #     processed_ngrams_duration_df = processed_ngrams_duration_df.sort_values(by='id')
    
    selector = alt.selection_point(fields=['pattern'])
    y = alt.Y("voice", sort=None)
    
    # No need to create a new dataframe and convert again - already done above
    heatmap = create_heatmap('start', 'end', y, 'color', processed_ngrams_df, heatmap_width, heatmap_height,
                            selector, selector, tooltip=['start', 'end', 'pattern'])
    
    if includeCount:
        variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
        patterns_bar = create_bar_chart(variable, 'count(pattern)', 'pattern', processed_ngrams_df, selector, selector)
        chart = alt.vconcat(patterns_bar, heatmap)
    else:
        chart = heatmap
    
    # Apply title if provided
    if title is not None:
        chart = chart.properties(title=title)
    
    return chart

def plot_ngrams_barchart(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], chart_width=800,
                        chart_height=300):
    """
    Plot a bar chart for crim-intervals getNgram's output.
    :param ngrams_df: crim-intervals getNgram's output
    :param ngrams_duration: if not None, rely on durations in the
    df to calculate the durations of the ngrams.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param chart_width: the width of the final bar chart (optional)
    :param chart_height: the height of the final bar chart (optional)
    :return: a bar chart that displays the different patterns and their counts
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration,
                                            selected_pattern=selected_patterns,
                                            voices=voices)
    return _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=chart_width, chart_height=chart_height)

# 2024 version
# def _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=800, chart_height=300):
#     """
#     Plot a bar chart for crim-intervals getNgram's processed output.
#     :param ngrams_df: processed crim-intervals getNgram's output.
#     :param selected_pattern: list of specific patterns the users want (optional)
#     :param voices: list of specific voices the users want (optional)
#     :param chart_width: the width of the final bar chart (optional)
#     :param chart_height: the height of the final bar chart (optional)
#     :return: a bar chart that displays the different patterns and their counts
#     """

#     processed_ngrams_df = processed_ngrams_df.dropna(how='any')
#     selector = alt.selection_point(fields=['pattern'])
#     y = alt.Y("voice", sort=None)

#     # make a copy of the processed n_grams and turn them into Strings
#     new_processed_ngrams_df = processed_ngrams_df.copy()
#     new_processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(lambda cell: ", ".join(str(item) for item in cell), na_action='ignore')

#     variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
#     return create_bar_chart(variable, 'count(pattern)', 'pattern', new_processed_ngrams_df, selector, selector)

# 2025

def _plot_ngrams_df_barchart(processed_ngrams_df, chart_width=800, chart_height=300):
    """
    Plot a bar chart for crim-intervals getNgram's processed output.
    :param processed_ngrams_df: processed crim-intervals getNgram's output.
    :param chart_width: the width of the final bar chart (optional)
    :param chart_height: the height of the final bar chart (optional)
    :return: a bar chart that displays the different patterns and their counts
    """
    processed_ngrams_df = processed_ngrams_df.dropna(how='any').copy()
    
    # Convert ngrams to strings - improved version with type checking
    processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(
        lambda cell: ", ".join(map(str, cell)) if isinstance(cell, (tuple, list)) else str(cell), 
        na_action='ignore'
    )
    
    selector = alt.selection_point(fields=['pattern'])
    y = alt.Y("voice", sort=None)
    variable = alt.X('pattern', axis=alt.Axis(labelAngle=-45))
    
    return create_bar_chart(variable, 'count(pattern)', 'pattern', processed_ngrams_df, selector, selector)
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
                             heatmap_width=800, heatmap_height=300):
    """
    Plot how closely the other vectors match a selected vector.
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

    return create_heatmap('start', 'end', y, 'score', score_ngrams, heatmap_width, heatmap_height,
                          alt.datum.score > selector.cutoff, selector, tooltip=['start', 'end', 'pattern', 'score'])


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

# uses INTERACT, and so removed 2024
# def create_interactive_compare_df(df, interval_column):
#     """
#     This method returns a wdiget allowing users to interact with
#     the simple observations dataframe.
#     :param df: the dataframe the user interact with
#     :param interval_column: the column of intervals
#     :return: a widget that filters and colors a dataframe based on the users
#     search pattern.
#     """
#     return interact(_manipulate_processed_network_df, df=fixed(df),
#                     interval_column=fixed(interval_column), search_pattern_starts_with='Input search pattern')


# def create_comparisons_networks_and_interactive_df(df, interval_column, interval_type, ema_column, patterns=[]):
#     """
#     Generate a dictionary of networks and a simple dataframe allowing the users
#     search through the intervals.
#     :param df: the dataframe the user interact with
#     :param interval_column: the column of intervals
#     :param interval_type: put "time" or "melodic"
#     :param ema_column: column containing ema address
#     :param patterns: we could only choose to look at specific patterns (optional)
#     :return: a dictionary of networks created and a clean interactive df
#     """
#     # process df
#     if patterns:
#         df = df[df[interval_column].isin(patterns)].copy()

#     networks_dict = create_interval_networks(df[interval_column], interval_type)
#     df = process_network_df(df, interval_column, ema_column)
#     return networks_dict, create_interactive_compare_df(df, interval_column)

# new cadence visualization functions


# cadence radar
def cadence_radar(cadences, groupby_column='Title', chart_title="Radar Plot of Cadence Tones"):
    """
    Create a radar plot showing distribution of cadence tones.
    The optional chart_title parameter allows for a custom title.

    Cadences df must contain 'Composer', 'Title' and 'Tone' columns.  Groupby colum

    Parameters:
    -----------
    cadences : pd.DataFrame
        DataFrame containing cadence data

    groupby_column : str
        Column name to group by (default is 'Title'); could also be 'Composer'
    chart_title : str
        Title for the chart (default is "Radar Plot of Cadence Tones")  



    Returns:
    --------
    fig : go.Figure
        Plotly Figure object representing the radar plot

    Notes:
    ------
    This function creates a radar plot to visualize the relative distribution of cadence tones across different titles in the corpus.
    It uses Plotly Express to generate the plot and applies various customizations such as color mapping, legend positioning, and layout adjustments.
    The plot displays the percentage of occurrence for each tone within each title, allowing for easy comparison between titles and tones.
    """
    # Define constants at function scope
    tone_order = {'C': 0, 'D': 1, 'E-': 2, 'E': 3, 'F': 4,
        'G': 5, 'A': 6, 'B-': 7
    }

    
    # Vectorized approach using groupby operations
    grouped = cadences.groupby([groupby_column, 'Tone']).size().reset_index(name='count')
    
    # Calculate percentages efficiently
    title_sums = grouped.groupby(groupby_column)['count'].sum()
    grouped['Percentage'] = (grouped['count'] / grouped[groupby_column].map(title_sums)) * 100
    
    # Create radar plot
    fig = px.line_polar(
        grouped[grouped['count'] > 0],
        r='Percentage',
        theta='Tone',
        line_close=True,
        color=groupby_column,
        markers=True,
        category_orders={'Tone': sorted(tone_order.keys(), key=lambda x: tone_order[x])}
    )
    
    # Apply optimizations
    fig.update_traces(fill='toself', line=dict(width=2))
    
    # Update layout with bottom legend
    fig.update_layout(
        width=800,
        height=600,
        legend=dict(
            orientation="h",  # Horizontal layout for better space usage
            yanchor="bottom",
            y=-0.4,           # Position below plot
            xanchor="center",
            x=0.5,            # Center horizontally
            xref="container", # Scale with container
            yref="container", # Scale with container
            title=dict(
                text=groupby_column,
                side="top",
                font_size=12
            ),
            itemsizing='constant',
            itemwidth=30,
            bordercolor="black",
            borderwidth=1,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        title=dict(text=chart_title, x=0.5),
        polar=dict(
            radialaxis=dict(visible=True, title='Percentage')
        ),
        margin=dict(b=120)  # Bottom margin for legend
    )
    
    return fig



# cadence progress viz
def cadence_progress(cadences, chart_title="Radar Plot of Cadence Tones"):
    """
    Create a scatter plot showing progress of cadences in a composition.
    Cadence df must contain 'Composer', 'Title', 'Progress', 'Tone', and 'CadType' columns.

    Parameters:
    -----------
    cadences : pd.DataFrame
        DataFrame containing cadence data
    chart_title : str
        Title for the chart (default is "Radar Plot of Cadence Tones")

    Returns:
    --------
    fig : go.Figure
        Plotly Figure object representing the scatter plot

    Notes:
    ------
    This function generates a scatter plot to visualize the progression of cadences in a specific composition.
    It categorizes cadences based on their type and assigns distinct colors to each cadence type.
    The plot displays the cadence progression along the x-axis and the tone along the y-axis, allowing for easy identification of cadence changes throughout the composition.
    Custom color mappings are used to differentiate between original and modified cadence types.
    The plot includes a horizontal legend for easy identification of cadence types.
    """
    # Define custom ordering for CadTypes
    custom_order = ['Authentic', 'Evaded Authentic', 
        'Clausula Vera', 'Evaded Clausula Vera', 'Abandoned Clausula Vera', 'Phrygian Clausula Vera',
        'Double Leading Tone', 'Evaded Double Leading Tone', 'Abandoned Double Leading Tone',
        'Altizans Only', 'Phrygian Altizans', 'Evaded Altizans Only',
        'Phrygian', 'Reinterpreted', 'Quince', 'Leaping Contratenor']

    # order for y axis tones:
    custom_tone_order = ['E-', 'B-', 'F', 'C', 'G', 'D', 'A', 'E', 'B']  

    # color map for cadences--the evaded types are less saturated than corresponding regular types
    color_mapping = {'Authentic': '#FF0000',
     'Clausula Vera': '#0000FF',
     'Double Leading Tone': '#00FF00',
     'Altizans Only': '#800080',
     'Phrygian': '#00FF00',
     'Reinterpreted': '#00FFFF',
     'Quince': '#4B0082',
     'Leaping Contratenor': '#000000',
     'Phrygian Clausula Vera': '#FF00FF',
     'Evaded Authentic': '#FF6666',
     'Evaded Clausula Vera': '#6666FF',
     'Evaded Double Leading Tone': '#66FF66',
     'Evaded Altizans Only': '#CC99CC',
     'Evaded Phrygian': '#66FF66',
     'Evaded Reinterpreted': '#99FFFF',
     'Evaded Quince': '#9966CC',
     'Evaded Phrygian Clausula Vera': '#FF66FF',
     'Abandoned Clausula Vera': '#CCCCFF',
     'Abandoned Double Leading Tone': '#CCFFCC',
     'Abandoned Phrygian': '#FFE5CC',
     'Abandoned Authentic': '#FFCCCC',
     'Abandoned Phrygian Clausula Vera': '#FFCCFF'}
    
    composer = cadences['Composer'].iloc[0]
    title = cadences['Title'].iloc[0]

    # Ensure the Tone column is categorical with correct ordering
    cadences['Tone'] = pd.Categorical(
        cadences['Tone'],
        categories=custom_tone_order,  # specify tone order for y axis
        ordered=True
    )
    
    # Create figure with explicit category ordering
    fig = px.scatter(
        cadences,
        x='Progress',
        y='Tone',
        color='CadType',
        color_discrete_map=color_mapping, # use color mapping from above
        category_orders={'Tone': custom_tone_order}
    )
    
    # Configure Y-axis to show E- at bottom
    fig.update_layout(
        yaxis=dict(
            categoryorder='array',
            categoryarray=custom_tone_order,  # specify tone order for y axis
            autorange=True,
            fixedrange=True,
            scaleanchor='y',
            scaleratio=1,
            showgrid=True,
            showticklabels=True
        ),
        yaxis_range=[None, None]  # Allow Plotly to determine range
    )
    
    # Update marker properties
    fig.update_traces(marker=dict(size=25))
    
    # Customize layout
    fig.update_layout(
        title=f'Progress of Cadences in {composer}: {title}',
        legend=dict(
            title_text="Cadence Type",
        orientation="v"
        )
    )
    
    return fig
