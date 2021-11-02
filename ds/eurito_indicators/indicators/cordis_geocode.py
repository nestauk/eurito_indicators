import logging
import pickle
from time import sleep

import geopandas as gp
import geopy
import json
import pandas as pd
import ratelim
from geopy import Nominatim

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.cordis_getters import (
    get_cordis_clusters,
    get_cordis_organisations,
)

NUTS_SHAPE_PATH = f"{PROJECT_DIR}/inputs/data/nuts"


def make_eu_countries():
    eu_countries = "Belgium (BE)  Greece  (EL)  Lithuania (LT)  Portugal  (PT) Bulgaria  (BG)  Spain (ES)  Luxembourg  (LU)  Romania (RO) Czechia (CZ)  France  (FR)  Hungary (HU)  Slovenia  (SI) Denmark (DK)  Croatia (HR)  Malta (MT)  Slovakia  (SK) Germany (DE)  Italy (IT)  Netherlands (NL)  Finland (FI) Estonia (EE)  Cyprus  (CY)  Austria (AT)  Sweden  (SE) Ireland (IE)  Latvia  (LV)  Poland  (PL)"

    eu_countries = eu_countries.split("(")
    eu_countries_iso = [x[:2] for x in eu_countries[1:]]
    eu_countries_iso.append("UK")

    return eu_countries_iso


@ratelim.patient(7.5, 10)
def get_geo_info(row):

    id_ = row["id"]

    query = {
        v: row[v]
        for v in ["country", "city", "street", "postcode"]
        if pd.isnull(row[v]) == False
    }
    try:
        location = geolocator.geocode(query)[1]
        return [id_, location]
    except:
        return [id_, None]

    def reverse_geocode_cordis(table):
        """Reverse geocodes a table of articles taking into account what nuts version was available when it was published"""

        cordis_nuts = []

        table_coord = gp.GeoDataFrame(
            table,
            geometry=gp.points_from_xy(table["lng"], table["lat"]),
        )
        table_coord.crs = 4326

        for nuts_version in [2010, 2013, 2016, 2021]:

            logging.info("Reading shapefile")
            nuts_geoshape = gp.read_file(
                f"{NUTS_SHAPE_PATH}/{nuts_version}/NUTS_RG_10M_{str(nuts_version)}_4326.geojson"
            )

            logging.info("spatial join")
            table_geo = gp.sjoin(table_coord, nuts_geoshape, op="within")[
                ["cordis_id", "NUTS_ID", "LEVL_CODE"]
            ]

            table_geo["nuts_year"] = nuts_version
            cordis_nuts.append(table_geo)

        return cordis_nuts


geolocator = Nominatim(user_agent="jmateosgarcia0@gmail.com", timeout=10)

if __name__ == "__main__":

    eu_countries_iso = make_eu_countries()

    cordis_orgs = get_cordis_organisations()
    cordis_unique = (
        cordis_orgs.loc[cordis_orgs["country"].isin(eu_countries_iso)]
        .drop_duplicates("id")[["id", "name", "country", "street", "city", "postcode"]]
        .reset_index(drop=True)
    )

    results = []

    for n, r in enumerate(cordis_unique.iterrows()):

        if n % 1000 == 0:
            logging.info("failed {}".format(sum([x[1] is None for x in results])))

            logging.info("Saving")
            with open(
                f"{PROJECT_DIR}/inputs/data/cordis_geocoded.json", "w"
            ) as outfile:
                json.dump(results, outfile)

        geoc = get_geo_info(r[1])
        results.append(geoc)

    with open(f"{PROJECT_DIR}/inputs/data/cordis_geocoded.json", "w") as outfile:
        json.dump(results, outfile)

    # Create a df with ids and coordinates
    cordis_w_coords = pd.DataFrame(
        [
            pd.Series([r[0]] + list(r[1]), index=["cordis_id", "lat", "lng"])
            for r in results
            if r[1] is not None
        ]
    )

    # Reverse geocode

    cordis_rev_geocoded = reverse_geocode_cordis(cordis_w_coords)

    cordis_coord_df = pd.concat(cordis_rev_geocoded).reset_index(drop=True)
    cordis_coord_dict = cordis_coord_df.to_dict(orient="list")

    with open(f"{PROJECT_DIR}/inputs/data/cordis_nuts.json", "w") as outfile:
        json.dump(cordis_coord_dict, outfile)
