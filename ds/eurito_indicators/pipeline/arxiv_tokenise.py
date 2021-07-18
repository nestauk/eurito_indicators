import json
import logging
import os

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import get_arxiv_articles
from eurito_indicators.pipeline.text_processing import make_ngram, pre_process

TOK_PATH = f"{PROJECT_DIR}/inputs/data/arxiv_tokenised.json"


def arxiv_tokenise():

    if os.path.exists(TOK_PATH) is True:

        logging.info("Already tokenised data")

    else:
        logging.info("Reading data")
        arxiv_articles = get_arxiv_articles()

        # Remove papers without abstracts
        arxiv_w_abst = arxiv_articles.dropna(axis=0, subset=["abstract"])

        logging.info("Cleaning and tokenising")
        arxiv_tokenised = [pre_process(x) for x in arxiv_w_abst["abstract"]]

        logging.info("Making ngrams")
        arxiv_ngrams = make_ngram(arxiv_tokenised, n_gram=3)

        # Turn into dictionary mapping ids to token lists
        out = {i: t for i, t in zip(arxiv_w_abst["article_id"], arxiv_ngrams)}

        logging.info("Saving")
        with open(TOK_PATH, "w") as outfile:
            json.dump(out, outfile)


if __name__ == "__main__":
    arxiv_tokenise()
