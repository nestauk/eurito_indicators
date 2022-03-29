# from json import encoder
import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline


SDGS = list(range(1, 3))
ENCODER = "distilbert-base-cased"
MODEL_PATH = f'{PROJECT_DIR}/outputs/models/sdg_classifier.pkl'

def train_model():
    models = {}
    for sdg in SDGS:
        annotated = data = load_annotated(sdg)

        st = SentenceTransformer(ENCODER)
        encodings = st.encode(list(annotated['abstract']))

        pipe = make_sdg_pipeline(sdg)
        pipe.fit(encodings, data['label'])
        models[sdg] = pipe

    with open(MODEL_PATH, 'wb') as fout:
            joblib.dump(models, fout)

if __name__ == "__main__":
    train_model()
