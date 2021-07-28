# Fits a topic model to the cordis data (focusing on recent projects)

import logging

from eurito_indicators.getters.arxiv_getters import get_covid_papers
from eurito_indicators.pipeline.processing_utils import save_model
from eurito_indicators.pipeline.text_processing import (
    make_engram,
    pre_process,
    remove_extr_freq,
)
from eurito_indicators.pipeline.topic_modelling import (
    post_process_model_clusters,
    train_model,
)


if __name__ == "__main__":

    logging.info("Reading data")
    preprint_corpus = (
        get_covid_papers().query("article_source!='cord'").reset_index(drop=True)
    )

    #preprint_corpus = get_covid_papers().sample(100000).reset_index(drop=True)

    pre_print_tokenised = remove_extr_freq(
        make_engram(
            [pre_process(doc) for doc in preprint_corpus["abstract"]],
        ),
        high=0.999,
    )

    # text_pipeline(cord_corp["text"], high_freq=0.997)
    logging.info(len(pre_print_tokenised))

    logging.info("Training topic model")
    model = train_model(pre_print_tokenised, preprint_corpus["article_id"].tolist())

    topic_mix, clusters = post_process_model_clusters(
        model, top_level=0, cl_level=0, top_thres=0.8
    )

    topic_mix.index = preprint_corpus["article_id"].tolist()

    logging.info("Saving outputs")
    save_model(
        [model, topic_mix, clusters, pre_print_tokenised], "topsbm_arxiv_v2"
    )
