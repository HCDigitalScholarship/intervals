import networkx as nx
from community import community_louvain
from copy import deepcopy
import pandas as pd
from itertools import combinations
from pyvis.network import Network

def add_communities(G):
    """
    Detect communities in a graph and store them as a node attribute.

    Runs Louvain community detection on a copy of `G` and stores each node's
    community id in a "group" attribute, which pyvis/networkx can use to
    color nodes by community.

    Parameters
    ----------
    G : networkx.Graph
        The graph to analyze. Not modified in place; a copy is returned.

    Returns
    -------
    networkx.Graph
        A copy of `G` with a "group" attribute added to every node.
    """
    G = deepcopy(G)
    partition = community_louvain.best_partition(G)
    nx.set_node_attributes(G, partition, "group")
    return G

def create_node_html(node: str, source_df: pd.DataFrame, node_col: str):
    """
    Build an HTML tooltip listing the pieces/offsets where a node occurs.

    Filters `source_df` for rows where `node_col` equals `node`, and renders
    an HTML `<ul>` with one `<li>` per matching row showing Composer, Title,
    and First_Offset. Intended to be passed as the `title` of a pyvis node
    so it displays as a hover tooltip.

    Parameters
    ----------
    node : str
        The value to match against `node_col` in `source_df`.
    source_df : pandas.DataFrame
        A dataframe with "Composer", "Title", "First_Offset", and `node_col`
        columns.
    node_col : str
        The name of the column in `source_df` to match `node` against.

    Returns
    -------
    str
        An HTML string (`<ul>...</ul>`) suitable for use as a pyvis node title.
    """
    rows = source_df.loc[source_df[node_col] == node].itertuples()

    html_lis = []

    for r in rows:
        html_lis.append(f"""<li>Composer: {r.Composer}<br>
                                Title: {r.Title}<br>
                                Offset: {r.First_Offset}</li>"""
                       )

    html_ul = f"""<ul>{''.join(html_lis)}</ul>"""

    return html_ul


def add_nodes_from_edgelist(edge_list: list,
                               source_df: pd.DataFrame,
                               graph: nx.Graph,
                               node_col: str):
    """
    Add every unique node found in an edge list to a graph, with tooltips.

    Flattens `edge_list` (a list of node pairs) to its unique node values and
    adds each as a node in a copy of `graph`, using `create_node_html` to
    build a hover-tooltip title for each node from `source_df`.

    Parameters
    ----------
    edge_list : list
        A list of node pairs (e.g. 2-tuples) defining the edges to draw nodes
        from.
    source_df : pandas.DataFrame
        A dataframe with "Composer", "Title", "First_Offset", and `node_col`
        columns, passed through to `create_node_html` for each node.
    graph : networkx.Graph
        The graph to add nodes to. Not modified in place; a copy is returned.
    node_col : str
        The column in `source_df` that node values correspond to.

    Returns
    -------
    networkx.Graph
        A copy of `graph` with a node (and HTML tooltip) added for every
        unique value found in `edge_list`.
    """
    graph = deepcopy(graph)

    node_list = pd.Series(edge_list).apply(pd.Series).stack().unique()

    for n in node_list:
        graph.add_node(n, title=create_node_html(n, source_df, node_col))

    return graph

def choose_network(df, chosen_word, file_name):
    """
    Build and render a pyvis network of co-occurring values within pieces.

    Groups `df` by "Title" and, within each piece, forms all pairwise
    combinations of the values in the `chosen_word` column (e.g. soggetti or
    presentation-type labels that co-occur in the same piece). Each unique
    pair becomes an edge; nodes are colored by detected community
    (`add_communities`) and annotated with hover tooltips
    (`add_nodes_from_edgelist`). The resulting graph is written to an HTML
    file via pyvis.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with a "Title" column and a `chosen_word` column.
    chosen_word : str
        The column in `df` whose values become the network's nodes.
    file_name : str
        The path/filename pyvis will write the rendered HTML graph to.

    Returns
    -------
    None
        The graph is written to `file_name` as a side effect; nothing is
        returned.
    """
    output_grouped = df.groupby(['Title'])[chosen_word].apply(list).reset_index()
    pairs = output_grouped[chosen_word].apply(lambda x: list(combinations(x, 2)))
    pairs2 = pairs.explode().dropna()
    unique_pairs = pairs.explode().dropna().unique()


    pyvis_graph = Network(notebook=True, width="1800", height="1400", bgcolor="black", font_color="white")
    G = nx.Graph()

    try:
        G = add_nodes_from_edgelist(edge_list=unique_pairs, source_df=df, graph=G, node_col=chosen_word)
    except Exception as e:
        print(e)


    G.add_edges_from(unique_pairs)
    G = add_communities(G)
    pyvis_graph.from_nx(G)
    pyvis_graph.show(file_name)

def create_ptype_network(df, p_type, chosen_word, corpus_name):
    """
    Build a `choose_network` graph limited to one presentation type.

    Filters `df` to rows where "Presentation_Type" equals `p_type`, then
    calls `choose_network` on the filtered result, writing the output to a
    file named `"{corpus_name}_{p_type}_{chosen_word}.html"`.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with "Title", "Presentation_Type", and `chosen_word`
        columns.
    p_type : str
        The presentation type to filter for (matched against
        "Presentation_Type").
    chosen_word : str
        The column in `df` whose values become the network's nodes.
    corpus_name : str
        A label used (with `p_type` and `chosen_word`) to build the output
        HTML filename.

    Returns
    -------
    None
        The graph is written to a file as a side effect; nothing is
        returned.
    """
    output_file_name = f"{corpus_name}_{p_type}_{chosen_word}.html"
    choose_network(df.query(f"Presentation_Type == '{p_type}'"), chosen_word, output_file_name)
