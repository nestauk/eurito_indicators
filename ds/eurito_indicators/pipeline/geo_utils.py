# geo scripts
import json
import logging
import os
from io import BytesIO
from zipfile import ZipFile

import altair as alt
import geopandas as gp
import requests

from eurito_indicators import PROJECT_DIR


SHAPE_PATH = f"{PROJECT_DIR}/inputs/data/shapefile"


def fetch_shapefile():

    url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip"

    request = requests.get(url)

    zipf = ZipFile(BytesIO(request.content))
    zipf.extractall(SHAPE_PATH)


def read_shape():
    """Read shapefile"""

    shapef = (
        gp.read_file(
            f"{PROJECT_DIR}/inputs/data/shapefile/ne_50m_admin_0_countries.shp"
        )
        .to_crs(epsg=4326)
        .assign(id=lambda x: x.index.astype(int))
    )

    return shapef


def make_shape(table):
    """Make a shapefile combined with a table we want to maap"""
    shapef = read_shape()

    shapef.to_crs(3426)

    shape_m = shapef.merge(table, left_on="ISO_A2", right_on="country_code", how="left")

    for t in table.columns:
        shape_m[t] = shape_m[t].fillna(0)

    shapef_json = json.loads(shape_m.to_json())

    return shapef_json


def plot_choro(shapef_json, variable, name):

    base_map = (  # Base chart with outlines
        alt.Chart(alt.Data(values=shapef_json["features"]))
        .project(type="equirectangular")
        .mark_geoshape(filled=True, stroke="gray")
    )

    choropleth = (  # Filled polygons and tooltip
        base_map.transform_calculate(region="datum.properties.ADMIN")
        .mark_geoshape(filled=True, stroke="darkgrey", strokeWidth=0.2)
        .encode(
            size=f"properties.{variable}:Q",
            color=alt.Color(
                f"properties.{variable}:Q",
                title=name,
                scale=alt.Scale(scheme="oranges", type="linear"),
                sort="ascending",
            ),
            tooltip=[
                "region:N",
                alt.Tooltip(f"properties.{variable}:Q", format="1.2f"),
            ],
        )
    )

    return choropleth


if __name__ == "__main__":
    if os.path.exists(SHAPE_PATH) is False:
        os.makedirs(SHAPE_PATH, exist_ok=True)
        logging.info("Fetching shapefile")
        fetch_shapefile()
