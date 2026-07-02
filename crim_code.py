# functions to load
# run this cell but don't edit it!
import plotly.express as px
import crim_intervals.visualizations as viz
import pandas as pd

python__all__ = [
    # functions
    'extract_letter',
    'extract_descending',
    'extract_and_sort_reverse',
    'extract_and_sort_forward',
    'convert_tuple',
    'ngram_heatmap',
    'ng_network',
    'mm',
    'standardize_note',

    # lookup lists and orders
    'pitch_order',
    'recta_order',
    'pitch_class_order',
    'custom_tone_order',
    'values',

    # color dictionaries
    'cadence_color_dict',
    'cvf_color_dict',
    'color_palette',
]


    
def extract_descending(interval):
        """
        Extract descending interval value.
        
        Parameters:
        -----------
        interval : str
            Interval string
            
        Returns:
        --------
        int
            Extracted interval value
        """
        match = re.search(r'-?\d+', interval)
        return int(match.group())
    

def extract_and_sort_reverse(items):
    """
    Extract numbers from items and sort in reverse order.

    Parameters:
    -----------
    items : list
        List of items to sort

    Returns:
    --------
    list
        Sorted list
    """
    # Function to extract numeric part
    def extract_num(item):
        match = re.search(r'[-+]?\d+', item)
        return int(match.group()) if match else 0

    # Extract numbers and sort
    sorted_neg_items = sorted(items, key=extract_num, reverse=True)
    return sorted_neg_items


def extract_and_sort_forward(items):
    """
    Extract numbers from items and sort in forward order.

    Parameters:
    -----------
    items : list
        List of items to sort

    Returns:
    --------
    list
        Sorted list
    """
    # Function to extract numeric part
    def extract_num(item):
        match = re.search(r'[-+]?\d+', item)
        return int(match.group()) if match else 0

    # Extract numbers and sort
    sorted_items = sorted(items, key=extract_num, reverse=False)
    return sorted_items


def extract_letter(value):
    """
    Extract letter part from a value.

    Parameters:
    -----------
    value : str
        String value to extract from

    Returns:
    --------
    str
        Extracted letter part
    """
    # Find the index of the first digit
    if value is not None:
        for i, char in enumerate(value):
            if char.isdigit():
                # Return everything before the first digit
                return value[:i]
        # If no digit is found, return the entire string
        return value
    return None


def convert_tuple(tup):
    """
    Convert tuple to string.

    Parameters:
    -----------
    tup : tuple
        Tuple to convert

    Returns:
    --------
    str
        Converted string
    """
    out = ""
    if isinstance(tup, tuple):
        out = '_'.join(tup)
    return out

# function for ngram heatmap:  do not edit!

def ngram_heatmap(piece, combine_unisons_choice, kind_choice, directed, compound, length_choice, include_count, entries_only, style='color', heatmap_width=800, heatmap_height=300):
    # find entries for model
    nr = piece.notes(combineUnisons = combine_unisons_choice)
    mel = piece.melodic(df = nr, 
                        kind = kind_choice,
                        directed = directed,
                        compound = compound,
                        end = False)
    
    # this is for entries only
    if entries_only == True:    
        # pass the following ngrams to the plot below as first df
        entry_ngrams = piece.entries(df = mel, 
                                    n = length_choice, 
                                    thematic = True, 
                                    anywhere = True,
                                    exclude = ['Rest'])
        # pass the ngram durations below to the plot as second df
        entry_ngrams_duration = piece.durations(df = mel, 
                                            n =length_choice, 
                                            mask_df = entry_ngrams)
        # make the heatmap
        chart = viz.plot_ngrams_heatmap(entry_ngrams,
                                         entry_ngrams_duration,
                                         selected_patterns=[],
                                         voices=[],
                                         includeCount=include_count,
                                         style=style,
                                         heatmap_width=heatmap_width,
                                         heatmap_height=heatmap_height)

        return chart
    
    # this is for ALL mel ngrams (if entries is False in form)
    else:
        mel_ngrams = piece.ngrams(df = mel, n = length_choice, exclude = ['Rest'])
        mel_ngrams_duration = piece.durations(df = mel, 
                                          n =length_choice)
        
        chart = viz.plot_ngrams_heatmap(mel_ngrams,
                                         mel_ngrams_duration,
                                         selected_patterns=[],
                                         voices=[],
                                         includeCount=include_count,
                                         style=style,
                                         heatmap_width=heatmap_width,
                                         heatmap_height=heatmap_height)
        
        # # mel_ngrams_detail = piece.detailIndex(mel_ngrams, offset = False)  
        return chart

# Network Function--Do Not Edit!
def ng_network(data, threshold_for_shared_ngrams, thickness_adjust, network_name):

    # and now, a network in which the nodes are the pieces and edges represent the ngrams they share.  
    # the thickness of the edges varies with the number of shared ngrams
    # the colors distinguish 'communities' of pieces that are highly related

    df = pd.DataFrame(data)
    df = df.reset_index()
    if 'level_1' in df.columns:
        df.drop('level_1', axis=1, inplace=True)
    df = df.rename(columns={0: 'ngram'})

    #define the function to convert tuples to strings
    def convertTuple(tup):
        out = ""
        if isinstance(tup, tuple):
            out = '_'.join(tup)
        return out  
    # clean the tuples
    df['ngram'] = df['ngram'].apply(convertTuple)

    # Group by 'ngram' and extract a list of unique titles for each group
    grouped_titles = df.groupby('ngram')['title'].unique().reset_index(name='titles')

    # Generate all pairs of titles for each group
    all_pairs = []
    for _, row in grouped_titles.iterrows():
        pairs = list(combinations(row['titles'], 2))
        all_pairs.append((row['ngram'], pairs))

    # Create a new DataFrame with the results
    result_df = pd.DataFrame(all_pairs, columns=['ngram', 'title_pairs'])
    # remove the empty pairs
    df_filtered = result_df[result_df['title_pairs'].apply(len) > 0]

    # explode the complicated lists of tuples, effectively 'tyding' the data
    exploded_df = df_filtered.explode('title_pairs')

    # get the counts of each pair, which provides the basis of the weights
    pair_counts = exploded_df['title_pairs'].value_counts()

    # limit to high scoring pairs (>3)
    pair_counts = pair_counts[pair_counts >= threshold_for_shared_ngrams]

    # Adding Louvain Communities
    def add_communities(G):
        G = deepcopy(G)
        partition = community_louvain.best_partition(G)
        nx.set_node_attributes(G, partition, "group")
        return G

    # Create an empty NetworkX graph
    G = nx.Graph()


    # Add nodes and assign weights to edges
    for pair, count in pair_counts.items():
        # Directly unpacking the tuple into node1 and node2
        node1, node2 = pair
        # Adding nodes if they don't exist already
        if node1 not in G.nodes:
            G.add_node(node1)
        if node2 not in G.nodes:
            G.add_node(node2)
        # Adding edge with weight
        G.add_edge(node1, node2, weight=count)

    # Adjusting edge thickness based on weights
    for edge in G.edges(data=True):
        edge[2]['width'] = edge[2]['weight']/thickness_adjust

    G = add_communities(G)

    # set display parameters
    ngram_map = Network(notebook=True,
                       width="1000",
                              height="1000",
                              bgcolor="black", 
                              font_color="white")

    # Set the physics layout of the network
    ngram_map.set_options("""
    {
    "physics": {
    "enabled": true,
    "forceAtlas2Based": {
        "springLength": 1
    },
    "solver": "forceAtlas2Based"
    }
    }
    """)

    ngram_map.from_nx(G)
    return ngram_map.show(network_name)
    

    
    
# variable orders.  These include the full chromatic range of possibilities

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


pitch_class_order = ['C', 'C#', 'D-','D', 'D#', 'E-', 'E', 'E#', 'F', 'F#', 'G-', 'G', 'G#', 'A-','A', 'A#', 'B-', 'B', 'Rest']


def mm(graph):
    graphbytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    display(
        Image(
            url="https://mermaid.ink/img/" + base64_string
        )
    )
    
# Function to standardize note names
def standardize_note(note):
   
    if '-' in note:
        return note.replace('-', 'b')
    return note


# Create a color map dictionary that maps each cadence type to a specific color
cadence_color_dict = {
    'Authentic': '#1f77b4',  # blue
    'Clausula Vera': '#ff7f0e',  # orange
    'Evaded Authentic': '#2ca02c',  # green
    'Leaping Contratenor': '#d62728',  # red
    'Phrygian Clausula Vera': '#9467bd',  # purple
    'Phrygian': '#8c564b',  # brown
    'Evaded Clausula Vera': '#e377c2',  # pink
    'Double Leading Tone': '#7f7f7f',  # gray
    'Abandoned Clausula Vera': '#bcbd22',  # olive
    'Quince': '#17becf',  # cyan
    'Altizans Only': '#aec7e8',  # light blue
    'Abandoned Authentic': '#ffbb78'  # light orange
}

# List of values for CVFs
values = ['Cx', 'CB', 'CTB', 'TCB', 'zCB', 'CT', 'CTA', 'CTx', 'TC', 'TCA',
          'TCx', 'ACT', 'CAT', 'CTb', 'TCb', 'CTL', 'CzB', 'CxT', 'zCT',
          'Ct', 'tCx']

# Get the default color palette
color_palette = px.colors.qualitative.Plotly

# Create a color dictionary
cvf_color_dict = {value: color for value, color in zip(values, color_palette)}


# tone order for charts

custom_tone_order = ['E-', 'B-', 'F', 'C', 'G', 'D', 'A', 'E', 'B']  # Your desired order
