# Some utilities to cluster and name vectors

import logging
from collections import Counter
from itertools import combinations

import altair as alt
import networkx as nx
import numpy as np
import pandas as pd
from community import community_louvain
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer

from eurito_indicators.pipeline.processing_utils import clean_table_names, make_lq


def build_cluster_graph(
    vectors: pd.DataFrame, clustering_algorithms: list, n_runs: int = 10, 
    sample:int = None
):
    """Builds a cluster network based on observation co-occurrences in a clustering output
    Args:
        vector: vectors to cluster
        clustering_algorithms: a list where the first element is the clustering
            algorithm and the second element are the parameter names and sets
        n_runs: number of times to run a clustering algorithm
        sample: size of the vector to sample.
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
    doc_id: str = "project_id",
    doc_text: str = "title",
) -> list:
    """Extracts community from the cluster graph and names them
    Args:
        cluster_graph: network object
        resolution: resolution for community detection
        index_lookup: lookup between integer indices and project ids
        text_table: table with variable names
        doc_id: document id in the text table
        doc_text: text variable in the text table
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
        (text_table.assign(community=lambda df: df[doc_id].map(ids_to_comms))),
        text_var=doc_text,
    )

    return comm_assignments, comm_names


def name_category(
    text_table: pd.DataFrame,
    cat_var: str = "community",
    text_var: str = "title",
    top_words: int = 15,
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
        stop_words="english", ngram_range=[2, 3], max_features=150, max_df=0.8
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


def make_doc_comm_lookup(comm_doc_lookup: dict, method: str = "single") -> dict:
    """Creates doc to comm lookup from a comm to list of docs lookup
    Args:
        comm_doc_lookup: lookup between clusters and their related vectors
        method: if single, assign one element to each cluster. If multiple,
        many clusters can be assigned to the same document
    """
    if method == "single":

        return {el: k for k, v in comm_doc_lookup.items() for el in v}
    elif method == "multiple":
        assign_dict = dict()

        for cl, assignments in comm_doc_lookup.items():

            for _id in assignments:
                if _id not in assign_dict.keys():
                    assign_dict[_id] = []
                    assign_dict[_id].append(cl)
                else:
                    assign_dict[_id].append(cl)

        return assign_dict


def get_closest_documents(
    dist_df: pd.DataFrame,
    cluster: int,
    cluster_assignments: dict,
    sd_scale: float = 2,
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

    selected = (
        dist_copy.sort_values(cluster, ascending=True)
        .loc[dist_copy[cluster] < (np.mean(dist_copy[cluster]) - sd_scale * sd)]
        .index.tolist()
    )

    logging.info(cluster)
    logging.info(len(selected))

    return selected


def tag_clusters(docs, cluster_assignment, cluster_name="cluster_covid"):
    """Tag clusters with an assignment"""

    docs_copy = docs.copy()
    docs_copy[cluster_name] = docs_copy["project_id"].map(cluster_assignment)
    docs_copy[cluster_name] = docs_copy[cluster_name].fillna("non_covid")

    return docs_copy


def make_activity(
    table: pd.DataFrame,
    reg_var: str = "coordinator_country",
    cat_var: str = "cluster_covid",
    funding_var: str = "ec_max_contribution",
) -> pd.DataFrame:
    """Counts activity, funding and LQs in a project activity table"""

    if reg_var == "participant_country":
        table = process_participant(table)

    table_wide = table.groupby([reg_var, cat_var]).size().unstack().fillna(0)

    table_funding = (
        table.groupby([reg_var, cat_var])[funding_var].sum().unstack().fillna(0)
    )

    table_lq, table_funding_lq = [make_lq(t) for t in [table_wide, table_funding]]

    stacked_tables = [
        t.stack().reset_index(name="value").assign(variable=v)
        for t, v in zip(
            [table_wide, table_lq, table_funding, table_funding_lq],
            ["project_total", "project_lq", "funding_total", "funding_lq"],
        )
    ]

    return pd.concat(stacked_tables, axis=0)


def process_participant(table):
    """Creates a participant table (requires exploding a combined variable
    in the projects table)
    """

    docs = table.copy()
    docs["participant_country"] = docs["participant_countries"].apply(
        lambda x: x.split(";") if type(x) == str else np.nan
    )
    docs_expl = docs.dropna(axis=0, subset=["participant_country"]).explode(
        "participant_country"
    )

    return docs_expl


def specialisation_robust(
    doc_distances,
    sd_thres,
    projects,
    cluster_assignments,
    pre_covid_date="2019/01/01",
    reg_var="coordinator_country",
):
    """Extract activity levels based on different thresholds of "distance"
    from a cluster centroid
    """

    docs = projects.copy().query(f"start_date<'{pre_covid_date}'")
    # Get project lists under different threshold

    close_to_clusters = [
        make_doc_comm_lookup(
            {
                cl: get_closest_documents(
                    doc_distances, cl, cluster_assignments, sd_scale=sd
                )
                for cl in doc_distances.columns
            },
            method="multiple",
        )
        for sd in sd_thres
    ]

    # Assign projects to categories

    results = []

    for thres, assign in zip(["low", "high"], close_to_clusters):

        docs_ = docs.copy()
        docs_["cluster_covid"] = docs_["project_id"].map(assign)
        docs_["cluster_covid"] = docs_["cluster_covid"].fillna("non_covid")

        docs_expl = docs_.explode("cluster_covid")

        if reg_var == "participant_country":

            docs_part = process_participant(docs_expl)
            act = make_activity(docs_part, reg_var="participant_country")
        else:
            act = make_activity(docs_expl)
        act = act.rename(columns={"value": f"value_{str(thres)}"})
        results.append(act)

    if len(results) > 1:
        merged = results[0].merge(results[1], on=[reg_var, "cluster_covid", "variable"])
        return merged
    else:
        return results[0]


def chart_specialisation_robust(
    reg_var,
    activity_var,
    dist_to_clusters,
    cluster_assignments,
    projs,
    focus_countries,
    clean_var_lookup,
    thres=[1.5, 2.5],
):
    """Plot level of preparedness in a covid cluster"""

    specialisation_related = specialisation_robust(
        dist_to_clusters,
        [1.5, 2.5],
        projects=projs,
        reg_var=reg_var,
        cluster_assignments=cluster_assignments,
    )

    specialisation_long = (
        specialisation_related.loc[
            specialisation_related[reg_var].isin(focus_countries)
        ]
        .query(f"variable=='{activity_var}'")
        .reset_index(drop=True)
        .melt(id_vars=[reg_var, "variable", "cluster_covid"], var_name="position")
        .reset_index(drop=True)
    )

    specialisation_long_clean = clean_table_names(
        specialisation_long, [reg_var, "cluster_covid"], clean_var_lookup
    ).query("cluster_covid!='non_covid'")
    spec_comp = (
        alt.Chart()
        .mark_line()
        .encode(
            x=alt.X("value", title=activity_var),
            detail="cluster_covid",
            y=alt.Y(
                "cluster_covid",
                title=None,
                axis=alt.Axis(ticks=False, labels=False),
                sort="descending",
            ),
            color="cluster_covid_clean:N",
        )
    ).properties(height=20, width=200)

    ruler = (
        alt.Chart()
        .transform_calculate(v="1")
        .mark_rule(color="black", strokeDash=[1, 1])
        .encode(x="v:Q")
    )

    comp_chart = alt.layer(spec_comp, ruler, data=specialisation_long_clean).facet(
        row=alt.Row(
            f"{reg_var}_clean",
            sort=alt.EncodingSortField("value", "median", order="descending"),
            header=alt.Header(labelAngle=360, labelAlign="left"),
        )
    )

    return comp_chart


def make_pre_post_table(
    projs,
    cluster_groups,
    distance_to_clusters,
    reg_var="coordinator_country",
    sd=1.5,
):
    """Extracts activity levels before and after covid-19"""

    # NB there is some confusion between the two types of lookups we use
    #   one that maps one project id to one cluster
    #   one that maps one cluster to a list of project ids
    #   Should find a clearer way to organise this

    response = make_activity(
        projs.query("start_date>'2019/01/01'").assign(
            cluster_covid=lambda df: df["project_id"].map(
                make_doc_comm_lookup(cluster_groups)
            )
        ),
        reg_var=reg_var,
    )

    print(response.head())

    sp_related = specialisation_robust(
        distance_to_clusters,
        [sd],
        projects=projs,
        reg_var=reg_var,
        cluster_assignments=cluster_groups,
    ).rename(columns={"value_low": "value_pre"})

    print(sp_related.head())

    combi = response.merge(sp_related, on=[reg_var, "cluster_covid", "variable"])

    logging.info(
        combi.groupby(["variable", "cluster_covid"]).apply(
            lambda df: df[["value", "value_pre"]].corr(method="spearman").iloc[0, 1]
        )
    )

    return combi


def filter_pre_post_table(
    combi_table,
    focus_countries,
    reg_var="coordinator_country",
    focus_var="project_lq",
    volume_var="project_total",
):
    """Filters an activity table to focus on particular variables and countries"""

    combined_table_focus = combi_table.loc[
        combi_table[reg_var].isin(focus_countries)
    ].query(f"variable=='{focus_var}'")

    size_lookup = combi_table.query(f"variable=='{volume_var}'")[
        [reg_var, "cluster_covid", "value"]
    ].rename(columns={"value": "volume"})

    combined_table_focus = combined_table_focus.merge(
        size_lookup, on=[reg_var, "cluster_covid"]
    )

    return combined_table_focus


def preparedness_response_chart(data, clean_var_lookup, reg_var):
    """Plots a comparison between preparedness and response"""

    data_clean = clean_table_names(data, [reg_var, "cluster_covid"], clean_var_lookup)
    clean_country_name = reg_var + "_clean"
    data_clean["cluster_covid_clean"] = [x for x in data_clean["cluster_covid_clean"]]

    comp_ch = (
        alt.Chart()
        .mark_point(filled=True, stroke="black", strokeWidth=0.5)
        .encode(
            x=alt.X(
                "value_pre",
                title="Related activity pre 2020",
                scale=alt.Scale(zero=False),
            ),
            size="volume",
            y=alt.Y("value", title="Activity post-2020", scale=alt.Scale(zero=False)),
            color=alt.Color(clean_country_name, scale=alt.Scale(scheme="tableau20")),
            tooltip=[clean_country_name, "volume"],
        )
    ).properties(height=200, width=300)

    hor = (
        alt.Chart()
        .transform_calculate(y="1")
        .mark_rule(strokeDash=[2, 2])
        .encode(y="y:Q")
    )

    vert = (
        alt.Chart()
        .transform_calculate(x="1")
        .mark_rule(strokeDash=[2, 2])
        .encode(x="x:Q")
    )

    lay = alt.layer(comp_ch, hor, vert, data=data_clean).facet(
        "cluster_covid_clean", columns=3
    )

    return lay
