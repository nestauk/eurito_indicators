# Some utilities to cluster and name vectors

import logging
from collections import Counter
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd
from community import community_louvain
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer


def build_cluster_graph(
    vectors: pd.DataFrame, clustering_algorithms: list, n_runs: int = 10
):
    """Builds a cluster network based on observation co-occurrences in a clustering output
    Args:
        vector: vectors to cluster
        clustering_algorithms: a list where the first element is the clustering
            algorithm and the second element are the parameter names and sets
        n_runs: number of times to run a clustering algorithm
    Returns:
        A network where the nodes are observations and their edges number
            of co-occurrences in the clustering
    """

    clustering_edges = []

    index_to_id_lookup = {n: ind for n, ind in enumerate(vectors.index)}

    logging.info("Running cluster ensemble")
    for cl in clustering_algorithms:

        logging.info(cl[0])

        algo = cl[0]

        parametres = [{cl[1][0]: v} for v in cl[1][1]]

        for par in parametres:

            logging.info(f"running {par}")

            for _ in range(n_runs):

                cl_assignments = algo(**par).fit_predict(vectors)
                index_cluster_pair = {n: c for n, c in enumerate(cl_assignments)}

                indices = range(0, len(cl_assignments))

                pairs = combinations(indices, 2)

                for p in pairs:

                    if index_cluster_pair[p[0]] == index_cluster_pair[p[1]]:
                        clustering_edges.append(frozenset(p))

    edges_weighted = Counter(clustering_edges)

    logging.info("Building cluster graph")

    edge_list = [(list(fs)[0], list(fs)[1]) for fs in edges_weighted.keys()]
    cluster_graph = nx.Graph()
    cluster_graph.add_edges_from(edge_list)

    for ed in cluster_graph.edges():

        cluster_graph[ed[0]][ed[1]]["weight"] = edges_weighted[
            frozenset([ed[0], ed[1]])
        ]

    return cluster_graph, index_to_id_lookup


def extract_name_communities(
    cluster_graph: nx.Graph,
    resolution: float,
    index_lookup: dict,
    text_table: pd.DataFrame,
) -> list:
    """Extracts community from the cluster graph
    Args:
        cluster_graph: network object
        resolution: resolution for community detection
        index_lookup: lookup between integer indices and project ids
        text_table: table with variable names
    Returns:
        a lookup between communities and the projects that belong to them
        a lookup between community indices and names
    """
    logging.info("Extracting communities")
    comms = community_louvain.best_partition(cluster_graph, resolution=resolution)
    ids_to_comms = {index_lookup[k]: v for k, v in comms.items()}

    comm_assignments = {
        comm: [index_lookup[k] for k, v in comms.items() if v == comm]
        for comm in set(comms.values())
    }

    logging.info("Naming communities")
    comm_names = name_category(
        (text_table.assign(community=lambda df: df["project_id"].map(ids_to_comms))),
    )

    return comm_assignments, comm_names


def name_category(
    text_table: pd.DataFrame,
    cat_var: str = "community",
    text_var: str = "title",
    top_words: int = 20,
) -> dict:
    """Names the clusters with their highest tfidf tokens
    Args:
        text_table: a dataframe with category to name
        cat_var: category to name
        text_var: text to use in naming
        top_words: top words to keep in name
    Returns:
        lookup between category indices and names
    """

    grouped_names = text_table.groupby(cat_var)[text_var].apply(
        lambda x: " ".join(list(x))
    )

    tfidf = TfidfVectorizer(
        stop_words="english", ngram_range=[1, 3], max_features=3000, max_df=0.7
    )
    tfidf_fit = tfidf.fit_transform(grouped_names)
    tfidf_df = pd.DataFrame(tfidf_fit.todense(), columns=tfidf.vocabulary_)


    cluster_names = {}

    for ind, _ in tfidf_df.iterrows():

        salient_words = tfidf_df.loc[ind].sort_values(ascending=False).index[:top_words]

        cluster_names[ind] = "_".join(salient_words)

    return cluster_names


def make_distance_to_clusters(
    vectors_df: pd.DataFrame,
    cluster_ids: dict,
) -> pd.DataFrame:
    """Calculates distances between all vectors in a table and the centroids of identified clusters
    Args:
        vectors_df: table with all vectors
        cluster_id: lookup between cluster indices and vector indices
    Returns:
        A table with distance between each vector and the cluster categories
    """

    logging.info("Calculating cluster centroids")
    cluster_centroids_df = pd.concat(
        [
            vectors_df.loc[vectors_df.index.isin(set(v))].median()
            for v in cluster_ids.values()
        ],
        axis=1,
    ).T
    cluster_centroids_df.index = cluster_ids.keys()

    cluster_centroids_array = np.array(cluster_centroids_df)
    vectors_array = np.array(vectors_df)

    dists = []

    logging.info("Calculating vector distances to clusters")
    for v in vectors_array:
        vect_dist = []
        for cl_centr in cluster_centroids_array:
            vect_dist.append(cosine(v, cl_centr))
        dists.append(vect_dist)

    dist_df = pd.DataFrame(
        dists,
        index=vectors_df.index,
        columns=sorted(set(cluster_ids.keys()))
        # columns=[cluster_names[comm] for comm in sorted(set(cluster_ids.keys()))],
    )

    return dist_df


def check_community_consensus(doc_ids: list, communities: list) -> pd.DataFrame:
    """Checks if project ids are allocated to the same communities by our approach
    Args:
        doc_ids: list of doc ids
        communities: list of community assignments
    Returns:
        A dataframe with pairs of projects and the number of times they are assigned together
    """

    id_consensus = []

    doc_pairs = combinations(doc_ids, 2)

    for c in doc_pairs:

        match = [1 if comm[c[0]] == comm[c[1]] else 0 for comm in communities]

        matches_id = pd.Series(
            list(c) + match, index=["doc1", "doc2"] + list(range(len(communities)))
        )
        id_consensus.append(matches_id)

    id_consensus_df = pd.DataFrame(id_consensus).set_index(["doc1", "doc2"])
    return id_consensus_df


def make_doc_comm_lookup(comm_doc_lookup):
    """Creates doc to comm lookup from a comm to list of docs lookup"""

    return {el: k for k, v in comm_doc_lookup.items() for el in v}


def get_closest_documents(
    dist_df: pd.DataFrame,
    cluster: int,
    cluster_assignments: dict,
    sd_scale: int = 2,
    exclude_in_cluster: bool = True,
) -> list:
    """Returns closest documents to a cluster
    Args:
        dist_df: dataframe with distances
        cluster: cluster we are interested in
        cluster assignments: lookup between cluster ids and project ids
        sd_scale: standard deviation to define proximity
        exclude_in_cluster: whether we want to exclude docs already in a cluster from the results
    Returns:
        A list of project ids
    """

    dist_copy = dist_df.copy()

    if exclude_in_cluster is True:

        dist_copy = dist_copy.loc[~dist_copy.index.isin(cluster_assignments[cluster])]

    sd = np.std(dist_copy[cluster])

    selected = dist_copy.loc[
        dist_copy[0] < (np.mean(dist_copy[0]) - sd_scale * sd)
    ].index.tolist()

    logging.info(len(selected))

    return selected
