import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from itertools import product

import eurostat
import pandas as pd
import ratelim
import yaml
from toolz import pipe

from eurito_indicators import PROJECT_DIR

# Declare global variables

EUROSTAT_NAME_LOOKUP = (
    eurostat.get_toc_df()
    .drop_duplicates("code")
    .query("type=='dataset'")
    .set_index("code")["title"]
)

BASIC_VARS = ["geo", "TIME_PERIOD", "OBS_VALUE"]

META_CACHE = defaultdict()

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{table}/?format=SDMX-CSV&compressed=true"

EURITO_INDICATORS = [
    ["RD_E_GERDREG", 2010],
    ["HRST_ST_RCAT", 2010],
    ["PAT_EP_RTOT", 2010],
    ["PAT_EP_RTEC", 2010],
    ["RD_E_GERDREG", 2010],
    ["RD_P_PERSREG", 2010],
]


# Functions

# Pipeline


def fetch_table(code):
    """Fetch table from Eurostat api using its code"""

    t = pd.read_csv(BASE_URL.format(table=code), compression="gzip")
    return t.drop(axis=1, labels=["DATAFLOW", "LAST UPDATE", "freq", "OBS_FLAG"])


def get_variable_combinations(table):
    """Eurostat table combine indicators with different measures and
    e.g. sectors. We want to split them into a single table for each measurement
    and area of activity. This function returns a list of dictonaries
    where the keys are variable names and the values
    are their values in the data
    """

    return pipe(
        table,
        lambda table: list(set(table.columns) - set(BASIC_VARS)),
        lambda variables: [
            product(*[table[var].unique() for var in variables]),
            variables,
        ],
        lambda combi_vars: [
            {var: value for var, value in zip(combi_vars[1], combi)}
            for combi in combi_vars[0]
        ],
    )


def clean_table(table, name, nuts_edition=2010):
    """Processes a Eurostat table to align with our schema"""

    table_clean = (
        table.copy()
        .rename(
            columns={
                "geo": "region_id",
                "TIME_PERIOD": "year",
                "OBS_VALUE": name.lower(),
            }
        )
        .assign(region_type="NUTS")
        .assign(region_year_spec=nuts_edition)
        .assign(region_level=lambda df: df["region_id"].apply(get_nuts_level))
    )

    table_clean.name = name.lower()

    return table_clean[
        [
            "year",
            "region_type",
            "region_year_spec",
            "region_id",
            "region_level",
            name.lower(),
        ]
    ]


def extract_tables(table, variable_combs):
    """Generates a table for each combination of values in a variable
    e.g "one indicator based on thousands, another on share of population"""

    tables = []

    for comb in variable_combs:
        table_filtered = table.copy()

        for variable, value in comb.items():

            table_filtered = table_filtered.loc[table[variable] == value]

        tables.append(table_filtered.reset_index(drop=True))

    return tables


def fill_schema(code, variables, table):
    """Fills the eurostat schema with various values based on the
    variable name, selection of additional indicator values etc.
    """
    euro_schema = eurostat_schema()
    var_name = make_var_name(variables, code)

    euro_schema["api_doc_url"] = BASE_URL.format(table=code)
    euro_schema["schema"]["value"]["id"] = var_name
    euro_schema["schema"]["value"]["data_type"] = clean_types(
        type(table[var_name].iloc[0])
    )

    if "unit" in variables.keys():
        euro_schema["schema"]["value"]["unit_string"] = eurostat_dict("unit")[
            variables["unit"]
        ].lower()

    euro_schema["schema"]["value"]["label"] = make_label(code, variables)
    euro_schema["title"] = make_label(code, variables)

    return euro_schema


def save_table(table):
    """Saves a table"""

    # We use the last column (indicator name) to name the table

    table.to_csv(
        f"{PROJECT_DIR}/outputs/data/processed/eurostat/{table.columns[-1]}.csv",
        index=False,
    )

    return table


def save_schema(schema):
    """Saves the json for a schema using the indicator id as name"""

    with open(
        f"{PROJECT_DIR}/outputs/data/processed/eurostat/{schema['schema']['value']['id']}.json",
        "w",
    ) as outfile:
        json.dump(schema, outfile)


def make_indicator_schema(code, nuts_version):
    """Creates and saves indicators and schemas"""

    code = code.lower()

    logging.info("Fetching table")
    raw_table = fetch_table(code)

    logging.info("Getting variable combinations")
    variable_combinations = get_variable_combinations(raw_table)

    logging.info(f"{len(variable_combinations)} sub-indicators")

    logging.info("Extracting, cleaning and saving tables")
    extracted_tables = extract_tables(raw_table, variable_combinations)

    cleaned_tables = [
        save_table(clean_table(comb, make_var_name(_vars, code)))
        for comb, _vars in zip(extracted_tables, variable_combinations)
    ]

    logging.info("Filling and saving schemas")
    filled_schemas = [
        save_schema(fill_schema(code, variables, tables))
        for variables, tables in zip(variable_combinations, cleaned_tables)
    ]


# Utilities


def get_nuts_level(nuts_id):
    """Uses the length of a nuts id string to infer its level"""

    return len(nuts_id) - 2


def clean_datetime():
    """Clean date for the schema"""
    return pipe(
        datetime.now(), str, lambda t: t.split(" ")[0], lambda t: re.sub("-", "", t)
    )


def eurostat_dict(code):
    """Fetch data dictionary from eurostat if we haven't used it before"""

    if code in META_CACHE.keys():
        return META_CACHE[code]
    else:
        META_CACHE[code] = eurostat.get_dic(code)
        return META_CACHE[code]


def eurostat_schema():
    """Read the eurostat schema"""

    with open(
        f"{PROJECT_DIR}/outputs/data/schema/eurostat/eurostat_schema_template.yaml", "r"
    ) as infile:
        sch = yaml.safe_load(infile)

    sch["data_date"] = f"DATE_{clean_datetime()}"
    return sch


def make_var_name(_vars, code):
    """Make a variaable name using its id and additional variables"""

    return "_".join([code] + [v for v in _vars.values()]).lower()


def clean_types(data_type):
    """Return a data type"""

    return "float" if "float" in str(data_type) else "int"


@ratelim.patient(10, 5)
def make_label(code, variables):
    """Creates a variable label based on its clean name and
    the clean names for its metadata eg R&D (million euros, private sector)
    """

    var_name = EUROSTAT_NAME_LOOKUP[code]

    variables = ", ".join(
        [eurostat_dict(variable)[value] for variable, value in variables.items()]
    )

    return f"{var_name} ({variables})"


if __name__ == "__main__":
    for ind in EURITO_INDICATORS:
        logging.info(ind)
        make_indicator_schema(ind[0], ind[1])
