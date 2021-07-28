# Script to produce Cordis related analytical charts

import logging
import warnings
from datetime import datetime

import altair as alt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cityblock

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.cordis_getters import (
    get_cluster_labels,
    get_cordis_clusters,
    get_cordis_organisations,
    get_cordis_projects,
    get_specter,
)
from eurito_indicators.pipeline.clustering_naming import (
    calculate_pairwise_distances,
    filter_pre_post_table,
    get_closest_documents,
    make_distance_to_clusters,
    make_doc_comm_lookup,
    make_pre_post_table,
    plot_participation_distance,
    plot_preparedness_response,
    plot_specialisation_robust,
    rank_org_distances,
    specialisation_robust,
)
from eurito_indicators.pipeline.processing_utils import (
    get_top_countries,
    make_bins,
    make_iso_country_lookup,
    make_lq,
)
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    make_altair_save_dirs,
    save_altair,
)

warnings.simplefilter(action="ignore", category=FutureWarning)

VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"

make_altair_save_dirs(FIG_PATH)

driv = google_chrome_driver_setup()


def get_labels_lookups():
    iso_lookup = make_iso_country_lookup()
    cluster_labels = get_cluster_labels()

    clean_var_lookup = {**iso_lookup, **cluster_labels}
    clean_var_lookup["non_covid"] = "Non-Covid related"
    return cluster_labels, clean_var_lookup


# Initial plot of activity
def plot_covid_cluster_activity(
    projs, cluster_lookup, cluster_labels, start_date="2019-01-01"
):
    """Point chart with specialisations and levels of activity by country"""

    projs_cov = (
        projs.query(f"start_date > '{start_date}'")
        .assign(
            cluster=lambda df: df["project_id"]
            .map(cluster_lookup)
            .map(cluster_labels)
            .fillna("Not covid")
        )
        .groupby(["coordinator_country", "cluster"])
        .size()
        .unstack()
        .fillna(0)
    )

    projs_lq_size = pd.concat(
        [make_lq(projs_cov).stack(), projs_cov.stack()], axis=1
    ).loc[focus_countries]
    projs_lq_size.columns = ["Relative specialisation", "Total"]

    projs_lq_size = projs_lq_size.reset_index(drop=False)
    projs_lq_size["country"] = projs_lq_size["coordinator_country"].map(
        clean_var_lookup
    )

    spec_chart = (
        alt.Chart(projs_lq_size.query("cluster!='Not covid'"))
        .mark_point(filled=True, stroke="black", strokeWidth=0.5)
        .encode(
            y=alt.Y(
                "country",
                title="Coordinating country",
                sort=alt.EncodingSortField(
                    "Relative specialisation", op="mean", order="descending"
                ),
                axis=alt.Axis(grid=True),
            ),
            x=alt.X(
                "Relative specialisation",
                title=["Relative specialisation", "(projects started since 2019)"],
            ),
            tooltip=["country", "cluster"],
            size=alt.Size("Total", title="Total projects"),
            color=alt.Color("cluster", title="Covid research cluster"),
        )
    )
    rul = (
        alt.Chart(projs_lq_size)
        .transform_calculate(x="1")
        .mark_rule(color="black", strokeDash=[2, 2])
        .encode(x="x:Q")
    )

    spec_ch_final = ch_resize((spec_chart + rul).properties(height=500, width=300))
    return spec_ch_final


def plot_relatedness_trends(projs, cluster_proximity_lookup, cluster_labels):
    """Plots evolution of projects that are close to a covid research cluster"""
    projs_proxim = (
        projs.assign(
            cluster_prox=lambda df: df["project_id"]
            .map(cluster_proximity_lookup)
            .map(cluster_labels)
        )
        .dropna(axis=0, subset=["cluster_prox", "start_date"])
        .assign(
            month_year=lambda df: [
                datetime(x.year, x.month, 1) for x in df["start_date"]
            ]
        )
    )

    proj_proximity_trends = (
        projs_proxim.groupby(["cluster_prox", "month_year"])
        .size()
        .reset_index(name="number")
    )

    proj_trends = (
        alt.Chart(proj_proximity_trends)
        .transform_window(mean="mean(number)", frame=[-3, 0], groupby=["cluster_prox"])
        .mark_bar(width=8)
        .encode(
            x=alt.X("month_year", title=None),
            y=alt.Y("mean:Q", title="Number of related projects"),
            color=alt.Color(
                "cluster_prox", sort="ascending", title="Covid research cluster"
            ),
        )
    ).properties(width=800, height=400)

    proj_trends_resized = ch_resize(proj_trends)
    return proj_trends_resized


# Analysis of distance distributions
def plot_distrs(dist_to_cluster, cluster_labels):
    """Plots the distribution of distances inside / outside a research cluster"""

    charts = []

    for c in dist_to_clusters.columns:

        in_c = cluster_assignments[c]

        # outside cluster
        bins_in = make_bins(
            dist_to_clusters.loc[~dist_to_clusters.index.isin(in_c), c]
        ).reset_index(name="freq")

        in_dist_distr = (
            alt.Chart(bins_in)
            .mark_bar(color="blue", opacity=0.5)
            .encode(x="index", y="freq")
        )

        bins_out = make_bins(
            dist_to_clusters.loc[dist_to_clusters.index.isin(in_c), c]
        ).reset_index(name="freq")
        out_dist_distr = (
            alt.Chart(bins_out)
            .mark_bar(color="orange", opacity=0.5)
            .encode(x="index", y="freq")
        )

        out_dist = dist_to_clusters.loc[~dist_to_clusters.index.isin(in_c)][c]

        x_2sd = np.mean(out_dist) - 2 * np.std(out_dist)

        ruler = (
            alt.Chart(bins_out)
            .transform_calculate(x=f"{x_2sd}")
            .mark_rule(stroke="green")
            .encode(x="x:Q")
        )

        ch = (in_dist_distr + out_dist_distr + ruler).properties(
            width=400, height=100, title=cluster_labels[c]
        )
        charts.append(ch)

    return alt.vconcat(*charts)


# proximity analysis


def make_document_relatedness(dist_to_clusters, cluster_assignments, cluster_labels):
    """Gets documents which are closest to a Covid research cluster"""
    close_to_clusters = {
        cl: get_closest_documents(dist_to_clusters, cl, cluster_assignments, sd_scale=2)
        for cl in range(len(cluster_labels.keys()))
    }
    cluster_proximity_lookup = make_doc_comm_lookup(close_to_clusters)
    return cluster_proximity_lookup


def make_prep_plot(reg_var="coordinator_country"):
    """Produces a cluster preparedness comparing specialisation in covid-related topics
    before and after the pandemic
    """

    combined_table = make_pre_post_table(
        projs, cluster_assignments, dist_to_clusters, sd=2, reg_var=reg_var
    )

    combined_table_focus = filter_pre_post_table(
        combined_table, focus_countries, reg_var=reg_var
    )

    prep_plot = ch_resize(
        plot_preparedness_response(
            combined_table_focus, clean_var_lookup, reg_var=reg_var
        )
    )

    return prep_plot


# Organisational analysis


def get_covid_ids(projs):
    """Returns covid-related ids in cordis data"""
    d_ids = set(
        projs.loc[
            (projs["covid_level"] != "non_covid") | (projs["has_covid_term"] == True)
        ]["project_id"]
    )
    return d_ids


def make_org_covid_representations(orgs, cluster_assignments, projs, doc_vectors):
    """Creates vectors representing organisational and covid research cluster
    positions in vector space
    """

    # When creating org representations, fcus on recent projects not including IDS

    covid_ids = get_covid_ids(projs)

    recent_projects = (
        set(
            projs.query("start_date>'2018/01/01'").query("start_date < '2020/01/01'")[
                "project_id"
            ]
        )
        - covid_ids
    )

    # Signature vector for all organisations excluding covid projects
    vector_org_merged = (
        doc_vectors.loc[doc_vectors.index.isin(recent_projects)]
        .reset_index(drop=False)
        .merge(orgs[["project_id", "id", "name"]], on=["project_id"], how="inner")
    )

    # %%
    # %%time
    org_signatures = (
        vector_org_merged.drop(axis=1, labels=["project_id"])
        .melt(id_vars=["id", "name"])
        .groupby(["id", "name", "variable"])["value"]
        .mean()
    )

    org_signatures_wide = org_signatures.unstack()

    # Covid research cluster vector representations
    covid_sig = pd.concat(
        [
            doc_vectors.loc[doc_vectors.index.isin(v)].mean()
            for k, v in cluster_assignments.items()
        ],
        axis=1,
    ).T

    return org_signatures_wide, covid_sig


def make_org_country(orgs):
    """Lookup between organisation and country"""
    return orgs.drop_duplicates("id").set_index("id")["country"].to_dict()


if __name__ == "__main__":

    # Read all the data
    logging.info("Reading data")
    projs = get_cordis_projects()
    doc_vectors = get_specter()
    cluster_assignments, cluster_name_lookup = get_cordis_clusters()
    cluster_names = list(cluster_name_lookup.values())
    orgs = get_cordis_organisations()

    focus_countries = get_top_countries(projs)

    cluster_labels, clean_var_lookup = get_labels_lookups()

    cluster_lookup = make_doc_comm_lookup(cluster_assignments, method="single")

    logging.info("Making specialisation in covid clusters")
    spec_ch_final = plot_covid_cluster_activity(projs, cluster_lookup, cluster_labels)
    save_altair(spec_ch_final, "cordis_specialisation", driver=driv, path=FIG_PATH)

    # Plot distribution of distances to cluster
    dist_to_clusters = make_distance_to_clusters(
        doc_vectors, cityblock, cluster_assignments
    )

    distance_distr_plot = plot_distrs(dist_to_clusters, cluster_labels)

    save_altair(
        ch_resize(distance_distr_plot), "dist_distribution", driver=driv, path=VAL_PATH
    )

    logging.info("Analysis of relatedness")
    cluster_proximity_lookup = make_document_relatedness(
        dist_to_clusters, cluster_assignments, cluster_labels
    )

    # Calculate robust specialisation
    specialisation_related = specialisation_robust(
        dist_to_clusters,
        [1.5, 2.5],
        cluster_assignments=cluster_assignments,
        projects=projs,
    )

    # Plot specialisation robustness
    sp_rob = plot_specialisation_robust(
        "coordinator_country",
        "project_lq",
        dist_to_clusters=dist_to_clusters,
        projs=projs,
        cluster_assignments=cluster_assignments,
        focus_countries=focus_countries,
        clean_var_lookup=clean_var_lookup,
    )

    save_altair(sp_rob, "specialisation_robustness", driver=driv, path=VAL_PATH)

    # Preparedness plot
    prep_plot = make_prep_plot()

    save_altair(prep_plot, "preparedness_plot", path=FIG_PATH, driver=driv)

    # Cluster-related activity trends
    relatedness_time_chart = plot_relatedness_trends(
        projs, cluster_proximity_lookup, cluster_labels
    )

    save_altair(
        relatedness_time_chart, "relatedness_trends", driver=driv, path=FIG_PATH
    )

    logging.info("Analysis of organisational distance")
    # Assign orgs to clusters
    orgs_in_cluster = {
        k: set(orgs.loc[orgs["project_id"].isin(v)]["id"])
        for k, v in cluster_assignments.items()
    }

    org_vectors, cluster_vectors = make_org_covid_representations(
        orgs, cluster_assignments, projs, doc_vectors
    )

    dists = []

    org_cluster_dist = calculate_pairwise_distances(org_vectors, cluster_vectors)
    org_cluster_dist["country"] = org_cluster_dist.index.get_level_values(0).map(
        make_org_country(orgs)
    )

    # Gets share of Covid participations at different distances from the cluster
    org_distances = pd.concat(
        [
            rank_org_distances(
                org_cluster_dist, cluster, orgs_in_cluster, cluster_labels
            )
            for cluster in range(6)
        ]
    )

    part_distances = ch_resize(
        plot_participation_distance(org_distances, focus_countries, clean_var_lookup)
    ).properties(width=300, height=300)

    save_altair(part_distances, "participation_distances", driver=driv, path=FIG_PATH)
