# Make article indicators

import logging
import os
import re
from io import BytesIO
from zipfile import ZipFile

import geopandas as gp
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

# %%
NUTS_SHAPE_PATH = f"{PROJECT_DIR}/inputs/data/nuts_2016"

arx_clusters = get_cluster_ids()

CLEAN_CLUSTERS = {
    n: " ".join([x.capitalize() for x in re.sub("_", " ", n).split(" ")])
    for n in set(arx_clusters.values())
}


def fetch_nuts_shape():
    """Fetch NUTS 16 shape"""

    logging.info("fetching NUTS shape")
    content = requests.get(
        "https://gisco-services.ec.europa.eu/distribution/v2/nuts/download/ref-nuts-2016-10m.geojson.zip"
    ).content

    logging.info("Saving shapefile")
    ZipFile(BytesIO(content)).extractall(NUTS_SHAPE_PATH)


def fetch_template_schema(name="article_base"):
    with open(
        f"{PROJECT_DIR}/outputs/data/processed/_articles/{name}_schema.yaml", "r"
    ) as infile:
        return yaml.safe_load(infile)


def make_indicator(
    table, category, nuts_level, indicator_type, suffix="count", nuts_spec=2016
):
    """Takes a table with counts / LQs of article by category and splits them.
    It also produces a schema
    """

    split_tables = []
    schema_list = []

    # Filter by category and rename consistent with our schema
    for c in sorted(set(table[category])):

        t = (
            table.query(f"{category}=='{c}'")
            .reset_index(drop=True)
            .rename(
                columns={0: f"{c}_{suffix}", f"nuts_level{nuts_level}_code": "nuts_id"}
            )
            .assign(nuts_year_spec=nuts_spec)
        )[["year", "nuts_id", "nuts_year_spec", f"{c}_{suffix}"]]
        split_tables.append(t)

        if c == "cord":
            c = "cord-19"

        schema = make_schema(
            indicator_type, category=c, nuts_level=nuts_level, suffix=suffix
        )
        schema_list.append(schema)

    return split_tables, schema_list


def specialisation_indicator(inst, nuts_level, years=[2020, 2021]):
    """Calculate yearly specialisation in covid research clusters including non-covids"""

    lqs = []

    for y in years:

        inst_year = inst_geo.copy().query("article_source!='cord'")
        inst_year["article_cluster"] = inst_year["article_cluster"].fillna("not_covid")

        year_totals = (
            inst_year.query(f"year=={y}")
            .groupby([f"nuts_level{nuts_level}_code", "article_cluster"])
            .size()
            .unstack(level=1)
            .fillna(0)
        )
        year_lq = (
            make_lq(year_totals)
            .drop(axis=1, labels=["not_covid"])  # we drop the Covid category
            .stack()
            .reset_index(drop=False)
            .assign(year=y)
        )
        lqs.append(year_lq)

    return pd.concat(lqs)


def make_schema(indicator_type, category, nuts_level, suffix="count"):
    """Adds specific fields to the schema depending on the type of indicator
    we are constructing
    """
    if indicator_type == "article_sources":
        schema = fetch_template_schema()
        schema["title"] = f"Number of participations in {category} articles"
        schema[
            "subtitle"
        ] = f"Number participations in {category} articles by institutions in the location"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {category} articles"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "clusters":
        schema = fetch_template_schema("articles_clusters_base")
        schema["is_experimental"] = True
        schema[
            "title"
        ] = f"Number of participations in {CLEAN_CLUSTERS[category]} preprints"
        schema[
            "subtitle"
        ] = f"Number participations in {CLEAN_CLUSTERS[category]} preprints by institutions in the location (research clusters identified through a topic model of article abstracts)"
        schema["region"]["level"] = nuts_level
        schema["schema"]["value"][
            "label"
        ] = f"Number participations in {CLEAN_CLUSTERS[category]} preprints"
        schema["schema"]["value"]["id"] = f"{category}_{suffix}"
    elif indicator_type == "clusters_specialisation":
        schema = fetch_template_schema("articles_clusters_specialisation_base")
        schema["is_experimental"] = True
        schema[
            "title"
        ] = f"Relative specialisation in {CLEAN_CLUSTERS[category]} preprints"
        schema[
            "subtitle"
        ] = f"Relative specialisation in {CLEAN_CLUSTERS[category]} preprints by institutions in the location (research clusters identified through a topic model of article abstracts, specialisation calculated as a location quotient taking into account non-covid activity)"
        schema["region"]["level"] = nuts_level
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

    logging.info("Reverse geocoding arXiv institutes into NUTS")

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

    logging.info("Reading articles")
    arts = get_arxiv_articles()

    # %%
    arts_sel = (
        arts.dropna(axis=0, subset=["month_year"])
        .assign(year=lambda df: [int(x.year) for x in df["month_year"]])
        .query("year>=2000")
        .query("year <= 2021")
        .reset_index(drop=True)
    )

    arts_lookup = arts_sel.set_index("article_id")[["article_source", "year"]].to_dict()

    logging.info("Logging articles with clusters")
    arx_clusters = get_cluster_ids()

    clean_clusters = {
        n: " ".join([x.capitalize() for x in re.sub("_", " ", n).split(" ")])
        for n in set(arx_clusters.values())
    }

    inst_geo["article_source"], inst_geo["year"] = [
        inst_geo["article_id"].map(arts_lookup[var])
        for var in ["article_source", "year"]
    ]

    inst_geo["article_cluster"] = inst_geo["article_id"].map(arx_clusters)

    logging.info("Making article source indicators")

    nuts_counts = [
        inst_geo.groupby(["year", "article_source", f"nuts_level{n}_code"])
        .size()
        .dropna()
        .reset_index(drop=False)
        for n in [0, 1, 2, 3]
    ]

    for n, table in enumerate(nuts_counts):
        tables, schemas = make_indicator(
            table,
            indicator_type="article_sources",
            category="article_source",
            nuts_level=n,
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

    logging.info("Making article cluster indicators")

    # %%
    nuts_counts_clusters = [
        inst_geo.groupby(["year", "article_cluster", f"nuts_level{n}_code"])
        .size()
        .dropna()
        .reset_index(drop=False)
        for n in [0, 1, 2, 3]
    ]

    for n, table in enumerate(nuts_counts_clusters):
        tables, schemas = make_indicator(
            table, indicator_type="clusters", category="article_cluster", nuts_level=n
        )

        for tb, sch in zip(tables, schemas):

            table_name = sch["schema"]["value"]["id"]
            nuts_level = sch["region"]["level"]

            logging.info(tb.head())
            # logging.info("\n")
            tb.to_csv(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.csv"
            )

            with open(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.yaml",
                "w",
            ) as outfile:
                yaml.safe_dump(sch, outfile)

    logging.info("Making article specialisation indicators")

    nuts_counts_cluster_lq = [
        specialisation_indicator(inst_geo, nuts_level=n) for n in [0, 1, 2, 3]
    ]

    for n, table in enumerate(nuts_counts_cluster_lq):
        tables, schemas = make_indicator(
            table,
            indicator_type="clusters_specialisation",
            category="article_cluster",
            nuts_level=n,
            suffix="lq",
        )

        for tb, sch in zip(tables, schemas):

            table_name = sch["schema"]["value"]["id"]
            nuts_level = sch["region"]["level"]

            logging.info(tb.head())
            # logging.info("\n")
            tb.to_csv(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.csv"
            )

            with open(
                f"{PROJECT_DIR}/outputs/data/processed/_articles/{table_name}.nuts{nuts_level}.yaml",
                "w",
            ) as outfile:
                yaml.safe_dump(sch, outfile)
