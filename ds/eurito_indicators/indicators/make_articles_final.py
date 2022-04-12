# Make article indicators

import datetime
import json
import logging
import os
import pickle
import re
from io import BytesIO
from zipfile import ZipFile

import geopandas as gp
import numpy as np
import pandas as pd
import requests
import yaml

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    get_arxiv_articles,
    get_cluster_ids,
    query_arxiv_institute,
)
from eurito_indicators.pipeline.processing_utils import make_lq

# PATHS ETC
NUTS_SHAPE_PATH = f"{PROJECT_DIR}/inputs/data/nuts"

arx_clusters = get_cluster_ids()

nuts_lookup = {
    "2010": set(range(2010, 2013)),
    "2013": set(range(2013, 2016)),
    "2016": set(range(2016, 2021)),
    "2021": [2021],
}

# FUNCTIONS


def make_clean_clusters():
    """Creates a lookup between data variable names and clean variable names"""

    CLEAN_CLUSTERS = {
        n: " ".join([x.capitalize() for x in re.sub("_", " ", n).split(" ")])
        for n in set(arx_clusters.values())
    }

    AI_CLUSTERS = {}

    AI_CLUSTERS["deep_learning"] = "Deep Learning"
    AI_CLUSTERS["artificial_intelligence"] = "Artificial Intelligence"
    AI_CLUSTERS["ai_covid"] = "AI applications to Covid-19"

    return CLEAN_CLUSTERS, AI_CLUSTERS


CLEAN_CLUSTERS, AI_CLUSTERS = make_clean_clusters()


def fetch_nuts_shape():
    """Fetch NUTS shapes"""

    for nuts_version in ["2010", "2013", "2016", "2021"]:
        logging.info(f"fetching NUTS {nuts_version}")
        content = requests.get(
            f"https://gisco-services.ec.europa.eu/distribution/v2/nuts/download/ref-nuts-{nuts_version}-10m.geojson.zip"
        ).content
        logging.info("Saving")
        ZipFile(BytesIO(content)).extractall(f"{NUTS_SHAPE_PATH}/{nuts_version}")


def reverse_geocode_table(
    table,
    nuts_version,
    vars_to_keep=[
        "article_source",
        "cluster",
        "artificial_intelligence",
        "deep_learning",
        "ai_covid",
    ],
):
    """Reverse geocodes a table of articles taking into account what nuts version was available when it was published"""

    # Filter the table by year
    table_in_year = table.loc[
        table["year"].isin(nuts_lookup[nuts_version])
    ].reset_index(drop=True)

    logging.info("Reading shapefile")
    nuts_geoshape = gp.read_file(
        f"{NUTS_SHAPE_PATH}/{nuts_version}/NUTS_RG_10M_{nuts_version}_4326.geojson"
    )

    table_coord = gp.GeoDataFrame(
        table_in_year,
        geometry=gp.points_from_xy(table_in_year["lng"], table_in_year["lat"]),
    )
    table_coord.crs = 4326

    logging.info("spatial join")
    table_geo = gp.sjoin(table_coord, nuts_geoshape, op="within")[
        ["article_id", "year", "NUTS_ID", "LEVL_CODE"] + vars_to_keep
    ]

    return table_geo


def make_table_aggr(table_geo, cat_variable):
    """Aggregates a geocoded article table by a categorical variable"""
    return (
        table_geo.groupby(["year", cat_variable, "NUTS_ID", "LEVL_CODE"])
        .size()
        .reset_index(drop=False)
    )


def fetch_template_schema(name="articles_base"):
    with open(
        f"{PROJECT_DIR}/outputs/data/schema/articles/{name}_schema.json", "r"
    ) as infile:
        return json.load(infile)


def get_nuts_year_spec(year):

    if year < 2013:
        return 2010
    elif year < 2016:
        return 2013
    elif year < 2021:
        return 2016
    else:
        return 2021


def fetch_countries():
    """Fetch list of countries"""
    country_yaml = yaml.safe_load(
        requests.get(
            "https://raw.githubusercontent.com/nestauk/svizzle_atlas_distro/cd24cad6af8dde3bc469ab7d4ae5f24df055e4b2/NUTS/countries_by_year.yaml"
        ).text
    )

    return set([val for el in [x for x in country_yaml.values()] for val in el])


def country_filter(table, reg="region_id"):
    """Removes any categories which are not in the country categories"""

    country_focus = fetch_countries()

    table_ = table.loc[table[reg].apply(lambda x: x[:2] in country_focus)].reset_index(
        drop=True
    )

    return table_


def get_ai_outputs():
    """Gets AI outputs. first AI papers, second DL papers, third Covid"""

    with open(f"{PROJECT_DIR}/inputs/data/ai_lookups.p", "rb") as infile:
        ai_ids = pickle.load(infile)

    return {
        "ai": ai_ids[0],
        "dl": ai_ids[1],
        "ai_covid": set(ai_ids[0]) & set(ai_ids[2]),
    }


def make_indicator(
    table,
    category,
    suffix,
    table_type,
    categories=["arxiv", "medrxiv", "biorxiv", "cord"],
):
    """Function to create article indicators.
    Args:
        table: Table combining article counts from various sources
        category: category variable
        table_type: what type of table is this
        nuts_spec: year for the nuts specification we are using
        categories: categories we use to split the table
    """

    split_tables = {}

    for cat in categories:
        t_ = table.copy()
        t_[category] = t_[category].astype(str)
        t_ = table.query(f"{category} == '{cat}'")
        t_["region_year_spec"] = t_["year"].apply(get_nuts_year_spec)
        t_["region_type"] = "NUTS"
        t_ = t_.rename(
            columns={
                0: cat + f"_{suffix}",
                "NUTS_ID": "region_id",
                "LEVL_CODE": "region_level",
            }
        )
        t_ = t_[
            [
                "year",
                "region_type",
                "region_year_spec",
                "region_id",
                "region_level",
                cat + f"_{suffix}",
            ]
        ]
        split_tables[cat] = t_

    for cat, table in split_tables.items():
        logging.info(table.tail())

        table_filtered = country_filter(table)

        table_filtered["year"] = table_filtered["year"].astype(int)

        table_filtered.to_csv(
            f"{PROJECT_DIR}/outputs/data/processed/articles/{cat}_{suffix}.csv",
            index_label=False,
            index=False,
        )

        sch = make_schema(indicator_type=table_type, category=cat, suffix=suffix)

        for field, length in zip(["title", "subtitle"], [60, 140]):
            if len(sch[field]) > length:
                print(f"{field} too long: {len(sch[field])}")

        with open(
            f"{PROJECT_DIR}/outputs/data/processed/articles/{cat}_{suffix}.json", "w"
        ) as outfile:
            json.dump(sch, outfile, indent=2)


def make_schema(indicator_type, category, suffix="count"):
    """Adds specific fields to the schema depending on the type of indicator
    we are constructing
    """
    if indicator_type == "article_sources":
        schema = fetch_template_schema()
        # schema["date"] = str(datetime.date.today())
        schema["data_date"] = "2021/07/01"
        schema["title"] = f"{category} articles (count)"
        schema[
            "subtitle"
        ] = f"Number participations in {category} articles by institutions in the location"
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {category} articles"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "clusters":
        schema = fetch_template_schema("articles_clusters_base")
        # schema["date"] = str(datetime.date.today())
        schema["data_date"] = "2021/07/01"
        schema["is_experimental"] = True
        schema["title"] = f"{CLEAN_CLUSTERS[category]} preprints (count)"
        schema[
            "subtitle"
        ] = f"Number participations in {CLEAN_CLUSTERS[category]} preprints by institutions in the location"
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {CLEAN_CLUSTERS[category]} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "ai_counts":
        schema = fetch_template_schema("articles_ai_base")
        # schema["date"] = str(datetime.date.today())
        schema["data_date"] = "2021/07/01"
        schema["is_experimental"] = True
        schema["title"] = f"{AI_CLUSTERS[category]} preprints (count)"
        schema[
            "subtitle"
        ] = f"Number participations in {AI_CLUSTERS[category]} preprints by institutions in the location"
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {AI_CLUSTERS[category]} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "ai_spec":
        schema = fetch_template_schema("articles_ai_base")
        # schema["date"] = str(datetime.date.today())
        schema["data_date"] = "2021/07/01"
        schema["is_experimental"] = True
        schema["title"] = f"{AI_CLUSTERS[category]} preprints (relative specialisation)"
        schema[
            "subtitle"
        ] = f"Relative specialisation in {AI_CLUSTERS[category]} preprints by institutions in the location"
        schema["schema"]["value"][
            "label"
        ] = f"{AI_CLUSTERS[category]} preprints (relative specialisation)"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"

    elif indicator_type == "clusters_specialisation":
        schema = fetch_template_schema("articles_clusters_specialisation_base")
        # schema["date"] = str(datetime.date.today())
        schema["data_date"] = "2021/07/01"
        schema["is_experimental"] = True
        schema[
            "title"
        ] = f"{CLEAN_CLUSTERS[category]} preprints (relative specialisation)"
        schema[
            "subtitle"
        ] = f"Relative specialisation in {CLEAN_CLUSTERS[category]} preprints by institutions in the location"
        schema["schema"]["value"][
            "label"
        ] = f"Relative specialisation in {CLEAN_CLUSTERS[category]} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"

    return schema


if __name__ == "__main__":
    if os.path.exists(NUTS_SHAPE_PATH) is False:
        fetch_nuts_shape()

    logging.info("Reading institute data")
    inst = (
        query_arxiv_institute()
        .query("is_multinational==False")
        .drop(
            axis=1, labels=["nuts_level1_code", "nuts_level2_code", "nuts_level3_code"]
        )
    )
    logging.info("Reading articles")
    arts = get_arxiv_articles()

    arts_sel = (
        arts.dropna(axis=0, subset=["month_year"])
        .assign(year=lambda df: [int(x.year) for x in df["month_year"]])
        .query("year>=2000")
        .query("year <= 2021")
        .reset_index(drop=True)
    )

    arts_lookup = arts_sel.set_index("article_id")[["article_source", "year"]].to_dict()
    # -

    ai_outputs = get_ai_outputs()

    # +
    # Label each article with its year, source and cluster
    inst["year"], inst["article_source"] = [
        inst["article_id"].map(arts_lookup[var]) for var in ["year", "article_source"]
    ]
    inst["cluster"] = inst["article_id"].map(arx_clusters)
    inst["artificial_intelligence"] = inst["article_id"].isin(ai_outputs["ai"])
    inst["deep_learning"] = inst["article_id"].isin(ai_outputs["dl"])
    inst["ai_covid"] = inst["article_id"].isin(ai_outputs["ai_covid"])

    inst = inst.dropna(axis=0, subset=["year"]).reset_index(drop=True)
    inst["year"] = inst["year"].astype(int)

    # Reverse geocode
    all_tables_geo = [
        reverse_geocode_table(inst, nuts) for nuts in ["2010", "2013", "2016", "2021"]
    ]

    # +
    logging.info("Making article - category counts")
    # Combine all tables into a single one and split by category
    all_tables_source = pd.concat(
        [make_table_aggr(t, "article_source") for t in all_tables_geo]
    ).reset_index(drop=True)

    make_indicator(all_tables_source, "article_source", "count", "article_sources")

    logging.info("Making article cluster indicators")
    all_tables_cluster = pd.concat(
        [make_table_aggr(t, "cluster") for t in all_tables_geo]
    ).reset_index(drop=True)

    make_indicator(
        all_tables_cluster, "cluster", "count", "clusters", list(CLEAN_CLUSTERS.keys())
    )

    logging.info("Making article cluster specialisation indicators")

    # Here we fill NAs with not covid because we are interested in determining
    # what areas were underspecialised in covid research across the board
    all_tables_cluster = pd.concat(
        [
            make_table_aggr(
                t.assign(cluster=lambda df: df["cluster"].fillna("not_covid")),
                "cluster",
            )
            for t in all_tables_geo
        ]
    ).reset_index(drop=True)

    all_tables_cluster_lq = (
        all_tables_cluster.groupby(["year", "LEVL_CODE"])
        .apply(
            lambda x: make_lq(
                x.pivot_table(
                    index="NUTS_ID", columns="cluster", values=0, aggfunc="sum"
                ).fillna(0)
            )
        )
        .stack()
        .loc[[2020, 2021]]
    ).reset_index(drop=False)

    all_tables_cluster = all_tables_cluster.query("cluster!='not_covid'")

    all_tables_cluster_lq[0] = all_tables_cluster_lq[0].apply(lambda x: np.round(x, 2))

    make_indicator(
        all_tables_cluster_lq,
        "cluster",
        "lq",
        "clusters_specialisation",
        list(CLEAN_CLUSTERS.keys()),
    )

    logging.info("make AI count")

    logging.info("Making article AI indicators")
    all_tables_ai = (
        pd.concat(
            [make_table_aggr(t, "artificial_intelligence") for t in all_tables_geo]
        )
        .reset_index(drop=True)
        .replace({True: "artificial_intelligence"})
    )

    make_indicator(
        table=all_tables_ai,
        category="artificial_intelligence",
        suffix="count",
        table_type="ai_counts",
        categories=["artificial_intelligence"],
    )

    # deep learning
    all_tables_dl = (
        pd.concat([make_table_aggr(t, "deep_learning") for t in all_tables_geo])
        .reset_index(drop=True)
        .replace({True: "deep_learning"})
    )

    make_indicator(
        table=all_tables_dl,
        category="deep_learning",
        suffix="count",
        table_type="ai_counts",
        categories=["deep_learning"],
    )

    # ai covid
    all_tables_covid_ai = (
        pd.concat([make_table_aggr(t, "ai_covid") for t in all_tables_geo])
        .reset_index(drop=True)
        .replace({True: "ai_covid"})
    )

    make_indicator(
        table=all_tables_covid_ai,
        category="ai_covid",
        suffix="count",
        table_type="ai_counts",
        categories=["ai_covid"],
    )
