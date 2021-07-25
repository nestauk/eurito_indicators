# Utilities to process and clean data

import os
import pickle

import numpy as np
import pandas as pd

from eurito_indicators import config, PROJECT_DIR

covid_names = config["covid_names"]

MOD_PATH = f"{PROJECT_DIR}/outputs/models"

if os.path.exists(MOD_PATH) is False:
    os.makedirs(MOD_PATH, exist_ok=True)


def covid_getter(text: str, covid_terms: list = covid_names) -> bool:
    """Check if a string contains a covid related term

    Args:
        text: string e.g. a project abstract
        covid_terms: covid related vocabulary

    Returns true if a covid term is in the string
    """
    return any(x in text.lower() for x in covid_terms)


def make_iso_country_lookup() -> dict:
    """Creates a country name - iso code lookup.
    Takes into account that some EU ISO country names are different from the standard.
    """

    country_names = (
        pd.read_csv(
            "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
        )
        .set_index("alpha-2")["name"]
        .to_dict()
    )

    country_names["EL"] = "Greece"
    country_names["UK"] = "United Kingdom"

    return country_names


def get_top_countries(docs, reg_var="coordinator_country", top_n=15):
    """Returns top countries in a cordis table"""
    return docs[reg_var].value_counts().index[:15].tolist()


def clean_variable_names(
    table: pd.DataFrame, variables: str, lookup: dict
) -> pd.DataFrame:
    """Clean variable names for plotting

    Args:
        table: table with variables to cleaan
        variables: list of variables to clean
        lookup: lookup between existing names and clean names

    Returns:
        table wit new, clean variable names
    """
    table_clean = table.copy()

    for v in variables:

        table_clean[v + "_clean"] = table_clean[v].map(lookup)

    return table_clean


def cordis_combine_text(cordis_corpus):
    """Combines title and objective in Cordis corpus"""

    cordis_corpus = cordis_corpus.dropna(axis=0, subset=["objective"])
    cordis_corpus["text"] = [
        r["title"] + r["objective"] for _, r in cordis_corpus.iterrows()
    ]

    return cordis_corpus


def filter_by_length(corpus, text_var, min_length=300):
    """Remove very short documents from a corpus"""

    filtered = corpus.loc[[len(doc) > min_length for doc in corpus[text_var]]]
    filtered = filtered.reset_index(drop=True)

    return filtered


def make_lq(table: pd.DataFrame) -> pd.DataFrame:
    """Calculate LQ for a category X in  population of categories Y
    Args:
        table where the rows are the categories X and columns the categories Y
    Returns:
        a table with LQs
    """
    denom = table.sum(axis=1) / table.sum().sum()
    return table.apply(lambda x: (x / x.sum()) / denom)


def save_model(model, name):
    with open(f"{MOD_PATH}/{name}.p", "wb") as outfile:
        pickle.dump(model, outfile)


def clean_table_names(
    table: pd.DataFrame, variables: list, lookup: dict
) -> pd.DataFrame:
    """Adds clean names to a table"""
    t = table.copy()

    for v in variables:
        t[v + "_clean"] = t[v].map(lookup)
    return t

def make_bins(vector:pd.Series, bins:int=30)->pd.Series:
    """Creates a binned vector
    """
    
    bins = pd.cut(vector,bins=100)
    bins_mid = pd.Series([float(x.mid) for x in bins])
    
    bins_norm = bins_mid.value_counts(normalize=True)
    return bins_norm

def remove_diagonal(table, c1, c2, value):

    for _, row in table.iterrows():
        if row[c1] == row[c2]:
            table.loc[_, value] = np.nan
    return table