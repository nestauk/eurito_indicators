# Get arxiv data

import logging
import os
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests

from eurito_indicators import PROJECT_DIR

GRID_PATH = f"{PROJECT_DIR}/inputs/data/grid"


def get_arxiv_articles():
    """Get arxiv - and cord - articles"""

    art = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_articles.csv",
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
        f"{PROJECT_DIR}/inputs/data/arxiv_article_institutes.csv",
        dtype={"article_id": str, "institute_id": str},
    )
    return inst


def fetch_grid():
    """Fetch the grid data"""

    if os.path.exists(GRID_PATH) is False:
        logging.info("Collecting Grid data")
        os.makedirs(GRID_PATH, exist_ok=True)
        g = requests.get("https://ndownloader.figshare.com/files/28431024")
        g_z = ZipFile(BytesIO(g.content))
        g_z.extractall(GRID_PATH)


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


if __name__ == "__main__":
    fetch_grid()
