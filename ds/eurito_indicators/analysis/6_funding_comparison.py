# Funding comparison
import logging
from datetime import datetime

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from community import community_louvain
from currency_converter import CurrencyConverter
from numpy.random import choice
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.funding_getters import (
    get_cordis_covid,
    get_gtr_projects,
    get_wellcome,
)
from eurito_indicators.pipeline.networks import (
    make_network_from_doc_term_matrix,
    plot_altair_network,
    process_network,
)
from eurito_indicators.pipeline.text_processing import text_pipeline
from eurito_indicators.pipeline.topic_modelling import (
    post_process_model_clusters,
    train_model,
)
from eurito_indicators.pipeline.topic_utils import topic_regression
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    save_altair,
)

alt.data_transformers.disable_max_rows()

VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"


def make_id_lookups(fund_table):
    lookups = [
        fund_table.set_index("project_id")[var].to_dict()
        for var in ["source", "start_date"]
    ]
    return lookups


if __name__ == "__main__":

    driv = google_chrome_driver_setup()

    logging.info("Reading data")

    ec = get_cordis_covid()
    ukri = get_gtr_projects()
    wellc = get_wellcome()

    all_projects = pd.concat([ec, ukri, wellc]).reset_index(drop=True)

    logging.info("Processing data")
    conv = CurrencyConverter()

    converted = []

    for _, r in all_projects.iterrows():

        if pd.isnull(r["cost"]) is False:
            if r["currency"] == "EURO":
                converted.append(r["cost"])
            elif pd.isnull(r["start_date"]) == False:
                converted.append(conv.convert(r["cost"], r["currency"], "EUR"))
            else:
                converted.append(conv.convert(r["cost"], r["currency"], "EUR"))
        else:
            converted.append(np.nan)

    all_projects["cost_euro"] = converted

    all_projects["tokenised"] = text_pipeline(all_projects["abstract"], high_freq=0.99)

    id_funder_lookup, id_date_lookup = make_id_lookups(all_projects)

    id_funder_lookup = {str(k): v for k, v in id_funder_lookup.items()}
    id_date_lookup = {str(k): v for k, v in id_date_lookup.items()}

    logging.info("Training topic models")
    topic_mix_container = [
        post_process_model_clusters(
            train_model(all_projects["tokenised"], all_projects["project_id"].tolist()),
            top_level=0,
            cl_level=1,
            top_thres=0.8,
        )[0]
        for _ in range(30)
    ]

    topic_mix_combined = pd.concat(topic_mix_container, axis=1)

    topic_distances = pd.DataFrame(
        squareform(pdist(topic_mix_combined.T, metric="cosine")),
        index=topic_mix_combined.columns,
        columns=topic_mix_combined.columns,
    )

    topic_distances_long = topic_distances.stack()

    agg = AgglomerativeClustering(
        affinity="cosine", distance_threshold=0.6, n_clusters=None, linkage="average"
    )

    labels = agg.fit_predict(topic_mix_combined.T)

    topic_lookup = {topic_mix_combined.columns[n]: k for n, k in enumerate(labels)}

    topic_clusters = {
        cl: [k for k, v in topic_lookup.items() if v == cl]
        for cl in set(topic_lookup.values())
    }

    logging.info("Checking clusters")
    topic_distr = (
        topic_distances_long.reset_index(name="distance")
        .assign(bucket=lambda df: pd.cut(df["distance"], bins=100))
        .groupby("bucket")
        .size()
    )
    topic_distr = (topic_distr / topic_distr.sum()).cumsum()

    topic_clusters_lengths = [len(x) for x in topic_clusters.values()]

    fig, ax = plt.subplots(nrows=2)
    topic_distr = (
        topic_distr.reset_index(name="share")
        .assign(midpoint=lambda x: [el.mid for el in x["bucket"]])
        .set_index("midpoint")
        .drop(axis=1, labels=["bucket"])
    )

    topic_distr.plot(ax=ax[0], legend=False, title="Cumulative share of distances")

    ax[0].vlines(x=0.6, ymin=0, ymax=1, color="red", linestyle="--")

    ax[1].hist(topic_clusters_lengths, bins=30)
    ax[1].set_title("Distribution of lengths in clustered topics")
    ax[1].set_yscale("log")

    plt.tight_layout()

    plt.savefig(f"{FIG_PATH}/topic_distances.png", dpi=200)

    robust_clusters = [choice(v, 1)[0] for k, v in topic_clusters.items() if len(v) > 1]

    topic_mix_robust = topic_mix_combined[robust_clusters]
    topic_mix_robust = topic_mix_robust.loc[:, ~topic_mix_robust.columns.duplicated()]

    logging.info("Network analysis")
    topic_net = process_network(
        make_network_from_doc_term_matrix(
            topic_mix_robust.reset_index(drop=False), threshold=0.05, id_var="index"
        ),
        extra_edges=50,
    )
    comm = community_louvain.best_partition(topic_net[1])

    node_df = (
        pd.DataFrame(topic_net[0])
        .T.reset_index(drop=False)
        .rename(columns={0: "x", 1: "y", "index": "node"})
        .assign(node_name=lambda df: df["node"])
        .assign(node_label=lambda df: df["node_name"])
        .assign(
            node_size=lambda df: df["node_name"].map(
                topic_mix_robust.applymap(lambda x: x > 0.1).sum()
            )
        )
        .assign(node_color=lambda df: df["node_name"].map(comm))
    )

    funding_network = plot_altair_network(
        node_df,
        topic_net[1],
        node_color="node_color",
        node_label="node_label",
        node_size="node_size",
        **{
            "edge_weight_title": "Topic co-occurrences",
            "title": "Topic network in funding corpus",
            "node_color_title": "Topic Community",
            "node_size_title": "Number of occurrences",
        },
    ).properties(width=700, height=500)

    save_altair(
        ch_resize(funding_network), "funding_network", driver=driv, path=FIG_PATH
    )

    logging.info("Regression analysis")

    # %%
    reg_comp = topic_regression(
        topic_mix_robust,
        [id_funder_lookup[ind] for ind in topic_mix_robust.index],
        None,
    )

    # %%
    reg_table = pd.concat(reg_comp)
    topic_df = (
        reg_table.rename(columns={"index": "source", 0: "low", 1: "high"})
        .assign(community=lambda df: df["label"].map(comm))
        .assign(mean=lambda df: (df["low"] + df["high"]) / 2)
        .dropna(axis=0, subset=["community"])
        .sort_values(["community", "mean"], ascending=[True, False])
        .reset_index(drop=True)
        .assign(rank=lambda df: df.index)
    )

    topics_sorted = (
        topic_df.query("source=='ec'")
        .sort_values(["community", "mean"], ascending=[True, False])["label"]
        .tolist()
    )

    topic_df_long = topic_df.melt(
        id_vars=["source", "label", "community", "mean", "rank"]
    )

    funder_lookup = {
        "ukri": "UKRI",
        "ec": "European Commission",
        "wellcome": "Wellcome Trust",
    }

    topic_df_long["funder"] = topic_df_long["source"].map(funder_lookup)

    ch = (
        alt.Chart()
        .mark_point(filled=True, size=20, stroke="black", strokeWidth=0.1)
        .encode(
            y=alt.Y(
                "label",
                axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
            ),
            x=alt.X("mean", scale=alt.Scale(type="linear")),
            color="community:N",
            tooltip=["label"],
        )
    ).properties(width=300, height=600)

    line = (
        alt.Chart()
        .mark_line(strokeWidth=1.5)
        .encode(
            y=alt.Y(
                "label",
                title="Topic",
                axis=alt.Axis(grid=False, labels=False, ticks=False, labelFontSize=9),
                sort=alt.EncodingSortField("rank"),
            ),
            x=alt.X("value", title=["Topic regression coefficient"]),
            detail="label",
            tooltip=["label"],
            color=alt.Color(
                "community:N",
                sort=alt.EncodingSortField("discipline"),
                scale=alt.Scale(scheme="tableau20"),
                title="Topic community",
            ),
        )
    ).properties(width=300, height=600)

    rule = (
        alt.Chart()
        .transform_calculate(x="0")
        .mark_rule(strokeDash=[4, 1], stroke="black")
        .encode(x="x:Q")
    )

    funder_topic = alt.layer(line, ch, rule, data=topic_df_long).facet(
        alt.Facet("funder", title="Funder"), columns=3
    )

    save_altair(ch_resize(funder_topic), "funder_topic", driver=driv, path=FIG_PATH)

    logging.info("Evolution of activity")
    topic_long = (
        topic_mix_robust.stack()
        .reset_index(name="value")
        .assign(funder=lambda df: df["level_0"].map(id_funder_lookup))
        .assign(date=lambda df: df["level_0"].map(id_date_lookup))
        .dropna(axis=0, subset=["date"])
        .assign(
            month_year=lambda df: [datetime(x.year, x.month, 1) for x in df["date"]]
        )
    )

    # %%
    topic_long["value"] = topic_long["value"].apply(lambda x: x > 0.2)

    topic_trend = (
        topic_long.groupby(["funder", "month_year", "level_1"])["value"]
        .sum()
        .reset_index(drop=False)
        .assign(comm=lambda x: x["level_1"].map(comm))
        .query("month_year > '2020-01-01'")
        .query("month_year < '2021-07-01'")
    )

    # %%
    topical_trends = (
        (
            alt.Chart(topic_trend)
            .mark_bar(stroke="grey", strokeWidth=0.1, width=20)
            .encode(
                x="month_year",
                y="value",
                color=alt.Color("comm:N", scale=alt.Scale(scheme="tableau20")),
                tooltip=["level_1"],
                row="funder",
            )
        )
        .resolve_scale(y="independent")
        .properties(width=500, height=100)
    )

    save_altair(
        ch_resize(topical_trends), "funder_topic_trends", driver=driv, path=FIG_PATH
    )

    # # %%
    # comms_grouped = (
    #     pd.Series(comm).reset_index(drop=False).groupby(0)["index"].apply(lambda x: list(x))
    # )

    # for n, k in enumerate(sorted(comms_grouped.keys())):
    #     print(n)

    #     topics = comms_grouped.loc[k]

    #     tops = []

    #     for t in topics:

    #         tops.append([t, len(topic_mix_robust.loc[topic_mix_robust[t] > 0.1])])

    #     print(sorted(tops, key=lambda x: x[1], reverse=True))

    #     print("\n")

    # # %%
