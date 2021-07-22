# Script to collect all the daps data including arXiv and NIH

import logging
import os

from dotenv import find_dotenv, load_dotenv

from eurito_indicators import config, PROJECT_DIR
from eurito_indicators.pipeline.fetch_utils import fetch_daps_table, get_engine

DATA_PATH = f"{PROJECT_DIR}/inputs/data"
COLUMNS = config["fetch_columns"]

load_dotenv(find_dotenv())

config_path = os.getenv("MYSQL_CONFIG")

if __name__ == "__main__":

    # Connect to db
    con = get_engine(f"{config_path}")

    logging.info("Downloading data")

    # Read tables

    for t in [
        "nih_projects",
        "nih_abstracts",
        "arxiv_articles",
        "arxiv_article_institutes",
        "gtr_projects",
        "gtr_funds",
        "gtr_link_table",
        'arxiv_categories',
        'arxiv_article_categories',
        'arxiv_article_fields_of_study',
        'mag_fields_of_study'
    ]:

        if os.path.exists(f"{DATA_PATH}/{t}.csv") is False:
            logging.info(f"Donwloading table: {t}")

            if t in COLUMNS.keys():
                daps_t = fetch_daps_table(
                    t,
                    con,
                    cols=COLUMNS[t],
                    chunks=1000,
                )
            else:
                daps_t = fetch_daps_table(t, con, chunks=1000)

            daps_t.to_csv(f"{DATA_PATH}/{t}.csv", index=False)
