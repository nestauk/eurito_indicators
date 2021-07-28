import logging
import warnings

import numpy as np
from sklearn.cluster import AffinityPropagation, KMeans
from sklearn.mixture import GaussianMixture

from eurito_indicators.getters.cordis_getters import (
    get_cordis_labelled,
    get_cordis_projects,
    get_specter,
)
from eurito_indicators.pipeline.clustering_naming import (
    build_cluster_graph,
    check_community_consensus,
    extract_name_communities,
    make_doc_comm_lookup,
)
from eurito_indicators.pipeline.processing_utils import (
    filter_by_length,
    save_model,
)
from eurito_indicators.utils.other_utils import save_matplot

warnings.simplefilter(action="ignore", category=FutureWarning)


if __name__ == "__main__":

    logging.info("Reading data")
    doc_vectors = get_specter()
    covid_level_lookup = get_cordis_labelled()
    projs = get_cordis_projects()

    doc_vectors_array = np.array(doc_vectors)
    covid_vectors = doc_vectors.loc[
        doc_vectors.index.isin(set(covid_level_lookup.keys()))
    ]
    index_project_id = {n: ind for n, ind in enumerate(covid_vectors.index)}

    clustering_options = [
        [KMeans, ["n_clusters", range(3, 30, 1)]],
        [AffinityPropagation, ["damping", np.arange(0.5, 0.91, 0.1)]],
        [GaussianMixture, ["n_components", range(3, 30, 1)]],
    ]
    logging.info("Building clusters")
    cluster_graph, index_lookup = build_cluster_graph(covid_vectors, clustering_options)

    logging.info("Checking clusters")
    comms = [
        make_doc_comm_lookup(
            extract_name_communities(
                cluster_graph=cluster_graph,
                resolution=0.65,
                index_lookup=index_lookup,
                text_table=projs,
            )[0]
        )
        for _ in range(20)
    ]

    covid_project_ids = list(
        filter_by_length(
            projs.query("covid_level!='non_covid'"),
            min_length=500,
            text_var="objective",
        )["project_id"]
    )
    cons_df = check_community_consensus(covid_project_ids, comms)

    has_match = cons_df.sum(axis=1) > 1

    cons_df.loc[has_match > 0].mean(axis=1).plot.hist()
    save_matplot("consensus_histogram")

    logging.info(cons_df.loc[has_match].mean(axis=1).mean())

    doc_consensus_means = (
        cons_df.loc[has_match]
        .stack()
        .reset_index(drop=False)
        .groupby("doc1")[0]
        .mean()
        .reset_index(name="consensus_share")
        .assign(project_type=lambda df: df["doc1"].map(covid_level_lookup))
    )

    doc_consensus_means.boxplot("consensus_share", by="project_type")
    save_matplot("consensus_boxplot")

    project_clusters = extract_name_communities(
        cluster_graph=cluster_graph,
        resolution=0.8,
        index_lookup=index_lookup,
        text_table=projs,
    )

    logging.info("Saving outputs")
    save_model(project_clusters, "cordis_clusters")
