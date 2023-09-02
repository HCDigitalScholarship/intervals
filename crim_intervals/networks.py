import networkx as nx
from community import community_louvain
from copy import deepcopy
import pandas as pd
from itertools import combinations
from pyvis.network import Network

def add_communities(G):
    G = deepcopy(G)
    partition = community_louvain.best_partition(G)
    nx.set_node_attributes(G, partition, "group")
    return G

def create_node_html(node: str, source_df: pd.DataFrame, node_col: str):
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

    graph = deepcopy(graph)

    node_list = pd.Series(edge_list).apply(pd.Series).stack().unique()

    for n in node_list:
        graph.add_node(n, title=create_node_html(n, source_df, node_col))

    return graph

def choose_network(df, chosen_word, file_name):

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
    output_file_name = f"{corpus_name}_{p_type}_{chosen_word}.html"
    choose_network(df.query(f"Presentation_Type == '{p_type}'"), chosen_word, output_file_name)
