# Script to work with network data
import logging
import random
from itertools import chain, combinations

import networkx as nx
import pandas as pd
from community import community_louvain

from eurito_indicators.pipeline.altair_network import plot_altair_network


def make_network_from_doc_term_matrix(mat, threshold, id_var):
    """Create a network from a document term matrix.
    Args
        Document term matrix where the rows are documents and the columns are topics
        threshold is the threshold to consider that a topic is present in a matrix.
    Returns:
        A network
    """
    # Melt the topic mix and remove empty entries
    cd = pd.melt(mat, id_vars=[id_var])

    cd = cd.loc[cd["value"] > threshold]

    # This gives us the topic co-occurrence matrix
    co_occurrence = cd.groupby(id_var)["variable"].apply(lambda x: list(x))

    # Here the idea is to create a proximity matrix based on co-occurrences

    # Turn co-occurrences into combinations of pairs we can use to construct a
    # similarity matrix
    sector_combs = chain(*[sorted(list(combinations(x, 2))) for x in co_occurrence])
    sector_combs = [x for x in sector_combs if len(x) > 0]

    # Turn the sector combs into an edgelist
    edge_list = pd.DataFrame(sector_combs, columns=["source", "target"])

    edge_list["weight"] = 1

    # Group over edge pairs to aggregate weights
    edge_list_weighted = (
        edge_list.groupby(["source", "target"])["weight"].sum().reset_index(drop=False)
    )

    edge_list_weighted.sort_values("weight", ascending=False).head(n=10)

    # Create network and extract communities
    net = nx.from_pandas_edgelist(edge_list_weighted, edge_attr=True)

    return net


def process_network(net, extra_edges=100):
    """Creates the base for a sector space network
    Args:
        sector_space (network): nx network object
        extra_edges (int): extra edges to add to the maximum spanning tree
    """
    logging.info("making network")

    max_tree = nx.maximum_spanning_tree(net)

    max_tree_edges = set(max_tree.edges())

    top_edges_net = nx.Graph(
        [
            x
            for x in sorted(
                net.edges(data=True),
                key=lambda x: x[2]["weight"],
                reverse=True,
            )
            if (x[0], x[1]) not in max_tree_edges
        ][:extra_edges]
    )
    united_graph = nx.Graph(
        list(max_tree.edges(data=True)) + list(top_edges_net.edges(data=True))
    )

    logging.info("Getting positions")
    pos = nx.kamada_kawai_layout(united_graph, dim=2)

    labs = {k: k for k, v in pos.items()}

    return pos, united_graph, labs


def make_topic_network(
    topic_df: pd.DataFrame,
    covid_ids,
    threshold: float = 0.1,
    resolution: float = 0.7,
    seed=None,
):
    """Plots a topic network
    Args:
        topic_df: topic mix
        threshold: threshold for considering that a topic is present in a corpus
    """

    net = make_network_from_doc_term_matrix(
        topic_df.reset_index(drop=False), threshold=threshold, id_var="index"
    )
    net2 = process_network(net, extra_edges=100)

    covid_topics = (
        topic_df.loc[topic_df.index.isin(covid_ids)]
        .applymap(lambda x: x > threshold)
        .sum()
    )

    keep_topics = covid_topics.loc[covid_topics > 1].index.tolist()
    covid_size_dict = covid_topics.loc[keep_topics].to_dict()

    if seed is None:
        comms = community_louvain.best_partition(net2[1], resolution=resolution)
    else:
        comms = community_louvain.best_partition(
            net2[1], resolution=resolution, random_state=seed
        )

    node_df = (
        pd.DataFrame(net2[0])
        .T.reset_index(drop=False)
        .rename(columns={0: "x", 1: "y", "index": "node"})
        .assign(size=lambda df: df["node"].map(covid_size_dict))
        .assign(node_name=lambda df: df["node"])
    )

    return net2, node_df, comms


def plot_topic_network(network, node_df):
    """Plots a topic network"""

    cov_net = plot_altair_network(
        node_df,
        network,
        node_label="node_name",
        node_size="size",
        node_color="comm",
        show_neighbours=False,
        **{
            "node_size_title": "Appearances in corpus",
            "node_color_title": "Community",
            "edge_weight_title": "Topic co-occurrences",
            "title": "H2020 Covid projects topic network",
        },
        edge_scale=0.1,
        edge_opacity=0.05
    ).properties(width=800, height=500)

    return cov_net
