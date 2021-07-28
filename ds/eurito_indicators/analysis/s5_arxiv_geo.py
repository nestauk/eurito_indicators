# Geographical analysis of arXiv data

import logging
import re

import altair as alt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    get_cluster_ids,
    query_arxiv_institute,
)
from eurito_indicators.pipeline.geo_utils import make_shape, plot_choro
from eurito_indicators.pipeline.processing_utils import remove_diagonal
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    save_altair,
)
from eurito_indicators.utils.other_utils import clean_table


driv = google_chrome_driver_setup()
VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"


if __name__ == "__main__":
    logging.info("Reading data")

    inst = query_arxiv_institute()
    cluster_ids = get_cluster_ids()

    clean_clusters = {
        n: " ".join([x.capitalize() for x in re.sub("_", " ", n).split(" ")])
        for n in set(cluster_ids.values())
    }

    inst_covid = (
        inst.assign(covid_clust=lambda df: df["article_id"].map(cluster_ids))
        .dropna(axis=0, subset=["covid_clust"])
        .reset_index(drop=True)
    )

    country_totals = (
        inst_covid.query("is_multinational==False")
        .groupby(["country", "country_code", "covid_clust"])
        .size()
        .unstack(level=2)
        .assign(covid_total=lambda df: df.sum(axis=1))
        .fillna(0)
    )

    logging.info(len(set(inst_covid["country"])))

    logging.info(len(set(inst_covid["city"])))

    shapef_json = make_shape(country_totals)

    choro = plot_choro(shapef_json, "covid_total", "Total papers").properties(
        width=1000, height=600
    )

    logging.info("Plot points")
    city_lookup = (
        inst.drop_duplicates(["city", "country"])
        .set_index(["city", "country"])[["lng", "lat"]]
        .to_dict()
    )

    article_totals = (
        inst_covid.query("is_multinational==False")
        .groupby(["city", "country"])
        .size()
        .fillna(0)
        .reset_index(name="papers")
    )

    article_totals["longitude"], article_totals["latitude"] = [
        [
            city_lookup[var][(cit, count)]
            for cit, count in zip(article_totals["city"], article_totals["country"])
        ]
        for var in ["lng", "lat"]
    ]

    points = (
        alt.Chart(article_totals)
        .mark_point(
            filled=True, stroke="white", strokeWidth=0.5, size=20, color="darkblue"
        )
        .encode(
            longitude=alt.Longitude("longitude"),
            latitude=alt.Latitude("latitude"),
            size=alt.Size("papers"),
            tooltip=["city", "latitude", "longitude"],
        )
    )

    save_altair(ch_resize(choro + points), "choropleth", driver=driv, path=FIG_PATH)

    logging.info("Specialisation analysis")

    cluster_totals = (
        inst_covid.query("is_multinational==False")
        .groupby(["city", "covid_clust"])
        .size()
        .unstack(level=1)
        .fillna(0)
    )

    
    corr_mat = cluster_totals.apply(lambda x: x / x.sum()).corr()

    corr_mat.columns = corr_mat.columns.map(clean_clusters)
    corr_mat.index = corr_mat.index.map(clean_clusters)

    # Run agglomerative clustering to sort research clusters based on their
    # similarity
    f = AgglomerativeClustering(n_clusters=10)
    sorted_labels = [corr_mat.index[n] for n in f.fit_predict(corr_mat)]

    corr_mat_long = corr_mat.stack()
    corr_mat_long.index = corr_mat_long.index.rename(["c1", "c2"])
    corr_mat_long = corr_mat_long.reset_index(name="correlation")
    corr_mat_long = remove_diagonal(corr_mat_long, "c1", "c2", "correlation")


    colocation_base = (
        alt.Chart(corr_mat_long).encode(
            x=alt.X("c1", sort=sorted_labels, axis=alt.Axis(labelAngle=310)),
            y=alt.Y("c2", sort=sorted_labels),
        )
    ).properties(height=400, width=500)

    colocation_plot = colocation_base.mark_rect().encode(
        color=alt.Color(
            "correlation", scale=alt.Scale(scheme="redblue"), sort="descending"
        )
    )
    colocation_text = colocation_base.mark_text(fontSize=8).encode(
        text=alt.Text("correlation", format=".1f"),
        color=alt.condition(
            "datum.correlation>0.8 | datum.correlation<0.4  ",
            alt.value("white"),
            alt.value("black"),
        ),
    )

    corr_chart = ch_resize(colocation_plot + colocation_text)
    save_altair(corr_chart, "colocation_chart", driver=driv, path=FIG_PATH)

    logging.info("Concentration analysis")

    # Shares of activity accounted by different locations
    city_shares = cluster_totals.apply(lambda x: x / x.sum())

    thresholds = [1, 5, 10, 20, 50]

    total_shares_long = (
        pd.DataFrame(
            [
                [
                    city_shares[t].sort_values(ascending=False)[:n].sum()
                    for t in city_shares.columns
                ]
                for n in thresholds
            ],
            columns=city_shares.columns,
            index=thresholds,
        )
        .stack()
        .reset_index(name="share")
    )

    total_values_long = (
        pd.DataFrame(
            [
                [
                    cluster_totals[t].sort_values(ascending=False)[:n].sum()
                    for t in city_shares.columns
                ]
                for n in thresholds
            ],
            columns=city_shares.columns,
            index=thresholds,
        )
        .stack()
        .reset_index(name="total")
    )

    values_combined = pd.concat(
        [
            df.set_index(["level_0", "covid_clust"])
            for df in [total_shares_long, total_values_long]
        ],
        axis=1,
    ).reset_index(drop=False)

    values_combined = clean_table(values_combined, ["covid_clust"], clean_clusters)

    # Make plot
    share_base = alt.Chart(values_combined).encode(
        y=alt.Y(
            "covid_clust_clean",
            axis=alt.Axis(grid=True),
            sort=alt.EncodingSortField("share", op="mean", order="descending"),
        ),
        x=alt.X("share", axis=alt.Axis(format="%")),
    )

    share_comparison = (
        share_base.mark_point(
            filled=True, stroke="black", strokeWidth=0.5, shape="circle"
        )
        # .mark_bar()
        .encode(
            color=alt.Color(
                "level_0:O",
                scale=alt.Scale(scheme="reds"),
                sort="descending",
                title="position",
            ),
            size="total",
        )
    )

    save_altair(
        ch_resize(share_comparison), "geographical_shares", driver=driv, path=FIG_PATH
    )
