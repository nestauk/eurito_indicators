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
