# Embed cordis abstracts using the specter language transformer

import pandas as pd
from sentence_transformers import SentenceTransformer

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.cordis_getters import get_cordis_projects
from eurito_indicators.pipeline.processing_utils import filter_by_length

if __name__ == "__main__":

    model = SentenceTransformer("allenai-specter")

    projects = get_cordis_projects()

    projects_long = filter_by_length(projects, "objective", 300)

    projects_long["text"] = [
        " ".join([row["title"], row["objective"]]).lower()
        for _, row in projects_long.iterrows()
    ]

    embedded = model.encode(list(projects_long["text"]), show_progress_bar=True)

    specter_embedding_df = pd.DataFrame(embedded, index=projects_long["project_id"])

    specter_embedding_df.to_csv(f"{PROJECT_DIR}/inputs/data/specter_embeddings.csv")
