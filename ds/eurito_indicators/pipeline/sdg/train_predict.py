import pandas as pd

from sentence_transformers import SentenceTransformer

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline
from eurito_indicators.pipeline.make_cordis import fetch_cordis_projects


ENCODER = "distilbert-base-cased"
SDGS = range(1, 17)
MODEL_PATH = "f{PROJECT_DIR}/outputs/models/sdg_classifier.pkl"

def train_predict():
    st = SentenceTransformer(ENCODER)

    sdg_models = {}

    for sdg in SDGS:
        abstracts_annotated = load_annotated(sdg)
        encodings = st.encode(abstracts_annotated["abstract"].to_list())
        pipeline = make_sdg_pipeline(sdg)
        pipeline.fit(encodings, abstracts_annotated["label"])
        sdg_models[sdg] = pipeline

    with open(MODEL_PATH, 'wb') as fout:
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