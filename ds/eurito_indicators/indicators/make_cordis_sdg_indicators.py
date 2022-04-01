import pandas as pd
import numpy as np
import joblib
import json
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime
import yaml

from eurito_indicators import PROJECT_DIR, get_yaml_config
from eurito_indicators.getters.sdg import load_annotated
from eurito_indicators.pipeline.sdg.classifier import make_sdg_pipeline
from eurito_indicators.pipeline.make_cordis import camel_to_snake
from eurito_indicators.pipeline.processing_utils import make_lq


SDGS = list(range(1, 17))
MODEL_OUT = f'{PROJECT_DIR}/outputs/models/sdg_classifier.pkl'
TRAIN = False


config = get_yaml_config(Path(f"{PROJECT_DIR}/pipeline/sdg/classifier_train.yaml"))

NUTS_YEAR_LOOKUP = {
    2010: 2010,
    2011: 2010,
    2012: 2010,
    2013: 2013,
    2014: 2013,
    2015: 2013,
    2016: 2016,
    2017: 2016,
    2018: 2016,
    2019: 2016,
    2020: 2016,
    2021: 2021,
}

def clean_cordis_projects(cordis_projects: pd.DataFrame) -> pd.DataFrame:
    """Clean and process cordis variable names

    Args:
        cordis_projects: cordis_project table
    """

    cordis_projects.columns = [camel_to_snake(c) for c in cordis_projects.columns]
    cordis_projects = cordis_projects.rename(columns={"id": "project_id"})

    cordis_projects["start_date"] = [
        datetime.strptime(d, "%Y-%m-%d") if type(d) == str else np.nan
        for d in cordis_projects["start_date"]
    ]
    cordis_projects["cost_num"] = [
        int(x.split(",")[0]) if type(x) == str else np.nan
        for x in cordis_projects["total_cost"]
    ]
    cordis_projects["eu_contr"] = [
        int(x.split(",")[0]) if type(x) == str else np.nan
        for x in cordis_projects["ec_max_contribution"]
    ]

    return cordis_projects


def generate_train_embeddings():
    encodings = {}
    for sdg in SDGS:
        annotated = load_annotated(sdg)

        st = SentenceTransformer(config["encoder"])
        encodings[sdg] = st.encode(list(annotated['abstract']))
    return encodings


def train_model(sdg_encodings):
    models = {}
    for sdg, encodings in sdg_encodings.items():

        annotated = load_annotated(sdg)

        pipe = make_sdg_pipeline(sdg)
        pipe.fit(encodings, annotated['label'])
        models[sdg] = pipe

    return models


def load_projects():
    projects = pd.read_csv(
        f"{PROJECT_DIR}/inputs/cordis/project.csv",
        delimiter=";",
        skiprows=0,
    ).dropna(axis=0, subset=["objective", "startDate"])

    projects = clean_cordis_projects(projects)

    projects["year"] = projects["start_date"].dt.year.astype(int)
    projects["nuts_year"] = projects["year"].map(NUTS_YEAR_LOOKUP)

    return projects


def create_embeddings(projects):

    st = SentenceTransformer(config["encoder"])
    encodings = st.encode(list(projects['objective']))

    return encodings


def predict_sdgs(models, projects, embeddings):

    sdg_project_predictions = {}

    for sdg, model in models.items():
        sdg_project_predictions[f"sdg_{str(sdg).zfill(2)}"] = model.predict(embeddings)

    predictions = pd.DataFrame(sdg_project_predictions)
    predictions["sdg_00"] = (predictions.sum(axis=1)< 1).astype(int)

    predictions["projectID"] = projects["project_id"]
    predictions["year"] = projects["year"]
    predictions["nuts_year"] = projects["nuts_year"]
    
    return predictions


def sdgs_by_org(sdg_predictions):
    orgs = pd.read_csv(
        f"{PROJECT_DIR}/inputs/cordis/organization.csv",
        delimiter=";",
        skiprows=0,
    )
    
    orgs = orgs[["projectID", "organisationID"]]
    org_sdgs = orgs.merge(
        sdg_predictions, 
        how="inner",
        on="projectID",
        )
    
    with open(f"{PROJECT_DIR}/inputs/cordis_nuts.json", "r") as f:
        org_nuts_lookup = pd.DataFrame(json.load(f))
    
    org_sdgs = (org_sdgs
    .merge(
        org_nuts_lookup,
        left_on=["organisationID", "nuts_year"],
        right_on=["cordis_id", "nuts_year"],
        how="inner"
    )
    .rename(columns={
        "LEVL_CODE": "region_level", 
        "NUTS_ID": "region_code", 
        "nuts_year": "nuts_year_spec"})
    )

    return org_sdgs


def sdg_cols(zero=True):

    first = 0 if zero else 1
    return[f"sdg_{str(sdg).zfill(2)}" for sdg in range(first, 17)]


def sdg_counts(org_sdgs):

    group_cols = ["region_level", "year", "nuts_year_spec", "region_code"]
    counts = (
        org_sdgs
        .groupby(group_cols)[sdg_cols()]
        .sum()
        .reset_index()
        )
    counts = counts.rename(columns={
        "region_code": "region_id",
        "nuts_year_spec": "region_year_spec"
        }
    )
    counts["year"] = counts["year"].astype(int)
    counts["region_year_spec"] = counts["region_year_spec"].astype(int)
    
    return counts


def sdg_lq(counts):
    
    groupby_cols = ["region_level", "region_year_spec", "year"]
    lqs = []
    for _, group in counts.groupby(groupby_cols):
        group = group.set_index(groupby_cols + ["region_id"])
        lq = make_lq(group[sdg_cols()])
        lq = lq.reset_index()
        lqs.append(lq)

    lq = pd.concat(lqs)

    for col in sdg_cols():
        lq[col] = lq[col].round(2)

    return lq


def fetch_template_sdg_schema(schema_type="base"):

    with open(
        f"{PROJECT_DIR}/outputs/data/schema/cordis/sdg_projects_{schema_type}_schema.json",
        "r"
    ) as infile:
        return json.load(infile)



if __name__ == "__main__":

    projects = load_projects()

    annotated_embeddings = {}
    for sdg in SDGS:
        annotated_embeddings[sdg] = np.load(
            f"{PROJECT_DIR}/inputs/sdg/annotated/sdg_{str(sdg).zfill(2)}_embeddings.npy"
        )
    if TRAIN:
        models = train_model(annotated_embeddings)
        with open(MODEL_OUT, 'wb') as fout:
                joblib.dump(models, fout)
    else:
        with open(MODEL_OUT, 'rb') as fin:
            models = joblib.load(fin)

    predict_embeddings = np.load(f"{PROJECT_DIR}/inputs/cordis/project_objective_embeddings.npy")
    predictions = predict_sdgs(models, projects, predict_embeddings)
    predictions.to_csv(f"{PROJECT_DIR}/inputs/cordis/sdg_predictions.csv", index=False)

    org_sdgs = sdgs_by_org(predictions)

    counts = sdg_counts(org_sdgs)
    lq = sdg_lq(counts)
    lq = lq[lq["year"] > 2014]


    counts["region_type"] = "NUTS"
    lq["region_type"] = "NUTS"

    with open(f"{PROJECT_DIR}/inputs/sdg/official/sdg_names.json", "r") as f:
        sdg_names = json.load(f)
        
    for sdg in SDGS:
        sdg_col = f"sdg_{str(sdg).zfill(2)}"
        sdg_name = sdg_names[str(sdg)]
        cols = ["year", "region_type", "region_year_spec", "region_id", "region_level", sdg_col]

        # Export counts
        schema = fetch_template_sdg_schema(schema_type="base")
        goal_counts = counts[cols]
        indicator_name = f"sdg_{str(sdg).zfill(2)}_project_count"
        goal_counts = goal_counts.rename(columns={sdg_col: indicator_name})
        
        goal_counts.to_csv(
            f"{PROJECT_DIR}/outputs/data/processed/cordis/{indicator_name}.csv",
            index=False
        )
        
        for field in ["description", "subtitle", "title"]:
            schema[field] = schema[field].format(sdg_name)
        
        schema["schema"]["value"]["id"] = indicator_name
        
        with open(f"{PROJECT_DIR}/outputs/data/processed/cordis/{indicator_name}.json", "w") as f:
            json.dump(schema, f, indent=2)

        # Export specialisation
        schema = fetch_template_sdg_schema(schema_type="specialisation")

        goal_lq = lq[cols]
        indicator_name = f"sdg_{str(sdg).zfill(2)}_project_specialisation"
        goal_lq = goal_lq.rename(columns={sdg_col: indicator_name})
        
        goal_lq.to_csv(
            f"{PROJECT_DIR}/outputs/data/processed/cordis/{indicator_name}.csv",
            index=False
        )
        
        for field in ["description", "subtitle", "title"]:
            schema[field] = schema[field].format(sdg_name)
        
        schema["schema"]["value"]["id"] = indicator_name
        
        with open(f"{PROJECT_DIR}/outputs/data/processed/cordis/{indicator_name}.json", "w") as f:
            json.dump(schema, f, indent=2)
