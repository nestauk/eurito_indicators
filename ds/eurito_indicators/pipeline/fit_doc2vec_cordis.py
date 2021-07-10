# Train a paragraaph vector model on the cordis corpus

import logging

from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from eurito_indicators.getters.cordis_getters import get_cordis_projects
from eurito_indicators.pipeline.processing_utils import (
    cordis_combine_text,
    filter_by_length,
    save_model,
)
from eurito_indicators.pipeline.text_processing import make_engram, pre_process


if __name__ == "__main__":

    logging.info("Reading and preprocessing data")
    cordis_corpus = get_cordis_projects()
    cordis_corpus_long = filter_by_length(cordis_corpus, "objective", min_length=500)

    cordis_tokenised = make_engram(
        [pre_process(doc) for doc in cordis_corpus_long["objective"]]
    )

    logging.info("Training model")
    train_corpus = [
        TaggedDocument(words=tok, tags=[str(_id)])
        for tok, _id in zip(cordis_tokenised, cordis_corpus_long["project_id"])
    ]

    model = Doc2Vec(vector_size=200, min_count=5, epochs=200)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

    save_model(model, "doc2vec_cordis")
