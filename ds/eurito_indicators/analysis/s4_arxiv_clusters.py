# Analysis of *rXiv clusters

# %%
import logging
import re
from datetime import datetime

import altair as alt
import pandas as pd
import statsmodels.api as sm
from numpy.random import choice
from scipy.spatial.distance import cityblock
from statsmodels.api import OLS, Poisson, ZeroInflatedPoisson

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    get_arxiv_articles,
    get_cluster_names,
    get_arxiv_tokenised,
    get_arxiv_topic_model,
    get_covid_papers,
    query_arxiv_institute,
)
from eurito_indicators.pipeline.clustering_naming import (
    k_check_clusters,
    make_distance_to_clusters,
    make_doc_comm_lookup,
)
from eurito_indicators.pipeline.processing_utils import make_lq
from eurito_indicators.pipeline.topic_modelling import post_process_model_clusters
from eurito_indicators.pipeline.topic_utils import make_topic_mix, train_topic_model
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    save_altair,
)
from eurito_indicators.utils.other_utils import clean_table

VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"


def plot_k_check_outputs(val_results, cluster_names):
    """
    Plots the results of a validation of clustering results using kmeans
    """

    logging.info("Cluster overlaps")
    cluster_check = (
        pd.concat([x[0] for x in kmeans_validation_results], axis=1)
        .mean(axis=1)
        .reset_index(name="co_occ")
        .assign(c1_name=lambda df: df["c1"].map(cluster_names))
        .assign(c2_name=lambda df: df["c2"].map(cluster_names))
    )
    hm = (
        alt.Chart(cluster_check)
        .mark_point(filled=True, stroke="black", strokeWidth=1)
        .encode(
            x=alt.X("c1_name:N", sort=alt.EncodingSortField("c1")),
            y=alt.Y("c2_name:N", sort=alt.EncodingSortField("c2")),
            size=alt.Size("co_occ", title="Number of co-occurrences"),
            color=alt.Color("co_occ", scale=alt.Scale(scheme="oranges")),
            tooltip=["c1_name", "c2_name"],
        )
    )

    logging.info("Correlations between assignment shares")
    dists_df = (
        pd.concat([x[1] for x in kmeans_validation_results], axis=1)
        .mean(axis=1)
        .reset_index(name="share_corr")
        .assign(c1_name=lambda df: df["c1"].map(cluster_names))
        .assign(c2_name=lambda df: df["c2"].map(cluster_names))
    )

    pl = (
        alt.Chart(dists_df)
        .mark_rect()
        .encode(
            x=alt.X("c1_name:N", sort=alt.EncodingSortField("c1")),
            y=alt.Y("c2_name:N", sort=alt.EncodingSortField("c2")),
            color="share_corr",
            tooltip=["c1_name", "c2_name", "share_corr"],
        )
    )

    logging.info("Distribution of correlations with other clusters")
    melted = (
        dists_df[["c1", "c2", "share_corr"]]
        .melt(id_vars=["share_corr"])
        .assign(cl_name=lambda df: df["value"].map(cluster_names))
    )

    sort_clusters = (
        melted.groupby("cl_name")["share_corr"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )

    boxp = (
        alt.Chart(melted)
        .mark_boxplot()
        .encode(y=alt.Y("cl_name:N", sort=sort_clusters), x="share_corr")
    )

    return hm, pl, boxp


def make_clean_cluster_names(cluster_names):
    clean_clusters = {
        k: " ".join([x.capitalize() for x in re.sub("_", " ", v).split(" ")])
        for k,v in cluster_names.items()
    }
    return clean_clusters


def tag_covid_cluster(table, cluster_lookup, cluster_name):

    t = table.assign(
        cluster=lambda df: df["article_id"].map(cluster_lookup).map(cluster_name)
    ).assign(is_covid=lambda df: ~df["cluster"].isna())
    return t


def tag_month_year(table, art):
    return table["article_id"].map(art.set_index("article_id")["month_year"].to_dict())


def make_temp_reg_table(inst_cov, all_arts, focus_countries):
    """Creates a regression table to analyse the link
    between research nationality, topic and timeliness of Covid-19 response
    """

    inst_cov["created"] = inst_cov["article_id"].map(
        all_arts.set_index("article_id")["created"]
    )

    number_collabs = inst_cov.groupby("article_id")["country"].apply(
        lambda x: len(set(x))
    )

    inst_cov["n_collabs"] = inst_cov["article_id"].map(number_collabs)

    reg_data = (
        inst_cov.query("is_covid==True")
        .query("month_year < '2021-01-01'")
        .query("month_year >= '2020-01-01'")
        .copy()[["country", "cluster", "month_year", "created", "n_collabs"]]
        .reset_index(drop=True)
    )
    reg_data["y"] = [x.month for x in reg_data["month_year"]]
    reg_data["time_since_cov"] = [
        (x - datetime(2019, 12, 30)).days for x in reg_data["created"]
    ]

    reg_data = reg_data.loc[reg_data["country"].isin(focus_countries)].reset_index(
        drop=True
    )

    return reg_data


def time_reg_comparison(reg_data):

    X_count = sm.add_constant(pd.get_dummies(reg_data["country"]))

    X_clust = sm.add_constant(
        pd.concat(
            [
                pd.get_dummies(reg_data["country"]),
                pd.get_dummies(reg_data["cluster"]),
                reg_data["n_collabs"],
            ],
            axis=1,
        )
    )

    results = [
        OLS(endog=reg_data["time_since_cov"], exog=exog).fit()
        for exog in [X_count, X_clust]
    ]

    return results


def make_comparison_reg(arts, cluster, clust_assign, cluster_control):
    """Regression analysis comparing citations and collaboration levels
    between covid and non-covid papers
    """

    ids = list(clust_assign[cluster]) + list(cluster_control[cluster])
    logging.info(len(ids))

    arts_sel = (
        arts.loc[arts["article_id"].isin(ids)]
        .reset_index(drop=True)
        .dropna(axis=0, subset=["citation_count", "abstract"])
    )

    arts_sel["is_covid"] = arts_sel["article_id"].isin(clust_assign[cluster])

    # Citation analysis
    exog = arts_sel["is_covid"].astype(float)

    cit_res = ZeroInflatedPoisson(
        endog=arts_sel["citation_count"].astype(float), exog=exog
    ).fit()

    collab_b = (
        inst_cov.loc[inst_cov["article_id"].isin(arts_sel["article_id"])]
        .groupby("article_id")
        .apply(lambda x: len(set(x["country"])))
    )

    arts_sel["n_collab"] = arts_sel["article_id"].map(collab_b)

    # Collaboration analysis
    arts_sel_2 = arts_sel.dropna(axis=0, subset=["n_collab"])
    exog_2 = sm.add_constant(arts_sel_2["is_covid"]).astype(float)

    collab_res = Poisson(endog=arts_sel_2["n_collab"].astype(float), exog=exog_2).fit()

    return cit_res, collab_res, arts_sel


def plot_regression_coefficients(long):
    """Plots regression confidence intervals"""
    reg_int = (
        alt.Chart(long)
        .mark_line(color="red")
        .encode(
            y=alt.Y(
                "name",
                sort=alt.EncodingSortField("value", "mean", order="descending"),
                title="Reseach cluster",
            ),
            x=alt.X("value", title="Confidence interval"),
            detail="name",
        )
    )
    hor = (
        alt.Chart(long)
        .transform_calculate(x="0")
        .mark_rule(color="black", strokeDash=[2, 2])
        .encode(x="x:Q")
    )

    return reg_int + hor


if __name__ == "__main__":

    driv = google_chrome_driver_setup()
    logging.info("Reading data")

    arx_tm = get_arxiv_topic_model()
    arts = get_covid_papers()
    cluster_names = get_cluster_names()
    clean_names = make_clean_cluster_names(cluster_names)

    tm, cl = post_process_model_clusters(
        model=arx_tm[0], top_level=0, cl_level=1, top_thres=0.7
    )

    clust_assign = {k: [el[0] for el in v] for k, v in cl.items()}
    paper_cluster_lookup = {k[0]: v for k, v in make_doc_comm_lookup(cl).items()}

    cov_cl = (
        arts.copy()
        .assign(cluster=lambda df: df["article_id"].map(paper_cluster_lookup))
        .dropna(axis=0, subset=["cluster"])
        .reset_index(drop=True)
        .assign(tokenised=lambda df: arx_tm[3])
    )

    logging.info("K-check cluster outputs")

    kmeans_validation_results = [
        k_check_clusters(tm, n_clust=k, cluster_assignments=clust_assign)
        for k in [23] * 5 + [15] * 5 + [30] * 5
    ]

    heatmap, corr_shares, corr_distr = plot_k_check_outputs(
        kmeans_validation_results, cluster_names
    )

    save_altair(heatmap, "cluster_cooccurrences", driver=driv, path=FIG_PATH)
    save_altair(corr_shares, "cluster_correlations", driver=driv, path=FIG_PATH)
    save_altair(corr_distr, "correlation_distributions", driver=driv, path=FIG_PATH)

    cov_cl["cluster_name"] = cov_cl["cluster"].map(clean_names)
    cov_cl = cov_cl.loc[cov_cl["year"] >= 2020]

    logging.info("Descriptive analysis")
    # Distribution of sources over clusters
    cluster_source = (
        cov_cl.groupby("cluster_name")["article_source"]
        .value_counts()
        .reset_index(name="article_n")
    )

    source_ch = (
        alt.Chart(cluster_source)
        .mark_bar()
        .encode(
            y=alt.Y(
                "cluster_name",
                sort=alt.EncodingSortField("article_n", order="descending"),
            ),
            x="article_n",
            color="article_source",
        )
    ).properties(height=500, width=300)

    save_altair(ch_resize(source_ch), "cluster_sources", driver=driv, path=FIG_PATH)

    logging.info("Evolution of activity")

    cluster_time = (
        cov_cl.groupby("cluster_name")["month_year"]
        .value_counts(normalize=True)
        .reset_index(name="article_n")
    )

    #cluster_time = clean_table(cluster_time, ["cluster_name"], clean_names)

    # Gets the countries that responded fastest to Covid-19
    timeliness_studies = (
        cluster_time.pivot_table(
            index="month_year", columns="cluster_name", values="article_n"
        )
        .fillna(0)
        .cumsum()
        .iloc[6]
        .sort_values(ascending=False)
        .index.tolist()
    )

    cluster_agg = cov_cl["month_year"].value_counts(normalize=True)

    cluster_time["average"] = cluster_time["month_year"].map(cluster_agg)

    source_ch = (
        alt.Chart(cluster_time)
        .mark_line(point=True, size=2)
        .encode(
            y=alt.Y(
                "article_n", title=["Share", "of papers"], axis=alt.Axis(format="%")
            ),
            x=alt.X("month_year", axis=alt.Axis(format="%b-%Y")),
            tooltip=["cluster_name", "article_n"],
        )
    ).properties(height=70, width=120)

    source_avg = (
        alt.Chart(cluster_time)
        .mark_line(color="darkorange", strokeWidth=1)
        .encode(
            y=alt.Y("average"), x=alt.X("month_year", axis=alt.Axis(format="%b-%Y"))
        )
    ).properties(height=70, width=120)

    topic_evolution = ch_resize(
        (source_ch + source_avg)
        .facet(
            facet=alt.Facet(
                "cluster_name", sort=timeliness_studies, title="Topical cluster"
            ),
            columns=5,
        )
        .configure_point(size=15)
    )

    save_altair(topic_evolution, "arxiv_topic_evolution", driver=driv, path=FIG_PATH)

    #### CONTINUE HERE

    logging.info("International analysis")
    logging.info("Read data")
    all_arts = get_arxiv_articles().query("article_source!='cord'")
    inst = query_arxiv_institute().query("is_multinational == 0").reset_index(drop=True)
    inst_cov = tag_covid_cluster(inst, paper_cluster_lookup, clean_names)
    inst_cov["month_year"] = tag_month_year(inst_cov, all_arts)

    inst_cov = (
        inst_cov.query("month_year>='2020-01-01'")
        # .query("month_year<='2021-02-01'")
        .reset_index(drop=True)
    )

    focus_countries = (
        inst_cov.query("is_covid==True")["country"].value_counts().iloc[:30].index
    )

    country_shares = (
        inst_cov.groupby(["month_year", "is_covid", "country"])
        .size()
        .unstack(level=[1, 2])
        .fillna(0)
        .apply(lambda x: x / x.sum())
        .stack(level=[0, 1])
        .reset_index(name="paper_shares")
    )

    country_shares = country_shares.loc[
        country_shares["country"].isin(focus_countries)
    ].reset_index(drop=True)

    countries_sorted = (
        country_shares.query("month_year<'2020-06-01'")
        .query("is_covid==True")
        .groupby("country")["paper_shares"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # %%
    country_shares = clean_table(
        country_shares, ["is_covid"], {True: "Covid", False: "Not Covid"}
    )

    country_chart = (
        (
            alt.Chart(country_shares)
            .mark_line(point=True, size=1)
            .transform_window(
                mean="mean(paper_shares)",
                frame=[-1, 1],
                groupby=["is_covid_clean", "country"],
            )
            .encode(
                x=alt.X("month_year", title=None, axis=alt.Axis(format="%b%y")),
                y=alt.Y(
                    "mean:Q", axis=alt.Axis(format="%"), title=["Share", "of papers"]
                ),
                color=alt.Color("is_covid_clean", title="Category"),
                facet=alt.Facet(
                    "country", columns=5, sort=countries_sorted, title="Country"
                ),
            )
        )
        .properties(height=70, width=120)
        .configure_point(size=10)
    )

    save_altair(
        ch_resize(country_chart), "arxiv_country_trends", driver=driv, path=FIG_PATH
    )

    logging.info("Analysis of specialisation")
    focus_countries = (
        inst_cov.query("is_covid==True")["country"].value_counts().iloc[:30].index
    )

    totals = (
        inst_cov.dropna(axis=0, subset=["cluster"])
        .groupby(["country", "cluster"])
        .size()
        .unstack()
        .fillna(0)
        .stack()
        .loc[focus_countries]
    )
    lq = (
        make_lq(
            inst_cov.dropna(axis=0, subset=["cluster"])
            .groupby(["country", "cluster"])
            .size()
            .unstack()
            .fillna(0)
        )
        .stack()
        .loc[focus_countries]
    )

    countries_sorted = totals.unstack(level=0).sum().index.tolist()
    clusters_sorted = (
        totals.unstack(level=1).sum().sort_values(ascending=False).index.tolist()
    )

    combi = pd.concat([totals, lq], axis=1)
    combi.columns = ["total", "specialisation"]
    combi = combi.reset_index(drop=False)

    # Plot heatmap
    heatmap = (
        alt.Chart(combi.query("total>0"))
        .mark_point(filled=True, shape="square", stroke="darkgrey", strokeWidth=0.5)
        .encode(
            y=alt.Y("country", sort=countries_sorted),
            x=alt.X("cluster", sort=clusters_sorted, axis=alt.Axis(labelAngle=320)),
            size=alt.Size("total", scale=alt.Scale(type="log")),
            tooltip=["country", "cluster"],
            color=alt.X(
                "specialisation",
                scale=alt.Scale(scheme="redblue", type="log", domainMid=1),
                sort="descending",
            ),
        )
    )

    save_altair(heatmap, "country_specialisation", driver=driv, path=FIG_PATH)

    logging.info("Regression analysis")

    inst_cov["created"] = inst_cov["article_id"].map(
        all_arts.set_index("article_id")["created"]
    )

    reg_data = make_temp_reg_table(inst_cov, all_arts, focus_countries)
    reg_results = time_reg_comparison(reg_data)
    regression_coefficients = pd.concat(
        [
            reg_results[n].conf_int().loc[focus_countries].stack()
            for n, name in enumerate(["Country", "Cluster"])
        ],
        axis=1,
    )

    regression_coefficients.columns = ["country", "cluster"]

    regression_df = regression_coefficients.stack().reset_index(name="coefficient")

    # %%
    ch = (
        alt.Chart()
        .mark_line()
        .encode(
            y=alt.Y(
                "level_2",
                axis=alt.Axis(ticks=False, labels=False, title=None),
                scale=alt.Scale(domain=["country", "cluster"]),
            ),
            color=alt.Color("level_2", scale=alt.Scale(domain=["country", "cluster"])),
            x=alt.X("coefficient", title="Time coefficient"),
            detail="level_0",
        )
    ).properties(height=15, width=100)

    hor = (
        alt.Chart().transform_calculate(x="1").mark_rule(color="black").encode(x="x:Q")
    )

    regression_comparison = alt.layer(ch, hor, data=regression_df).facet(
        facet=alt.Facet(
            "level_0",
            sort=alt.EncodingSortField("coefficient", op="mean"),
            title=None,
            header=alt.Header(orient="top"),
        ),
        columns=3,
    )

    logging.info("Covid / non covid regression comparison")
    tok = get_arxiv_tokenised()

    arts_2020 = (
        all_arts.query("article_source!='cord'")
        .query("month_year < '2020-09-01'")
        .query("month_year > '2020-03-01'")
        .reset_index(drop=True)
        .assign(tok=lambda df: df["article_id"].map(tok))
        .dropna(axis=0, subset=["tok"])
    )

    mdl, ids = train_topic_model(150, arts_2020["tok"], arts_2020["article_id"])
    topic_mix = make_topic_mix(mdl, 150, ids)

    # Measure distance between all documents and cluster centroids
    centroids = (
        topic_mix.assign(cl=lambda df: df.index.map(paper_cluster_lookup))
        .dropna(axis=0, subset=["cl"])
        .melt(id_vars="cl")
        .groupby(["cl", "variable"])["value"]
        .mean()
        .unstack()
    )

    arxiv_dist_to_clust = make_distance_to_clusters(topic_mix, cityblock, clust_assign)

    arx_dist_not_covid = arxiv_dist_to_clust.loc[
        ~arxiv_dist_to_clust.index.isin(set(arts["article_id"]))
    ]

    logging.info("Get controls by cluster")
    cluster_control = {
        c: set(arx_dist_not_covid.sort_values(c, ascending=True).index[:500])
        for c in arx_dist_not_covid.columns
    }

    covid_comparisons = [
        make_comparison_reg(arts_2020, cl, clust_assign, cluster_control)
        for cl in range(23)
    ]

    cits, collabs = [
        [
            x[n].conf_int().assign(name=name)
            for x, name in zip(covid_comparisons, clean_names.values())
        ]
        for n in [0, 1]
    ]

    cit_long = (
        pd.concat(cits)
        .query("index!='const'")
        .sort_values(0, ascending=False)
        .reset_index(drop=True)
        .melt(id_vars="name")
    )

    cit_reg_plot = plot_regression_coefficients(cit_long).properties(
        title="Regression analysis: Citation counts"
    )

    logging.info("plotting results")
    coll_long = (
        pd.concat(collabs)
        .query("index!='const'")
        .sort_values(0, ascending=False)
        .reset_index(drop=True)
        .melt(id_vars="name")
    )

    collab_reg_plot = plot_regression_coefficients(coll_long).properties(
        title="Regression analysis: Number of countries"
    )

    for plot, name in zip([cit_reg_plot, collab_reg_plot], ["cit_reg", "collab_reg"]):
        save_altair(
            ch_resize(plot),
            name,
            driver=driv,
            path=FIG_PATH,
        )

    logging.info("Compare covid and control trends")
    arts_trends = pd.concat(
        [
            el[2]
            .groupby(["is_covid", "month_year"])
            .size()
            .unstack(level=0)
            .apply(lambda x: x / x.sum())
            .stack()
            .reset_index(name="paper_share")
            .assign(name=name)
            for el, name in zip(covid_comparisons, clean_names.values())
        ],
        axis=0,
    ).reset_index(drop=True)

    contrast_chart = (
        (
            alt.Chart(arts_trends)
            .mark_line(point=True, size=1.5)
            .encode(
                x="month_year",
                y="paper_share",
                color="is_covid",
                facet=alt.Facet("name", columns=5),
            )
        )
        .properties(width=100, height=100)
        .configure_point(size=10)
    )

    save_altair(
        ch_resize(contrast_chart), "control_treat_contrast", driver=driv, path=FIG_PATH
    )

    comparison_correlation = (
        arts_trends.groupby("name")
        .apply(
            lambda x: x.pivot_table(
                index="month_year", columns="is_covid", values="paper_share"
            )
            .corr()
            .iloc[0, 1]
        )
        .sort_values(ascending=False)
    )

    logging.info(comparison_correlation)

    for n, comp in enumerate(covid_comparisons):

        logging.info(clean_names[n])

        cov, no_cov = [comp[2].query(f"is_covid=={v}") for v in [True, False]]
        logging.info("Covid papers")
        for c in choice(list(cov["title"]), 5):
            logging.info(c)
        print("\n")
        
        logging.info("Covid papers")
        for c in choice(list(no_cov["title"]), 5):
            logging.info(c)
        print("\n")

    # %%
