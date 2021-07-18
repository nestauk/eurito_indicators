# Get arxiv data

import json
import logging
import os
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

from eurito_indicators import PROJECT_DIR
from eurito_indicators.pipeline.processing_utils import covid_getter

GRID_PATH = f"{PROJECT_DIR}/inputs/data/grid"
CORD_META_PATH = f"{PROJECT_DIR}/inputs/data/metadata.csv.zip"


def get_arxiv_articles():
    """Get arxiv - and cord - articles"""

    art = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_articles_v2.csv",
        dtype={"id": str},
        parse_dates=["created"],
    )
    art = art.rename(columns={"id": "article_id"})

    selected_columns = [
        "article_id",
        "created",
        "title",
        "journal_ref",
        "doi",
        "authors",
        "abstract",
        "mag_id",
        "citation_count",
        "article_source",
    ]
    return art[selected_columns]


def get_arxiv_institutes():
    """Lookup between paper ids and org id"""

    inst = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_article_institutes_v2.csv",
        dtype={"article_id": str, "institute_id": str},
    )
    return inst

def get_arxiv_article_categories():
    """Article categories"""

    inst = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_article_categories.csv",
        dtype={"article_id": str},
    )
    return inst

def get_arxiv_w2v():
    with open(f"{PROJECT_DIR}/outputs/models/arxiv_w2v.p", 'rb') as infile:
        return pickle.load(infile)




def fetch_grid():
    """Fetch the grid data"""

    if os.path.exists(GRID_PATH) is False:
        logging.info("Collecting Grid data")
        os.makedirs(GRID_PATH, exist_ok=True)
        g = requests.get("https://ndownloader.figshare.com/files/28431024")
        g_z = ZipFile(BytesIO(g.content))
        g_z.extractall(GRID_PATH)


def fetch_cord_meta():
    """Fetch the cord metadata"""
    if os.path.exists(CORD_META_PATH) is False:
        logging.info("Fetching cord data")
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_file(
            "allen-institute-for-ai/CORD-19-research-challenge",
            "metadata.csv",
            path=f"{PROJECT_DIR}/inputs/data",
        )


def get_cord_metadata():
    """Gets the cord metadata"""

    meta = pd.read_csv(f"{PROJECT_DIR}/inputs/data/metadata.csv.zip", compression="zip")
    meta_has_date = meta.dropna(axis=0, subset=["publish_time"])
    meta_bad_date = set(
        [
            f"cord-{_id}"
            for _id, date in zip(
                meta_has_date["cord_uid"], meta_has_date["publish_time"]
            )
            if "-" not in date
        ]
    )
    meta_year = {
        f"cord-{_id}": int(date.split("-")[0]) if "-" in date else int(date)
        for _id, date in zip(meta_has_date["cord_uid"], meta_has_date["publish_time"])
    }
    return meta_bad_date, meta_year


def make_papers():
    """Make the papers table
    Includes:
        Removing duplicated papers in cord
        Creating month year variable missing for cord papers without detailed
            publication date
    """

    arts = get_arxiv_articles()

    logging.info("processing arxiv papers")
    arxiv_covid = (
        arts.query("article_source!='cord'")
        .dropna(axis=0, subset=["abstract"])
        .assign(has_cov=lambda df: [covid_getter(text) for text in df["abstract"]])
        .query("has_cov == True")
    )
    arxiv_covid["month_year"] = [
        datetime(x.year, x.month, 1) for x in arxiv_covid["created"]
    ]
    arxiv_covid["year"] = [x.year for x in arxiv_covid["month_year"]]


    logging.info("processing cord papers")
    cord = (arts.query("article_source=='cord'")
            .dropna(axis=0, subset=['abstract'])
            .assign(has_cov=lambda df: [covid_getter(text) for text in df["abstract"]])
            .query("has_cov == True")
            .assign(
        journal_ref=lambda df: [
            x.lower() if type(x) == str else np.nan for x in df["journal_ref"]
        ]))

    cord = cord.loc[~cord["journal_ref"].isin(["biorxiv", "medrxiv"])]
    cord = cord.drop_duplicates("title")

    meta_bad_date, meta_year = get_cord_metadata()
    cord["year"] = cord["article_id"].map(meta_year)

    cord["month_year"] = [
        datetime(d.year, d.month, 1)
        if (_id not in meta_bad_date) & (not pd.isnull(d))
        else np.nan
        for _id, d in zip(cord["article_id"], cord["created"])
    ]

    papers = pd.concat(
        [arxiv_covid, cord], axis=0
    ).reset_index(drop=True).drop(axis=1, labels=["has_cov"])
    return papers


def get_grid_meta():
    """Get relevant grid metadata"""

    name, address, org_type, geo = [
        pd.read_csv(f"{GRID_PATH}/full_tables/{n}.csv")
        for n in ["institutes", "addresses", "types", "geonames"]
    ]

    merged = (
        name.merge(address, on="grid_id")
        .merge(org_type, on="grid_id")
        .merge(geo, on=["geonames_city_id", "city"], how="left")
    )

    grid_meta = merged[
        [
            "grid_id",
            "name",
            "lat",
            "lng",
            "city",
            "country",
            "country_code",
            "type",
            "nuts_level1_code",
            "nuts_level2_code",
            "nuts_level3_code",
        ]
    ]

    return grid_meta


def query_arxiv_institute():
    """Combine arXiv institute lookup with grid metadata"""

    inst = get_arxiv_institutes()

    grid_meta = get_grid_meta()

    inst_meta = inst.merge(grid_meta, left_on="institute_id", right_on="grid_id")
    return inst_meta

def get_arxiv_tokenised():
    with open(f"{PROJECT_DIR}/inputs/data/arxiv_tokenised.json", 'r') as infile:
        return json.load(infile)


if __name__ == "__main__":
    fetch_grid()
