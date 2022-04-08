"""Script to create covid-related indicators from cordis"""

import json
import logging
import re

import numpy as np
import pandas as pd
import yaml
from toolz import pipe

from eurito_indicators import PROJECT_DIR
from eurito_indicators.pipeline.processing_utils import make_lq
from eurito_indicators.getters.cordis_getters import (
    get_cordis_projects,
    get_cordis_organisations,
    get_cordis_clusters,
    get_cordis_labelled,
    get_cluster_labels,
    get_closest_cluster,
)

# Global vars

# %%
CLUSTER_SHORT = {
    "Cluster 0: Diagnosis & prevention": "diagnosis",
    "Cluster 1: Public health": "public_health",
    "Cluster 2: Systems and Networks": "systems",
    "Cluster 3: Policy": "policy",
    "Cluster 4: Products and Services": "products",
    "Cluster 5: Biotechnology": "biotech",
}

CLUSTER_LONG = {v: k.split(":")[1].strip().lower() for k, v in CLUSTER_SHORT.items()}

# Functions


def get_org_nuts():
    """Gets organisation nuts at different points in time"""
    with open(f"{PROJECT_DIR}/inputs/data/cordis_nuts.json", "r") as infile:
        return pd.DataFrame(json.load(infile))


def get_nuts_spec(year):
    """Returns the right NUT spec to use in different years"""

    return (
        2021
        if year >= 2021
        else 2016
        if year >= 2016
        else 2013
        if year >= 2013
        else 2010
    )


def make_clean_table(table, cluster, suffix):
    """Make a clean indicator table including a short name and suffix
    for unit of measurement
    """

    t = (
        table.assign(region_type="NUTS")[
            ["year", "region_type", "nuts_year", "NUTS_ID", "LEVL_CODE", "value"]
        ]
        .query("value>0")
        .assign(value=lambda df: df["value"].apply(lambda x: np.round(x, 2)))
        .assign(year=lambda df: df["year"].astype(int))
        .rename(
            columns={
                "value": CLUSTER_SHORT[cluster] + f"_{suffix}",
                "nuts_year": "region_year_spec",
                "NUTS_ID": "region_id",
                "LEVL_CODE": "region_level",
            }
        )
        .reset_index(drop=True)
    )

    logging.info(t.head())
    return t


def make_spec(table):
    """Calculates relative specialisation index for
    a location in a year and NUTS level
    """

    spec_index_vars = ["year", "LEVL_CODE", "nuts_year"]

    return table.groupby(spec_index_vars).apply(
        lambda df: pipe(
            df.pivot_table(
                index="NUTS_ID", columns="cluster_label", values="value"
            ).fillna(0),
            make_lq,
            lambda df: df.stack(),
        )
    )


def make_cordis_indicators(proj_labs):
    """Creates the cordis indicators we are interested in e.g.
    number of projects and level of funding
    """

    index_vars = ["cluster_label", "year", "nuts_year", "NUTS_ID", "LEVL_CODE"]

    # Number of projects
    project_n = proj_labs.groupby(index_vars).size().reset_index(name="value")

    # Level of funding
    funding_sum = (
        proj_labs.groupby(index_vars)["ec_contribution"].sum().reset_index(name="value")
    )

    # Specialisation (count)

    spec_index_vars = ["year", "LEVL_CODE"]

    project_spec = make_spec(project_n).reset_index(name="value")

    funding_spec = make_spec(funding_sum).reset_index(name="value")

    # Create indicators for each cluster

    for cluster in project_n["cluster_label"].unique():

        clean_proj_count = save_table(
            make_clean_table(
                project_n.query(f"cluster_label=='{cluster}'"), cluster, "proj_count"
            )
        )
        pipe(clean_proj_count, make_schema, save_schema)

        clean_fund = save_table(
            make_clean_table(
                funding_sum.query(f"cluster_label=='{cluster}'"), cluster, "fund_amount"
            )
        )
        pipe(clean_fund, make_schema, save_schema)

        clean_proj_spec = save_table(
            make_clean_table(
                project_spec.query(f"cluster_label=='{cluster}'"), cluster, "proj_spec"
            )
        )
        pipe(clean_proj_spec, make_schema, save_schema)

        clean_funding_spec = save_table(
            make_clean_table(
                funding_spec.query(f"cluster_label=='{cluster}'"), cluster, "fund_spec"
            )
        )
        pipe(clean_proj_spec, make_schema, save_schema)


def save_table(table):
    """Saves a table"""
    table.to_csv(
        f"{PROJECT_DIR}/outputs/data/processed/cordis_covid/{table.columns[-1]}.csv",
        index=False
    )

    return table


def get_cordis_schema():
    """Gets the cordis template"""
    with open(
        f"{PROJECT_DIR}/outputs/data/schema/cordis/cordis_schema_template.yaml", "r"
    ) as infile:
        return yaml.safe_load(infile)


def make_schema(table):
    """Automates the creation of the schema based on the variable type"""

    sch = get_cordis_schema()

    var_name = table.columns[-1]
    cluster_name = "_".join(var_name.split("_")[:-2])
    sch["schema"]["value"]["id"] = var_name

    if "proj_count" in var_name:

        sch["schema"]["value"]["label"] = f"Number of projects in {CLUSTER_LONG[cluster_name]}"

        sch["schema"]["value"]["data_type"] = "int"
        sch["schema"]["value"]["format"] = ".1f"

        sch["subtitle"] = f"Number of projects in {CLUSTER_LONG[cluster_name]}"
        sch[
            "title"
        ] = f"Number of EC projects about {CLUSTER_LONG[cluster_name]} involving organisations in the area"

    if "proj_spec" in var_name:

        sch["schema"]["value"]["label"] = f"Relative project specialisation in {CLUSTER_LONG[cluster_name]} research area"

        sch[
            "subtitle"
        ] = f"Relative project specialisation in {CLUSTER_LONG[cluster_name]} research area"
        sch[
            "title"
        ] = f"Relative specialisation in projects about {CLUSTER_LONG[cluster_name]} based on participation from organisation in the area."

    if "fund_amount" in var_name:

        sch["schema"]["value"]["label"] = f"EC contribution to research in {CLUSTER_LONG[cluster_name]}"

        sch["subtitle"] = f"EC contribution to research in {CLUSTER_LONG[cluster_name]}"
        sch[
            "title"
        ] = f"EC contribution to organisations in the area participating in research about {CLUSTER_LONG[cluster_name]}"

    if "fund_spec" in var_name:

        sch["schema"]["value"]["label"] = f"Relative funding specialisation in {CLUSTER_LONG[cluster_name]} research area"

        sch[
            "subtitle"
        ] = f"Relative funding specialisation in {CLUSTER_LONG[cluster_name]} research area"
        sch[
            "title"
        ] = f"Relative specialisation in projects about {CLUSTER_LONG[cluster_name]} based on funding received by projects involving organisation in the area"

    return sch


def save_schema(schema):
    """Saves a schema"""
    with open(
        f"{PROJECT_DIR}/outputs/data/processed/cordis_covid/{schema['schema']['value']['id']}.json",
        "w",
    ) as outfile:
        json.dump(schema, outfile, indent=2)


if __name__ == "__main__":

    logging.info("Preparing data")
    # Read and process projects
    projs = (
        get_cordis_projects()
        .dropna(axis=0, subset=["start_date"])
        .assign(year=lambda df: [int(x.year) for x in df["start_date"]])
        .query("year>=2010")
        .reset_index(drop=True)
    )

    proj_year_lookup = projs.set_index("project_id")["year"].to_dict()

    # Read and process orgs e.g. parse ec contribution
    orgs = get_cordis_organisations().assign(
        ec_contribution=lambda df: [
            float(re.sub(",", ".", x)) if pd.isnull(x) is False else np.nan
            for x in df["ec_contribution"]
        ]
    )

    # This is the closest covid research cluster to a project abstract
    closest = get_closest_cluster()

    # cluster labels
    labs = get_cluster_labels()

    # Organisation nuts
    org_nuts = get_org_nuts()

    # %%
    # Create labelled table
    projs_lab = (
        orgs.assign(cluster_code=lambda df: df["project_id"].astype(str).map(closest))
        .assign(cluster_label=lambda df: df["cluster_code"].map(labs))
        .assign(year=lambda df: df["project_id"].map(proj_year_lookup))
        .dropna(axis=0, subset=["year"])
        .assign(nuts_year=lambda df: df["year"].apply(get_nuts_spec))
        .merge(
            org_nuts, left_on=["id", "nuts_year"], right_on=["cordis_id", "nuts_year"]
        )[
            [
                "project_id",
                "project_acronym",
                "short_name",
                "ec_contribution",
                "cluster_label",
                "year",
                "nuts_year",
                "NUTS_ID",
                "LEVL_CODE",
            ]
        ]
    )

    logging.info("Making and saving indicators")
    make_cordis_indicators(projs_lab)
