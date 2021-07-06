# Fits a topic model to the cordis data (focusing on recent projects)

import logging

from eurito_indicators.getters.cordis_getters import get_cordis_projects
from eurito_indicators.pipeline.processing_utils import cordis_combine_text, save_model
from eurito_indicators.pipeline.text_processing import text_pipeline
from eurito_indicators.pipeline.topic_modelling import (
    post_process_model_clusters,
    train_model,
)


def make_training_set():
    """Get recent cordis projects with a new variable that combines text
    and abstract
    """

    cordis_projects = get_cordis_projects()
    cordis_text = (
        cordis_combine_text(cordis_projects)
        .query("start_date > '2019/01/01'")
        .reset_index(drop=False)
    )

    return cordis_text


if __name__ == "__main__":

    logging.info("Reading data")
    cord_corp = make_training_set()
    cord_tokenised = text_pipeline(cord_corp["text"], high_freq=0.997)

    logging.info("Training topic model")
    model = train_model(cord_tokenised, cord_corp["project_id"].tolist())

    modelling_outputs = post_process_model_clusters(
        model, top_level=0, cl_level=0, top_thres=0.9
    )

    logging.info("Saving outputs")
    save_model(modelling_outputs, "topsbm_cordis")
