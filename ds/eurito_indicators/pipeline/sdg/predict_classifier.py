import pandas as pd

from sentence_transformers import SentenceTransformer

from eurito_indicators import PROJECT_DIR, get_yaml_config
from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline
from eurito_indicators.pipeline.make_cordis import fetch_cordis_projects

SDGS = range(1, 17)
MODEL_PATH = "f{PROJECT_DIR}/outputs/models/sdg_classifier.pkl"

config = get_yaml_config(f"{PROJECT_DIR}/pipeline/sdg/classifier_train.yaml")

def train_predict():
    st = SentenceTransformer(config["encoder"])

    sdg_models = {}

    with open(MODEL_PATH, 'rb') as fout:
        joblib.dump(sdg_models, fout)

    projects = fetch_cordis_projects()
    project_encodings = st.encode(projects["abstract"].to_list())

    sdg_project_predictions = {}

    for sdg, model in sdg_models.items():
        sdg_project_predictions[sdg] = model.predict(project_encodings)

    predictions = pd.DataFrame(sdg_project_predictions, index=projects.index)
    return predictions

if __name__ == "__main__":
    train_predict()


from sentence_transformers import SentenceTransformer

import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline

config = get_yaml_config(f"{PROJECT_DIR}/pipeline/sdg/classifier_train.yaml")

def generate_embeddings():
    st = SentenceTransformer(config["encoder"])