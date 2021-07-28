# Analysis of CORDIS research topics

import logging
import warnings


import altair as alt
import pandas as pd

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.cordis_getters import (
    get_cluster_labels,
    get_cordis_clusters,
    get_cordis_projects,
    get_topic_community_names,
    get_topsbm,
)
from eurito_indicators.pipeline.clustering_naming import make_doc_comm_lookup
from eurito_indicators.pipeline.networks import (
    make_topic_network,
    plot_topic_network,
)
from eurito_indicators.pipeline.topic_utils import topic_regression
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    save_altair,
)

warnings.simplefilter(action="ignore", category=FutureWarning)

FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"
VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
driv = google_chrome_driver_setup()


def parse_var_name(var):
    return var.split(".")[1][:-1].strip()


if __name__ == "__main__":

    logging.info("Reading data")
    projs = get_cordis_projects()
    covid_ids = set(projs.query("covid_level !='non_covid'")["project_id"])
    cluster_labels = get_cluster_labels()
    cluster_results = get_cordis_clusters()
    topsbm_results = get_topsbm()
    topic_community_names = get_topic_community_names()

    cluster_doc_lookup = {
        k: cluster_labels[v]
        for k, v in make_doc_comm_lookup(cluster_results[0]).items()
    }
    topic_mix = topsbm_results[1]

    logging.info("Making topic network")
    network, node_df, community_partition = make_topic_network(
        topic_mix, covid_ids, threshold=0.1, seed=123, resolution=0.5
    )

    node_df["comm"] = (
        node_df["node"].map(community_partition).map(topic_community_names)
    )

    covid_network = plot_topic_network(network[1], node_df)

    save_altair(covid_network, "cordis_covid_topic_network", driver=driv, path=FIG_PATH)

    # Topic regression
    logging.info("Topic regression: all clusters")
    cluster_cats = topic_mix.index.map(cluster_doc_lookup).fillna("non_covid")
    reg_results = topic_regression(
        topic_mix, cluster_cats, ref_class="non_covid", log=False
    )

    # %%
    reg_results_df = (
        pd.concat(reg_results)
        .rename(columns={"index": "cluster", 0: "low", 1: "high"})
        .assign(community=lambda df: df["label"].map(community_partition))
        .assign(community_label=lambda df: df["community"].map(topic_community_names))
        .assign(mean=lambda df: (df["low"] + df["high"]) / 2)
        .dropna(axis=0, subset=["community"])
        .sort_values(["community", "label"], ascending=[True, False])
        .assign(rank=lambda df: df.index)
        .melt(
            id_vars=["cluster", "label", "community", "mean", "rank", "community_label"]
        )
    )

    ch = (
        alt.Chart()
        .mark_point(filled=True, size=2, color="white")
        .encode(
            y=alt.Y(
                "label",
                axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
                title="Topic",
            ),
            x=alt.X("mean", scale=alt.Scale(type="linear")),
            tooltip=["label"],
        )
    ).properties(width=200, height=350)

    line = (
        alt.Chart()
        .mark_line(strokeWidth=1.5)
        .encode(
            y=alt.Y(
                "label",
                axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
            ),
            x=alt.X("value", title="Regression confidence interval"),
            detail="label",
            tooltip=["label"],
            color=alt.Color(
                "community_label:N",
                title="Topic community",
                sort=alt.EncodingSortField("community"),
                scale=alt.Scale(scheme="tableau20"),
            ),
        )
    ).properties(width=200, height=350)

    rule = (
        alt.Chart()
        .transform_calculate(x="0")
        .mark_rule(strokeDash=[4, 1], stroke="black")
        .encode(x="x:Q")
    )

    topical_focus_chart = alt.layer(line, ch, rule, data=reg_results_df).facet(
        facet=alt.Facet("cluster", title="Research cluster"), columns=3
    )

    save_altair(
        ch_resize(topical_focus_chart), "topic_coefficients", driver=driv, path=VAL_PATH
    )

    # Model results based on cluster dummy
    logging.info("Topic regression: Covid response")
    is_covid_cat = [
        "Covid response" if x != "non_covid" else "non_covid"
        for x in topic_mix.index.map(cluster_doc_lookup).fillna("non_covid")
    ]

    reg_results_2 = topic_regression(
        topic_mix, is_covid_cat, ref_class="non_covid", log=False
    )

    reg_results_df_2 = (
        pd.concat(reg_results_2)
        .rename(columns={"index": "cluster", 0: "low", 1: "high"})
        .assign(community=lambda df: df["label"].map(community_partition))
        .assign(community_label=lambda df: df["community"].map(topic_community_names))
        .assign(mean=lambda df: (df["low"] + df["high"]) / 2)
        .dropna(axis=0, subset=["community"])
        .sort_values(["community", "mean"], ascending=[True, False])
        .assign(rank=lambda df: df.index)
        .melt(
            id_vars=["cluster", "label", "community", "mean", "rank", "community_label"]
        )
    )

    ch = (
        alt.Chart(reg_results_df_2)
        .mark_point(filled=True, size=10, color="grey", stroke="black", strokeWidth=0.1)
        .encode(
            x=alt.X(
                "label",
                axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
                title="Topic",
            ),
            y=alt.Y("mean", scale=alt.Scale(type="linear")),
            tooltip=["label"],
        )
    ).properties(width=800, height=300)

    line = (
        alt.Chart(reg_results_df_2)
        .mark_line(strokeWidth=1.5)
        .encode(
            x=alt.X(
                "label",
                axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
            ),
            y=alt.Y("value", title="Regression confidence interval"),
            detail="label",
            tooltip=["label"],
            color=alt.Color(
                "community_label:N",
                title="Topic community",
                sort=alt.EncodingSortField("community"),
                scale=alt.Scale(scheme="tableau20"),
            ),
        )
    ).properties(width=800, height=300)

    rule = (
        alt.Chart(reg_results_df_2)
        .transform_calculate(x="0")
        .mark_rule(strokeDash=[4, 1], stroke="black")
        .encode(y="x:Q")
    )

    commision_topics = ch_resize((ch + line + rule))

    save_altair(commision_topics, "topical_focus", driver=driv, path=FIG_PATH)

    comms_grouped = {cl:[k for k,v in community_partition.items() if v==cl] for cl in sorted(set(community_partition.values()))}

    for k,v in comms_grouped.items():

        print(k)
        print(v)
        print("\n")
