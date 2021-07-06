# cordis data getters

from datetime import datetime

import pandas as pd
from eurito_indicators import PROJECT_DIR


def get_cordis_projects():

    return pd.read_csv(f"{PROJECT_DIR}/inputs/data/cordis_projects.csv",
                       parse_dates=['start_date'])


def get_cordis_organisations():

    return pd.read_csv(f"{PROJECT_DIR}/inputs/data/cordis_organisations.csv")
