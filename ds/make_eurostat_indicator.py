# Create a couple of eurostat indicators

import logging
import os
import pandas as pd

CWD = os.getcwd()

DATA_DIR = f"{CWD}/outputs/data/processed/eurostat"
os.makedirs(DATA_DIR, exist_ok=True)

GEO_LENGTHS = {"nuts0": 2, "nuts1": 3, "nuts2": 4}


def filter_by_geo(table, geo):
    """Filters a table depending on the geographical level we focus on"""
    filt = table.loc[[len(x) == GEO_LENGTHS[geo] for x in table["geo"]]]
    return filt


def filter_eu_table(table, var_name, geography, filters, nuts_spec):
    """Takes the raw eurostat output and filters it to focus on particular units / sectors"""

    table_filt = table.copy()

    for k, v in filters.items():

        table_filt = table_filt.loc[table_filt[k] == v]

    table_filt_geo = filter_by_geo(table_filt, geography)

    table_clean = (
        table_filt_geo[["geo", "TIME_PERIOD", "OBS_VALUE"]]
        .rename(
            columns={"geo": "nuts_id", "TIME_PERIOD": "year", "OBS_VALUE": var_name}
        )
        .assign(nuts_year_spec=nuts_spec)
    )

    return table_clean[["year", "nuts_id", "nuts_year_spec", var_name]]


def save_eurostat_indicator(table, name, geo):
    """Saves a eurostat indicator table"""
    table.to_csv(f"{DATA_DIR}/{var_name}.{geo}.csv", index=False)


if __name__ == "__main__":

    # This table contains R&D spend indicators at various geographical levels (nuts0, nuts1, nuts2)
    rd_e = pd.read_csv(
        "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/RD_E_GERDREG$DEFAULTVIEW/?format=SDMX-CSV&compressed=true",
        compression="gzip",
    )

    logging.info("Example indicators")
    for sector, name in zip(["BES", "GOV"], ["private", "government"]):
        for geo in ["nuts0", "nuts1", "nuts2"]:
            var_name = f"rd_{name}_eur_hab"
            table = filter_eu_table(
                rd_e, var_name, geo, {"sectperf": sector, "unit": "EUR_HAB"}, 2016
            )
            save_eurostat_indicator(table, var_name, geo)
