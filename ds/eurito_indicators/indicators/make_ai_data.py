# Create AI dataset we later use to make indicators

from itertools import chain
import logging
import pickle

import pandas as pd
import numpy as np
import tomotopy as tp
from numpy.random import choice
import yaml

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    query_arxiv_institute,
    get_ai_results,
    get_article_categories,
    get_arxiv_tokenised,
    get_arxiv_w2v,
    get_arxiv_articles,
    get_cluster_ids,
)
from eurito_indicators.indicators.make_article_indicators import (
    reverse_geocode_table,
    get_nuts_year_spec,
    make_indicator,
    country_filter,
    make_table_aggr,
)
from eurito_indicators.pipeline.processing_utils import make_bins, make_lq
from eurito_indicators.pipeline.topic_utils import make_topic_mix


def make_ai_ids():
    """Function to extract AI Ids from the categories and expanded paper
    list files
    """
    ai = get_ai_results()

    cats = get_article_categories()

    ai_cats = set(["cs.AI", "cs.NE", "stat.ML", "cs.LG"])

    ai_core_papers = set(cats.loc[cats["category_id"].isin(ai_cats)]["article_id"])

    ai_papers_expanded = set(chain(*ai[0].values()))

    all_ai_ids = ai_core_papers.union(ai_papers_expanded)

    return all_ai_ids


#if __name__ == "__main__":
logging.info("Reading data")
arts = get_arxiv_articles()
ai_ids = make_ai_ids()
tok = get_arxiv_tokenised()
arx_w2v = get_arxiv_w2v()
covid_ids = get_cluster_ids()

# Get dict with tokenised AI abstracts
ai_tok = {k: v for k, v in tok.items() if (k in ai_ids) & (len(v) > 0)}
ai_tok_text = list(ai_tok.values())

logging.info("Train and fit topic model")
v = 150
mdl = tp.LDAModel(k=v, seed=123)

for t in ai_tok_text:
    mdl.add_doc(t)

for i in range(0, 150, 10):
    mdl.train(10)
    print("Iteration: {}\tLog-likelihood: {}".format(i, mdl.ll_per_word))

for k in range(mdl.k):
    # print('Top 10 words of topic #{}'.format(k))
    print(mdl.get_topic_words(k, top_n=10))

topic_names = [[x[0] for x in mdl.get_topic_words(k, top_n=5)] for k in range(v)]

logging.info("Identify deep learning papers")
sims = (
    pd.DataFrame(
        [
            np.mean(
                arx_w2v.wv.similarity(
                    [el for el in t if el in arx_w2v.wv], "artificial_neural"
                )
            )
            for t in topic_names
        ],
        index=["_".join(t) for t in topic_names],
    )
    .reset_index(drop=False)
    .rename(columns={0: "mean_similarity"})
)

dl_topics = sims.loc[
    sims["mean_similarity"]
    > sims["mean_similarity"].mean() + 1.5 * (sims["mean_similarity"].std())
]["index"].tolist()

dl_topics.remove("network_neuron_neural_brain_learning")
logging.info(dl_topics)

topic_mix = make_topic_mix(mdl, doc_indices=ai_tok.keys(), num_topics=150)

# Identify AI papers
dl_paper = set(
    chain(
        *[
            topic_mix.loc[
                topic_mix[t] > (topic_mix[t].mean() + topic_mix[t].std() * 2)
            ].index
            for t in dl_topics
        ]
    )
)

with open(f"{PROJECT_DIR}/inputs/data/ai_lookups.p",'wb') as outfile:
    outputs = [ai_ids, dl_paper, covid_ids]
    
    pickle.dump(outputs,outfile)
