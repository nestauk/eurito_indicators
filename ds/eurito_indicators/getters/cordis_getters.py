# cordis data getters

import pickle
import re

import pandas as pd

from eurito_indicators import config, PROJECT_DIR

LEVEL_LOOKUP = config["covid_level_names"]


def get_cordis_projects():

    return pd.read_csv(
        f"{PROJECT_DIR}/inputs/data/cordis_projects.csv", parse_dates=["start_date"]
    )


def get_cordis_organisations():

    return pd.read_csv(f"{PROJECT_DIR}/inputs/data/cordis_organisations.csv")


def get_cordis_labelled() -> pd.DataFrame:
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


def get_doc2vec():
    with open(f"{PROJECT_DIR}/outputs/models/doc2vec_cordis.p", "rb") as infile:
        return pickle.load(infile)
