# Get arxiv data

import json
import logging
import os
import pickle
from collections import Counter
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

from eurito_indicators import PROJECT_DIR
from eurito_indicators.pipeline.clustering_naming import make_doc_comm_lookup
from eurito_indicators.pipeline.processing_utils import covid_getter

GRID_PATH = f"{PROJECT_DIR}/inputs/data/grid"
CORD_META_PATH = f"{PROJECT_DIR}/inputs/data/metadata.csv.zip"
DISC_QUERY = f"{PROJECT_DIR}/inputs/data/arxiv_discipline.csv"
COV_PAPERS_PATH = f"{PROJECT_DIR}/inputs/data/arxiv_papers_covid.csv"


def get_arxiv_articles():
    """Get arxiv - and cord - articles"""

    art = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_articles_v2.csv",
        dtype={"id": str},
        parse_dates=["created"],
    )
    art = art.rename(columns={"id": "article_id"})
    art["month_year"] = [
        datetime(x.year, x.month, 1) if pd.isnull(x) == False else np.nan
        for x in art["created"]
    ]

    selected_columns = [
        "article_id",
        "created",
        "month_year",
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


def get_article_categories():
    """Article categories"""

    inst = pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_article_categories.csv",
        dtype={"article_id": str},
    )
    return inst


def get_arxiv_w2v():
    with open(f"{PROJECT_DIR}/outputs/models/arxiv_w2v.p", "rb") as infile:
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


def get_covid_papers():
    """Make the papers table
    Includes:
        Removing duplicated papers in cord
        Creating month year variable missing for cord papers without detailed
            publication date
    """

    if os.path.exists(COV_PAPERS_PATH) is False:
        logging.info("Making covid papers")

        arts = get_arxiv_articles()

        logging.info("processing arxiv papers")
        arxiv_covid = (
            arts.query("article_source!='cord'")
            .dropna(axis=0, subset=["abstract"])
            .assign(text = lambda df: [" ".join(x,y) for x,y in zip(df['title'],df['abstract'])])
            .assign(has_cov=lambda df: [covid_getter(text) for text in df["text"]])
            .query("has_cov == True")
        )
        arxiv_covid["month_year"] = [
            datetime(x.year, x.month, 1) for x in arxiv_covid["created"]
        ]
        arxiv_covid["year"] = [x.year for x in arxiv_covid["month_year"]]

        logging.info("processing cord papers")
        cord = (
            arts.query("article_source=='cord'")
            .dropna(axis=0, subset=["abstract"])
            .assign(has_cov=lambda df: [covid_getter(text) for text in df["abstract"]])
            .query("has_cov == True")
            .assign(
                journal_ref=lambda df: [
                    x.lower() if type(x) == str else np.nan for x in df["journal_ref"]
                ]
            )
        )

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

        papers = (
            pd.concat([arxiv_covid, cord], axis=0)
            .reset_index(drop=True)
            .drop(axis=1, labels=["has_cov"])
        )
        papers.to_csv(COV_PAPERS_PATH, index=False)
        return papers
    else:
        return pd.read_csv(
            COV_PAPERS_PATH,
            dtype={"article_id": str},
            parse_dates=["created", "month_year"],
        )


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
    with open(f"{PROJECT_DIR}/inputs/data/arxiv_tokenised.json", "r") as infile:
        return json.load(infile)


def get_arxiv_fos():
    return pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/arxiv_article_fields_of_study.csv",
        dtype={"article_id": str, "fos_id": int},
    )


def get_children(values):

    if type(values) is str:
        return [int(x) for x in values.split(",")]
    else:
        return np.nan


def make_fos_l0_lookup():
    """Creates a lookup between all MAG fos levels and the top level of the taxonomy"""
    logging.info("Reading data")

    fos_taxon = pd.read_csv(f"{PROJECT_DIR}/inputs/data/mag_fields_of_study.csv")
    id_name_lookup = fos_taxon.set_index("id")["name"].to_dict()

    all_children = {
        _id: get_children(values)
        for _id, values in zip(fos_taxon["id"], fos_taxon["child_ids"])
    }

    fos_0 = fos_taxon.loc[fos_taxon["level"] == 0]["id"].tolist()

    fos_lu = {}

    logging.info("Finding children categories")

    # We recursively look for the children of level 0s at different levels of the taxonomy
    for f in fos_0:

        children = all_children[f].copy()

        for level in range(1, 5):
            table = fos_taxon.loc[fos_taxon["id"].isin(children)].query(
                f"level=={level}"
            )

            for _id in table["id"]:
                try:
                    for ch in all_children[_id]:
                        children.append(ch)
                except BaseException:
                    pass
        for c in children:
            if c not in fos_lu.keys():
                fos_lu[c] = [f]
            else:
                fos_lu[c].append(f)

    logging.info("Creating dataframe")

    fos_lu_df = pd.DataFrame(
        {"fos_id": fos_lu.keys(), "fos_l0": fos_lu.values()}
    ).explode("fos_l0")

    fos_lu_df["fos_id_name"], fos_lu_df["fos_l0_name"] = [
        fos_lu_df[var].map(id_name_lookup) for var in ["fos_id", "fos_l0"]
    ]

    return fos_lu_df


def query_article_discipline():
    """Returns a lookup between articles and high level disciplines"""

    if os.path.exists(DISC_QUERY) is False:

        arxiv_fos = get_arxiv_fos()

        fos_lu_df = make_fos_l0_lookup()

        arxiv_f0 = arxiv_fos.merge(fos_lu_df, on="fos_id")
        logging.info("Finding top discipline")
        arxiv_discipline = (
            arxiv_f0.groupby("article_id")["fos_l0_name"]
            .apply(lambda x: Counter(x).most_common(1)[0][0])
            .reset_index(drop=False)
        )

        arxiv_discipline.to_csv(DISC_QUERY, index=False)
        return arxiv_discipline

    else:
        return pd.read_csv(DISC_QUERY, dtype={"article_id": str})


def get_arxiv_topic_model():
    with open(f"{PROJECT_DIR}/outputs/models/topsbm_arxiv_sampled.p", "rb") as infile:
        return pickle.load(infile)


def get_arxiv_tokenised():
    with open(f"{PROJECT_DIR}/inputs/data/arxiv_tokenised.json", "r") as infile:
        return json.load(infile)


def get_ai_results():
    with open(f"{PROJECT_DIR}/outputs/data/find_ai_outputs.p", "rb") as infile:
        return pickle.load(infile)

def get_cluster_names():
    with open(f"{PROJECT_DIR}/outputs/data/aux/arxiv_cluster_names.json",'r') as infile:
        return json.load(infile)

def get_cluster_ids():
    with open(f"{PROJECT_DIR}/inputs/data/arxiv_cluster_lookup.json",'r') as infile:
        paper_cluster_lookup = json.load(infile)

    
    cluster_names = get_cluster_names()
    
    paper_cluster_name = {k: cluster_names[str(v)] for k,v in paper_cluster_lookup.items()}
    return paper_cluster_name


if __name__ == "__main__":
    fetch_grid()
