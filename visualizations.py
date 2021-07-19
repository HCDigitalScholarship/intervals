"""
This script contains the method
"""

import altair as alt
import pandas as pd
import re
import textdistance

from fractions import Fraction
from ipywidgets import interact, fixed
from pyvis.network import Network

# pre-assigned relationship weights for different type of relationships
RELATIONSHIP_WEIGHTS = {
        'Quotation':1,
        'Mechanical transformation':2,
        'Non-mechanical transformation':3,
        'New material':4,
        'Omission':5,
        'Quotation, Mechanical transformation':6,
        'Quotation, Non-mechanical transformation':7,
        'Non-mechanical transformation, Omission':8,
        'Mechanical transformation, Non-mechanical transformation':9,
        'Quotation, New material':10,
        'Quotation, Mechanical transformation, Non-mechanical transformation':11
        }

def create_bar_chart(variable, count, color, data, condition, *selectors):
    # if type(data.iloc[0, :][variable]) != str:
    #     raise Exception("Label difficult to see!")

    observer_chart = alt.Chart(data).mark_bar().encode(
        y=variable,
        x=count,
        color = color,    
        opacity=alt.condition(condition, alt.value(1), alt.value(0.2))
    ).add_selection(
        *selectors
    )
    return observer_chart


def create_heatmap(x, x2, y, color, data, heat_map_width, heat_map_height, selector_condition, *selectors, tooltip):

    # if type(data.iloc[0, :][y]) != str:
    #     raise Exception("Label difficult to see!")

    heatmap = alt.Chart(data).mark_bar().encode(
        x=x,
        x2=x2,
        y=y,
        color=color, 
        opacity=alt.condition(selector_condition, alt.value(1), alt.value(0.2)),
        tooltip=tooltip
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_selection(
        *selectors
    ).interactive()

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

def _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=800, heatmap_height=300):
    """
    Plot a heatmap for crim-intervals getNgram's processed output.
    :param ngrams_df: processed crim-intervals getNgram's output.
    :param selected_pattern: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """

    processed_ngrams_df = processed_ngrams_df.dropna(how='any')
    
    selector = alt.selection_multi(fields=['pattern'])

    # # turns patterns into string to make it easier to see
    # processed_ngrams_df['pattern'] = processed_ngrams_df['pattern'].map(lambda cell: ", ".join(str(item) for item in cell), na_action='ignore').copy()

    patterns_bar = create_bar_chart('pattern', 'count(pattern)', 'pattern', processed_ngrams_df, selector, selector)
    heatmap = create_heatmap('start', 'end', 'voice', 'pattern', processed_ngrams_df, heatmap_width, heatmap_height,
                             selector, selector, tooltip=['start', 'end', 'pattern'])
    return alt.vconcat(patterns_bar, heatmap)

def plot_ngrams_heatmap(ngrams_df, ngrams_duration=None, selected_patterns=[], voices=[], heatmap_width=800,
                        heatmap_height=300):
    """
    Plot a heatmap for crim-intervals getNgram's output.
    :param ngrams_df: crim-intervals getNgram's output
    :param ngrams_duration: if not None, rely on durations in the
    df to calculate the durations of the ngrams.
    :param selected_patterns: list of specific patterns the users want (optional)
    :param voices: list of specific voices the users want (optional)
    :param heatmap_width: the width of the final heatmap (optional)
    :param heatmap_height: the height of the final heatmap (optional)
    :return: a bar chart that displays the different patterns and their counts,
    and a heatmap with the start offsets of chosen voices / patterns
    """
    processed_ngrams_df = process_ngrams_df(ngrams_df, ngrams_duration=ngrams_duration, selected_pattern=selected_patterns,
                                            voices=voices)
    return _plot_ngrams_df_heatmap(processed_ngrams_df, heatmap_width=heatmap_width, heatmap_height=heatmap_height)

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
    df = df.explode('locations', ignore_index=True)
    df[['start', 'end']] = df['locations'].str.split("-", expand=True).fillna(method='ffill')
    # print(df['start'].to_dict())
    # print(df['end'].to_dict())

    for index in df['start'].index:
        try:
            float(df['start'].loc[index])
        except:
            print(str(index) + ":" + df['start'].loc[index]+".")

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

    df = _from_ema_to_offsets(df, ema_col)
    df['website_url'] = _process_crim_json_url(df['url'])

    df['id'] = df['id'].astype(str)

    # because altair doesn't work when the categories' names have periods,
    # a period is replaced with a hyphen.

    new_other_category = other_category.replace(".", "_")
    new_main_category = main_category.replace(".", "_")

    df.rename(columns={other_category: new_other_category, main_category:new_main_category}, inplace=True)

    other_selector = alt.selection_multi(fields=[new_other_category])
    main_selector = alt.selection_multi(fields=[new_main_category])

    other_category = new_other_category
    main_category = new_main_category

    bar1 = create_bar_chart(main_category, str('count(' + main_category + ')'), main_category, df,
                            other_selector | main_selector, main_selector)
    bar0 = create_bar_chart(other_category, str('count(' + other_category + ')'), main_category, df,
                            other_selector | main_selector, other_selector)

    heatmap = alt.Chart(df).mark_bar().encode(
        x='start',
        x2='end',
        y=alt.Y(
            'id',
            sort=alt.SortField(field=main_category,  order='ascending')
        ),
        href='website_url',
        color=main_category,
        opacity=alt.condition(other_selector | main_selector, alt.value(1), alt.value(0.2)),
        tooltip=['website_url', main_category, other_category, 'start', 'end', 'id']
    ).properties(
        width=heat_map_width,
        height=heat_map_height
    ).add_selection(
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

    ngrams_df['score'] = ngrams_df['pattern'].map(lambda cell: 100*textdistance.levenshtein.normalized_similarity(key_pattern, cell), na_action='ignore')
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
    ngrams.dropna(how='any', inplace=True) # only the pattern column can be NaN because all columns have starts (==offsets) and voices
    # calculate the score
    key_pattern = _close_match_helper(key_pattern)
    score_ngrams = _close_match(ngrams, key_pattern)

    slider = alt.binding_range(min=0, max=100, step=1, name='cutoff:')
    selector = alt.selection_single(name="SelectorName", fields=['cutoff'],
                                    bind=slider, init={'cutoff': 50})
    return create_heatmap('start', 'end', 'voice', 'score', score_ngrams, heatmap_width, heatmap_height,
                          alt.datum.score > selector.cutoff, selector, tooltip=['start', 'end', 'pattern', 'score'])

def generate_ngrams_and_duration(model, df, n=3, exclude=['Rest'],
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
    if n==-1:
        raise Exception("Cannot calculate the duration for this type of ngrams")

    # compute dur for the ngrams
    dur = model.getDuration(df)
    dur = dur.reindex_like(df).applymap(str, na_action='ignore')
    # combine them and generate ngrams and duration at the same time
    notes_dur = pd.concat([df, dur])
    ngrams = model.getNgrams(df=df, n=n, exclude=exclude,
                             interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = model.getNgrams(df=dur, n=n, exclude=exclude,
                                 interval_settings=interval_settings, unit=0, offsets=offsets)
    dur_ngrams = dur_ngrams.reindex_like(ngrams)

    # sum up durations!
    dur_ngrams = dur_ngrams.applymap(lambda cell: sum(float(Fraction(item)) for item in cell.split(", ")),
                                     na_action='ignore')

    return ngrams, dur_ngrams

# Network visualizations
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
            separator='/'
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
    return filtered_df.fillna("-").style.applymap(lambda x: "background: #ccebc5" if search_pattern_starts_with in x else "")

def create_interactive_compare_df(df, interval_column):
    """
    This method returns a wdiget allowing users to interact with
    the simple observations dataframe.
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :return: a widget that filters and colors a dataframe based on the users
    search pattern.
    """
    return interact(_manipulate_processed_network_df, df=fixed(df),
                    interval_column=fixed(interval_column), search_pattern_starts_with='')

def create_comparisons_networks_and_interactive_df(df, interval_column, interval_type, ema_column, patterns=[]):
    """
    Generate a dictionary of networks and a simple dataframe allowing the users
    search through the intervals.
    :param df: the dataframe the user interact with
    :param interval_column: the column of intervals
    :param interval_type: put "time" or "melodic"
    :param ema_column: column containing ema address
    :param patterns: we could only choose to look at specific patterns (optional)
    :return: a dictionary of networks created and a clean interactive df
    """
    # process df
    if patterns:
        df = df[df[interval_column].isin(patterns)].copy()

    networks_dict = create_interval_networks(df[interval_column], interval_type)
    df = process_network_df(df, interval_column, ema_column)
    return networks_dict, create_interactive_compare_df(df, interval_column)

def _trim_and_combine_piece_ids_with_measures(df):
    # extract necessary columns
    df = df[['model_observation.ema', 'model_observation.piece.piece_id',
            'relationship_type', 'derivative_observation.piece.piece_id',
            'derivative_observation.ema'
            ]].copy()

    # combine ema and piece id
    df['model_observation.ema'] = df['model_observation.ema'].str.split("/", n=1, expand=True)[0]
    df['derivative_observation.ema'] = df['derivative_observation.ema'].str.split("/", n=1, expand=True)[0]
    df['model'] = df['model_observation.piece.piece_id'] + ":" + df['model_observation.ema']
    df['derivative'] = df['derivative_observation.piece.piece_id'] + ":" + df['derivative_observation.ema']

    # TODO convert everything into string for non error handling

    return df

def group_observations(model_series, derivative_series):
    groups = {}
    for i in model_series.index:
        x = model_series.loc[i]
        y = derivative_series.loc[i]
        xset = groups.get(x.split(":")[0], set([x]))
        yset = groups.get(y.split(":")[0], set([y]))
        jset = xset | yset
        for z in jset:
            groups[z.split(":")[0]] = jset
    return groups

# TODO rename to something fancy
def plot_relationship_network(df, color='derivative', selected_relationship_types=[], selected_model_ids=[],
                              selected_derivative_ids=[], selected_families=[]):

    # process df's piece ids and measure into one column
    df = _trim_and_combine_piece_ids_with_measures(df)

    # filter df according to users selected relationship_type,
    # model_ids and derivative_ids
    if selected_relationship_types:
        df = df[df['relationship_type'].isin(selected_relationship_types)].dropna(how='all')
    if selected_model_ids:
        df = df[df['model_observation.piece.piece_id'].isin(selected_model_ids)].dropna(how='all')
    if selected_derivative_ids:
        df = df[df['derivative_observation.piece.piece_id'].isin(selected_derivative_ids)].dropna(how='all')
    if selected_families:
        families_dict = group_observations(df['model'], df['derivative'])
        relatives = set()
        gone_members = []
        for member in selected_families:
            # because of previous filtering, this member has been remained from the df
            if member in families_dict:
                relatives = set.union(relatives, families_dict[member])
            else:
                gone_members.append(member)

        if gone_members:
            print(str(len(gone_members)) + " " + ", ".join(member for member in gone_members) +
                  " no longer exist in df because of other filtering options")
        df = df[df['model'].isin(relatives) | df['derivative'].isin(relatives)].dropna(how='all')

    weights_dict = RELATIONSHIP_WEIGHTS
    df['weight'] = df['relationship_type'].map(weights_dict,
                                               na_action='ignore')
    df['weight'].fillna(0, inplace=True)

    # construct the networks
    nt = Network(directed=True, notebook=True)
    if color=='derivative':
        normal_nodes_column = 'model'
        colored_nodes_column = 'derivative'
        color_inheritance = 'to'
    elif color=='model':
        normal_nodes_column = 'derivative'
        colored_nodes_column = 'model'
        color_inheritance = 'from'
    else:
        raise Exception("Invalid input for `color`, please put 'derivative' or 'model'.")

    nt.add_nodes(df[normal_nodes_column])

    for row in df[colored_nodes_column].index:
        nt.add_node(df[colored_nodes_column].loc[row], group=df['relationship_type'].loc[row])

    for row in df.index:
        nt.add_edge(df['model'].loc[row], df['derivative'].loc[row],
                    value=int(df['weight'].loc[row]), title=df['relationship_type'].loc[row])
    nt.inherit_edge_colors(color_inheritance)

    return nt

def plot_pieces_relationship_network():
    pass

def plot_ngram_network():
    pass