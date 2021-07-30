import logging
from itertools import chain

import altair as alt
import geopandas as gp
import numpy as np
import pandas as pd
import tomotopy as tp
import yaml

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    get_ai_results,
    get_article_categories,
    get_arxiv_articles,
    get_arxiv_tokenised,
    get_arxiv_w2v,
    get_cluster_ids,
    query_arxiv_institute,
)
from eurito_indicators.pipeline.processing_utils import make_bins, make_lq
from eurito_indicators.pipeline.topic_utils import make_topic_mix

NUTS_SHAPE_PATH = f"{PROJECT_DIR}/inputs/data/nuts_2016"


def make_ai_ids():
    """Function to extract AI Ids from the categories and expanded paper
    list files
    """
    ai = get_ai_results()

    cats = get_article_categories()

    ai_cats = set(["cs.AI", "cs.NE", "stat.ML", "cs.LG"])

    ai_core_papers = set(cats.loc[cats["category_id"].isin(ai_cats)]["article_id"])

    ai_papers_expanded = set(chain(*ai[0].values()))

    all_ai_ids = ai_core_papers.union(ai_papers_expanded)

    return all_ai_ids


def make_institutes_rev_geocoded():
    inst = (
        query_arxiv_institute()
        .query("is_multinational==False")
        .drop(
            axis=1, labels=["nuts_level1_code", "nuts_level2_code", "nuts_level3_code"]
        )
    )

    all_nuts = gp.read_file(f"{NUTS_SHAPE_PATH}/NUTS_RG_10M_2016_4326.geojson")

    inst_coords = inst.drop_duplicates("grid_id")[
        ["grid_id", "name", "lat", "lng"]
    ].reset_index(drop=True)

    inst_nuts_geo = gp.GeoDataFrame(
        inst_coords, geometry=gp.points_from_xy(inst_coords["lng"], inst_coords["lat"])
    )
    inst_nuts_geo.crs = 4326

    inst_table = gp.sjoin(inst_nuts_geo, all_nuts, op="within")
    inst_nuts_lookup = (
        inst_table.pivot_table(
            index="grid_id", columns="LEVL_CODE", values="NUTS_ID", aggfunc="max"
        )
        .rename(
            columns={
                n: v
                for n, v in enumerate(
                    [
                        "nuts_level0_code",
                        "nuts_level1_code",
                        "nuts_level2_code",
                        "nuts_level3_code",
                    ]
                )
            }
        )
        .reset_index(drop=False)
    )

    inst_geo = inst.merge(inst_nuts_lookup, on="grid_id")

    return inst_geo


def fetch_template_schema(name="article_base"):

    with open(
        f"{PROJECT_DIR}/outputs/data/processed/_articles/{name}_schema.yaml", "r"
    ) as infile:
        return yaml.safe_load(infile)


def make_indicator(
    table,
    category,
    clean_name,
    nuts_level,
    indicator_type,
    suffix="count",
    nuts_spec=2016,
    var_type="categorical",
):
    """Takes combined tables and splits them into"""

    split_tables = []
    schema_list = []

    if var_type == "categorical":

        for c in sorted(set(table[category])):

            t = (
                table.query(f"{category}=='{c}'")
                .reset_index(drop=True)
                .rename(
                    columns={
                        0: f"{c}_{suffix}",
                        f"nuts_level{nuts_level}_code": "nuts_id",
                    }
                )
                .assign(nuts_year_spec=nuts_spec)
            )[["year", "nuts_id", "nuts_year_spec", f"{c}_{suffix}"]]
            split_tables.append(t)

            if c == "cord":
                c = "cord-19"

            schema = make_schema(
                indicator_type,
                category=c,
                clean_name=clean_name,
                nuts_level=nuts_level,
                suffix=suffix,
            )
            schema_list.append(schema)

    if var_type == "dummy":

        t = (
            table.query(f"{category}==True")
            .drop(axis=1, labels=[category])
            .reset_index(drop=True)
            .rename(
                columns={
                    0: f"{category}_{suffix}",
                    f"nuts_level{nuts_level}_code": "nuts_id",
                }
            )
            .assign(nuts_year_spec=nuts_spec)
        )[["year", "nuts_id", "nuts_year_spec", f"{category}_{suffix}"]]
        split_tables.append(t)

        schema = make_schema(
            indicator_type,
            category=category,
            clean_name=clean_name,
            nuts_level=nuts_level,
            suffix=suffix,
        )
        schema_list.append(schema)

    if var_type == "value":
        t = (
            table.rename(
                columns={
                    category: f"{category}_{suffix}",
                    f"nuts_level{nuts_level}_code": "nuts_id",
                }
            ).assign(nuts_year_spec=nuts_spec)
        )[["year", "nuts_id", "nuts_year_spec", f"{category}_{suffix}"]]
        split_tables.append(t)

        schema = make_schema(
            indicator_type,
            category=category,
            clean_name=clean_name,
            nuts_level=nuts_level,
            suffix=suffix,
        )
        schema_list.append(schema)

    return split_tables, schema_list


# %%
def make_schema(indicator_type, category, clean_name, nuts_level, suffix="count"):
    if indicator_type == "article_sources":
        schema = fetch_template_schema()
        schema["title"] = f"Number of participations in {clean_name} articles"
        schema[
            "subtitle"
        ] = f"Number participations in {clean_name} articles by institutions in the location"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {clean_name} articles"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "clusters":
        schema = fetch_template_schema("articles_clusters_base")
        schema["is_experimental"] = True
        schema["title"] = f"Number of participations in {clean_name} preprints"
        schema[
            "subtitle"
        ] = f"Number participations in {clean_name} preprints by institutions in the location (research clusters identified through a topic model of article abstracts)"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {clean_name} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "clusters_specialisation":
        schema = fetch_template_schema("articles_clusters_specialisation_base")
        schema["is_experimental"] = True
        schema["title"] = f"Relative specialisation in {clean_name} preprints"
        schema[
            "subtitle"
        ] = f"Relative specialisation in {clean_name} preprints by institutions in the location (research clusters identified through a topic model of article abstracts, specialisation calculated as a location quotient taking into account non-covid activity)"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Relative specialisation in {clean_name} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "ai":
        schema = fetch_template_schema("articles_clusters_base")
        schema["is_experimental"] = True
        schema["framework"] = "artificial_intelligence"
        schema["title"] = f"Number of participations in {clean_name} preprints"
        schema[
            "subtitle"
        ] = f"Number participations in {clean_name} preprints by institutions in the location ({clean_name} papers identified through a semantic analysis of article abstracts)"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {clean_name} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "ai_covid_share":
        schema = fetch_template_schema("articles_clusters_base")
        schema["is_experimental"] = True
        schema["framework"] = "artificial_intelligence"
        schema["title"] = f"Share of {clean_name} in Covid preprints"
        schema[
            "subtitle"
        ] = f"{clean_name} as a share of all participations in Covid-19 preprints by institutions in the location ({clean_name} papers identified through a semantic analysis of article abstracts)"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"AI as a share of aall {clean_name} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"

    return schema


def make_save_indicator_tables(
    dummy_nuts_table,
    indicator_type,
    category,
    clean_name,
    var_type="dummy",
    suffix="count",
):

    for n, table in enumerate(dummy_nuts_table):
        tables, schemas = make_indicator(
            table,
            indicator_type=indicator_type,
            clean_name=clean_name,
            category=category,
            nuts_level=n,
            var_type=var_type,
            suffix=suffix,
        )

        for tb, sch in zip(tables, schemas):

            table_name = sch["schema"]["value"]["id"]
            nuts_level = sch["region"]["level"]

            print("\n")

            logging.info(tb.head())
            logging.info("\n")
            tb.to_csv(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.csv"
            )

            with open(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.yaml",
                "w",
            ) as outfile:
                yaml.safe_dump(sch, outfile)


def specialisation_indicator(inst, variable, nuts_level, years=range(2015, 2021)):

    lqs = []

    for y in years:

        year_totals = (
            inst.query(f"year=={y}")
            .groupby([f"nuts_level{nuts_level}_code", variable])
            .size()
            .unstack(level=1)
            .fillna(0)
        )
        year_lq = (
            make_lq(year_totals)
            .drop(axis=1, labels=[False])
            .stack()
            .reset_index(drop=False)
            .drop(axis=1, labels=[variable])
            .rename(columns={0: variable})
            .assign(year=y)
        )
        lqs.append(year_lq)

    return pd.concat(lqs)


if __name__ == "__main__":
    logging.info("Getting data")

    arts = get_arxiv_articles()
    ai_ids = make_ai_ids()
    tok = get_arxiv_tokenised()
    arx_w2v = get_arxiv_w2v()
    covid_ids = get_cluster_ids()

    ai_tok = {k: v for k, v in tok.items() if (k in ai_ids) & (len(v) > 0)}
    ai_tok_text = list(ai_tok.values())

    inst_geo = make_institutes_rev_geocoded()

    logging.info("Training topic model")
    v = 150
    mdl = tp.LDAModel(k=v, seed=123)

    for t in ai_tok_text:
        mdl.add_doc(t)

    for i in range(0, 150, 10):
        mdl.train(10)
        print("Iteration: {}\tLog-likelihood: {}".format(i, mdl.ll_per_word))

    logging.info(mdl.summary())

    topic_names = [[x[0] for x in mdl.get_topic_words(k, top_n=5)] for k in range(v)]

    sims = (
        pd.DataFrame(
            [
                np.mean(
                    arx_w2v.wv.similarity(
                        [el for el in t if el in arx_w2v.wv], "artificial_neural"
                    )
                )
                for t in topic_names
            ],
            index=["_".join(t) for t in topic_names],
        )
        .reset_index(drop=False)
        .rename(columns={0: "mean_similarity"})
    )

    # %%
    sim = (
        alt.Chart(sims)
        .mark_bar()
        .encode(
            y=alt.Y(
                "index",
                sort=alt.EncodingSortField("mean_similarity", order="descending"),
                axis=alt.Axis(labels=False, ticks=False),
            ),
            x="mean_similarity",
            tooltip=["index"],
            color="mean_similarity",
        )
        .properties(height=500, width=200)
    )

    sim_bins = make_bins(sims["mean_similarity"], bins=20).reset_index(name="density")

    alt.Chart(sim_bins).mark_bar().encode(x="index", y="density", color="density")

    dl_topics = sims.loc[
        sims["mean_similarity"]
        > sims["mean_similarity"].mean() + 1.5 * (sims["mean_similarity"].std())
    ]["index"].tolist()

    logging.info(dl_topics)

    dl_topics.remove("network_neuron_neural_brain_learning")

    topic_mix = make_topic_mix(mdl, doc_indices=ai_tok.keys(), num_topics=150)

    sim_freqs = []

    for t in dl_topics:
        print(t)
        b = make_bins(topic_mix[t]).reset_index(name="density").assign(name=t)
        sim_freqs.append(b)

    # %%
    topic_distr = pd.concat(
        [
            x.sort_values("index", ascending=True).assign(
                cs=lambda df: df["density"].cumsum()
            )
            for x in sim_freqs
        ]
    )

    topic_distr_chart = (
        alt.Chart(topic_distr)
        .mark_line(point=True)
        .encode(x="index", y="cs", color="name", tooltip=["name"])
    ).configure_point(size=5)
    topic_distr_chart

    logging.info("Finding deep learning papers")
    dl_paper = set(
        chain(
            *[
                topic_mix.loc[
                    topic_mix[t] > (topic_mix[t].mean() + topic_mix[t].std() * 2)
                ].index
                for t in dl_topics
            ]
        )
    )

    logging.info("Making indicators")
    arts_sel = (
        arts.query("article_source!='cord'")
        .dropna(axis=0, subset=["month_year"])
        .assign(year=lambda df: [int(x.year) for x in df["month_year"]])
        .query("year>=2000")
        .query("year <= 2021")
        .reset_index(drop=True)
        .assign(ai=lambda df: df["article_id"].isin(ai_ids))
        .assign(dl=lambda df: df["article_id"].isin(dl_paper))
        .assign(covid=lambda df: df["article_id"].isin(set(covid_ids.keys())))
    )

    arts_lookup = arts_sel.set_index("article_id")[
        ["ai", "dl", "covid", "year"]
    ].to_dict()

    (
        inst_geo["artificial_intelligence"],
        inst_geo["deep_learning"],
        inst_geo["covid"],
        inst_geo["year"],
    ) = [
        inst_geo["article_id"].map(arts_lookup[var])
        for var in ["ai", "dl", "covid", "year"]
    ]
    inst_geo_2 = inst_geo.loc[
        inst_geo["article_id"].isin(arts_sel["article_id"])
    ].reset_index(drop=False)

    ai_counts, dl_counts = [
        [
            inst_geo.groupby(["year", var, f"nuts_level{n}_code"])
            .size()
            .dropna()
            .reset_index(drop=False)
            for n in [0, 1, 2, 3]
        ]
        for var in ["artificial_intelligence", "deep_learning"]
    ]

    make_save_indicator_tables(
        ai_counts, "ai", "artificial_intelligence", "Artificial Intelligence"
    )

    # %%
    make_save_indicator_tables(dl_counts, "ai", "deep_learning", "Deep Learning")

    logging.info("AI and covid")
    inst_geo["ai_covid"] = inst_geo["covid"] & inst_geo["artificial_intelligence"]

    ai_covid_counts = [
        inst_geo.query("year>=2020")
        .groupby(["year", "ai_covid", f"nuts_level{n}_code"])
        .size()
        .dropna()
        .reset_index(drop=False)
        for n in [0, 1, 2, 3]
    ]

    make_save_indicator_tables(
        ai_covid_counts, "ai", "ai_covid", "AI application to Covid-19"
    )

    ai_covid_shares = [
        inst_geo.query("year>=2020")
        .query("covid==True")
        .groupby(["year", f"nuts_level{n}_code"])["ai_covid"]
        .mean()
        .dropna()
        .reset_index(drop=False)
        for n in [0, 1, 2, 3]
    ]

    make_save_indicator_tables(
        ai_covid_shares,
        "ai_covid_share",
        "ai_covid",
        "AI",
        var_type="value",
        suffix="share",
    )
