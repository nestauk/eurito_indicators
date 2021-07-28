# Text processing functions

import logging
import re
import string
from itertools import chain

import pandas as pd
from gensim.models import Phrases
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stem = WordNetLemmatizer()
STOP = set(stopwords.words("english"))
BAD = set([x for x in string.punctuation + string.digits if x != "-"])


def pre_process(text, count=None, decs=1e4):
    """Removes stopwords and symbols and lemmatises"""

    if count is not None:
        if count % decs == 0:
            logging.info(count)

    lowercase = re.sub("\n", " ", text.lower())
    no_numbers_symbols = "".join([x for x in lowercase if x not in BAD])
    tokenised = [x for x in no_numbers_symbols.split(" ") if x not in STOP]
    lemmatised = [stem.lemmatize(x) for x in tokenised if len(x) > 2]
    return lemmatised


def make_engram(corpus, n=3):
    """Makes engrams up to a desired level"""
    c = 2
    while c <= n:
        ngrammed = Phrases(corpus, min_count=3, threshold=100)
        corpus = ngrammed[corpus]
        c += 1
    return list(corpus)


def remove_extr_freq(corpus, high=0.999, low=5):
    """Removes words with very high and very low frequency
    Args:
        corpus: tokenised documents
        high: high-cile in the token frequency distribution
        low: minimum number of occurrences in the corpus
    Returns:
        A filtered corpus
    """

    freqs = pd.Series(chain(*corpus)).value_counts()
    very_high = freqs.quantile(high)
    drop_high = freqs[freqs > very_high].index.tolist()
    drop_low = freqs[freqs < low].index.tolist()

    todrop = set(drop_high + drop_low)

    corpus_filt = [[x for x in doc if x not in todrop] for doc in corpus]

    logging.info(drop_high)

    return corpus_filt


def text_pipeline(corpus, engram_max=3, high_freq=0.999):
    """Preprocesses, engrams and filters corpus"""

    logging.info("preprocessing text")
    pre_processed = [pre_process(x) for x in corpus]

    logging.info("Extracting engram")
    engrammed = make_engram(pre_processed, n=engram_max)

    logging.info("Filtering terms")
    tokenised = remove_extr_freq(engrammed, high=high_freq)

    return tokenised
