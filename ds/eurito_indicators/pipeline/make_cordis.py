# Collect and process cordis data

import logging
import os
import re
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests

from eurito_indicators import config, PROJECT_DIR
from eurito_indicators.pipeline.processing_utils import covid_getter

LEVEL_LOOKUP = config["covid_level_names"]
POST_PATH = f"{PROJECT_DIR}/inputs/data/postcode_nuts_lookup"


def camel_to_snake(text):
    """Converts camel case to snake case"""

    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def clean_cordis_projects(cordis_projects: pd.DataFrame) -> pd.DataFrame:
    """Clean and process cordis variable names

    Args:
        cordis_projects: cordis_project table
    """

    cordis_projects.columns = [camel_to_snake(c) for c in cordis_projects.columns]
    cordis_projects = cordis_projects.rename(columns={"id": "project_id"})

    cordis_projects["start_date"] = [
        datetime.strptime(d, "%d/%m/%Y") if type(d) == str else np.nan
        for d in cordis_projects["start_date"]
    ]
    cordis_projects["cost_num"] = [
        int(x.split(",")[0]) if type(x) == str else np.nan
        for x in cordis_projects["total_cost"]
    ]
    cordis_projects["eu_contr"] = [
        int(x.split(",")[0]) if type(x) == str else np.nan
        for x in cordis_projects["ec_max_contribution"]
    ]

    return cordis_projects


# Projects
def fetch_cordis_projects() -> pd.DataFrame:
    """Fetch cordis projects table"""
    logging.info("fetching cordis_projects")

    cordis_projects = pd.read_csv(
        "https://cordis.europa.eu/data/cordis-h2020projects.csv",
        delimiter=";",
        skiprows=0,
    ).dropna(axis=0, subset=["objective"])

    cordis_projects_clean = clean_cordis_projects(cordis_projects)

    return cordis_projects_clean

def read_cordis_labelled() -> pd.DataFrame:
    """Fetch cordis labelled dataset"""

    covid_port = pd.read_excel(
        f"{PROJECT_DIR}/inputs/data/covid_19_portfolio.xlsx",
        sheet_name="Projects",
        skiprows=1,
    )
    covid_port.columns = [re.sub(" ", "_", col.lower()) for col in covid_port.columns]

    # Rename levels

    covid_port["level_relabelled"] = covid_port["portfolio_level"].map(LEVEL_LOOKUP)

    covid_level_lookup = covid_port.set_index("project_number")[
        "level_relabelled"
    ].to_dict()

    return covid_level_lookup


def make_cordis_projects() -> pd.DataFrame:
    """Read the cordis data and enrich with Covid-related information"""

    cordis_projects = fetch_cordis_projects()

    cordis_level_lookup = read_cordis_labelled()

    cordis_projects["covid_level"] = cordis_projects["project_id"].map(
        cordis_level_lookup
    )
    cordis_projects["covid_level"] = cordis_projects["covid_level"].fillna("non_covid")
    cordis_projects["has_covid_term"] = (
        cordis_projects["objective"].apply(covid_getter)
    ) | (cordis_projects["title"].apply(covid_getter))

    return cordis_projects


def save_cordis_projects(cordis_projects):
    """Save cordis projects"""
    logging.info("Saving cordis projects")

    cordis_projects.to_csv(
        f"{PROJECT_DIR}/inputs/data/cordis_projects.csv", index=False
    )


def fetch_postcode_nuts_lookup():
    """Fetch EU postcode - nuts lookup"""
    logging.info("Fetching postcode - nuts lookup")

    post_url = (
        "https://gisco-services.ec.europa.eu/tercet/NUTS-2021/pc2020_NUTS-2021_v4.0.zip"
    )

    post_req = requests.get(post_url)

    post_zip = ZipFile(BytesIO(post_req.content))
    post_zip.extractall(POST_PATH)


def make_postcode_nuts_lookup() -> pd.DataFrame:
    """Combines national postcode lookups into a EU wide one"""

    country_lookups = os.listdir(POST_PATH)
    postcode_nuts_lookup = pd.concat(
        [read_clean_postcode_lookup(c) for c in country_lookups]
    )

    return postcode_nuts_lookup


def read_clean_postcode_lookup(table_path: str) -> pd.DataFrame:
    """Reads and processes a national postcode - nuts table lookup

    Args:
        table_path: path to the national table

    Returns
        A cleaned table
    """

    country_table = pd.read_csv(f"{POST_PATH}/{table_path}", delimiter=";")

    for c in country_table.columns:
        country_table[c] = [re.sub("'", "", x) for x in country_table[c]]

    country_table.columns = [c.lower() for c in country_table.columns]
    country_table["country"] = table_path.split("_")[1]
    country_table = country_table.rename(columns={"code": "postcode"})
    country_table["nuts3"] = [
        n if len(n) > 0 else np.nan for n in country_table["nuts3"]
    ]

    return country_table


def fetch_cordis_organisations():
    """Fetch cordis organisations"""
    logging.info("Fetching cordis organisations")

    orgs = pd.read_csv(
        "https://cordis.europa.eu/data/cordis-h2020organizations.csv", delimiter=";"
    )
    orgs.columns = [camel_to_snake(c) for c in orgs.columns]
    orgs = orgs.rename(columns={"project_i_d": "project_id"})

    return orgs


def make_cordis_organisations():
    """Fetch cordis organisations and postcode lookuo"""

    cordis_orgs = fetch_cordis_organisations()
    fetch_postcode_nuts_lookup()

    logging.info("making postcode-nuts lookup")
    postcode_nuts_lookup = make_postcode_nuts_lookup()

    orgs_geo = cordis_orgs.merge(
        postcode_nuts_lookup,
        left_on=["country", "post_code"],
        right_on=["country", "postcode"],
        how="left",
    )
    return orgs_geo


def save_cordis_organisations(cordis_orgs):
    """Save the cordis orgs after processing"""

    cordis_orgs.to_csv(
        f"{PROJECT_DIR}/inputs/data/cordis_organisations.csv", index=False
    )


if __name__ == "__main__":

    # cordis_projects = make_cordis_projects()
    # save_cordis_projects(cordis_projects)

    cordis_orgs = make_cordis_organisations()
    save_cordis_organisations(cordis_orgs)


# Organisations

## Fetch data

## Find Covid-19

## Geocode to various geographies9
