import logging
import os
import pickle
from numpy.random import choice

from gensim.models import Word2Vec

from eurito_indicators import config, PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import get_arxiv_tokenised

min_count = config["finding_ai"]["min_count"]
MOD_PATH = f"{PROJECT_DIR}/outputs/models/arxiv_w2v.p"


def train_word2vec():

    if os.path.exists(MOD_PATH) is True:
        logging.info("Already trained model")
    else:
        logging.info("loading and processing data")
        arxiv_tokenised = get_arxiv_tokenised()

        tok = list(arxiv_tokenised.values())

        logging.info("Training model")
        w2v = Word2Vec(tok, min_count=min_count)

        # Save model
        with open(MOD_PATH, "wb") as outfile:
            pickle.dump(w2v, outfile)


if __name__ == "__main__":
    train_word2vec()
