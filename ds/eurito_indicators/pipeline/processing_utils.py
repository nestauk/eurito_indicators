# Utilities to process and clean data

import pandas as pd

from eurito_indicators import config

covid_names = config["covid_names"]

def covid_getter(text: str, covid_terms: list = covid_names) -> bool:
    """Check if a string contains a covid related term

    Args:
        text: string e.g. a project abstract
        covid_terms: covid related vocabulary

    Returns true if a covid term is in the string
    """
    return any(x in text.lower() for x in covid_terms)


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