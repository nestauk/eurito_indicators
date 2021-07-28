import json
import logging
import os
from itertools import chain

import numpy as np

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import get_arxiv_articles
from eurito_indicators.pipeline.text_processing import make_engram, pre_process

TOK_PATH = f"{PROJECT_DIR}/inputs/data/arxiv_tokenised.json"


def arxiv_tokenise():

    if os.path.exists(TOK_PATH) is True:

        logging.info("Already tokenised data")

    else:
        logging.info("Reading data")
        arxiv_articles = get_arxiv_articles().query("article_source!='cord'")

        # Remove papers without abstracts
        arxiv_w_abst = arxiv_articles.dropna(axis=0, subset=["abstract"])

        # Shuffle articles
        arxiv_w_abst = arxiv_w_abst.sample(frac=1)

        logging.info("Cleaning and tokenising")
        arxiv_tokenised = [
            pre_process(x, count=n) for n, x in enumerate(arxiv_w_abst["abstract"])
        ]

        half_arx = int(len(arxiv_tokenised) / 2)

        logging.info("Making ngrams")
        ngrammed = []

        for mini_arx in [arxiv_tokenised[:half_arx], arxiv_tokenised[half_arx:]]:
            logging.info("Extracting ngrams")
            sample_ngram = make_engram(mini_arx, n=3)
            ngrammed.append(sample_ngram)

        all_ngrams = chain(*ngrammed)

        # Turn into dictionary mapping ids to token lists
        out = {i: t for i, t in zip(arxiv_w_abst["article_id"], all_ngrams)}

        logging.info("Saving")
        with open(TOK_PATH, "w") as outfile:
            json.dump(out, outfile)


if __name__ == "__main__":
    arxiv_tokenise()
