import logging
import os
import pickle
import json

import yaml

from gensim.models import FastText

from eurito_indicators import PROJECT_DIR, config
from eurito_indicators.getters.arxiv_getters import get_arxiv_tokenised

min_count = config['find_ai']['min_count']
MOD_PATH = f"{PROJECT_DIR}/outputs/models/arxiv_w2v.p"

def train_word2vec():

    if os.path.exists(MOD_PATH) is True:
        logging.info("Already trained model")
    else:
        logging.info("loading and processing data")
        arxiv_tokenised = get_arxiv_tokenised()

        tok = list(arxiv_tokenised.values())

        logging.info("Training model")
        ft = FastText(tok, min_count=min_count, word_ngrams=0)

        # Save model
        with open(MOD_PATH, "wb") as outfile:
            pickle.dump(ft, outfile)


if __name__ == "__main__":
    train_word2vec()
