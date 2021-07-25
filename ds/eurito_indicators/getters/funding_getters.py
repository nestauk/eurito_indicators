import json
import logging
from datetime import datetime

import numpy as np
import pandas as pd

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.cordis_getters import (
    get_cordis_projects,
)
from eurito_indicators.pipeline.processing_utils import (
    cordis_combine_text,
    covid_getter,
)


def make_gtr_fund_lookup():

    logging.info("Reading data")
    funds = pd.read_csv(f"{PROJECT_DIR}/inputs/data/gtr_funds.csv")
    link_table = pd.read_csv(f"{PROJECT_DIR}/inputs/data/gtr_link_table.csv")

    logging.info("Making lookup")
    fund_table = link_table.loc[link_table["table_name"] == "gtr_funds"]
    fund_income = funds.loc[funds["category"] == "INCOME_ACTUAL"]

    fund_income_pid = (
        fund_table.merge(fund_income, on="id")
        .drop_duplicates("project_id")
        .set_index("project_id")[["start", "amount"]]
        .to_dict(orient="index")
    )

    logging.info("Saving lookup")
    with open(f"{PROJECT_DIR}/inputs/data/gtr_project_income.json", "w") as outfile:
        json.dump(fund_income_pid, outfile)


def get_project_fund_lookup():
    with open(f"{PROJECT_DIR}/inputs/data/gtr_project_income.json", "r") as infile:
        return json.load(infile)


def get_cordis_covid():

    projs = cordis_combine_text(
        (get_cordis_projects().dropna(axis=0, subset=["title", "objective"]))
    )

    projs["has_covid"] = [covid_getter(t) for t in projs["text"]]

    projs_sel = projs.loc[projs["has_covid"] == True].reset_index(drop=True)[
        ["project_id", "title", "objective", "start_date", "ec_max_contribution"]
    ]

    projs_sel = (
        projs_sel.rename(
            columns={"objective": "abstract", "ec_max_contribution": "cost"}
        )
        .assign(currency="EUR")
        .assign(source="ec")
    )

    return projs_sel


def get_gtr_projects():

    projs = pd.read_csv(f"{PROJECT_DIR}/inputs/data/gtr_projects_v2.csv").dropna(
        axis=0, subset=["abstractText"]
    )

    fund_lookup = get_project_fund_lookup()
    date_lookup = {k: v["start"] for k, v in fund_lookup.items()}
    income_lookup = {k: v["amount"] for k, v in fund_lookup.items()}

    projs["has_covid"] = [covid_getter(t) for t in projs["abstractText"]]

    projs_sel = (
        projs.loc[projs["has_covid"] == True]
        .reset_index(drop=True)
        .rename(
            columns={"id": "project_id", "title": "title", "abstractText": "abstract"}
        )[["project_id", "title", "abstract"]]
        .assign(currency="GBP")
        .assign(source="ukri")
    )

    projs_sel["start_date"] = projs_sel["project_id"].map(date_lookup)
    projs_sel["start_date"] = [
        datetime.strptime(x.split(" ")[0], "%Y-%m-%d")
        if pd.isnull(x) == False
        else np.nan
        for x in projs_sel["start_date"]
    ]

    projs_sel["cost"] = projs_sel["project_id"].map(income_lookup)

    return projs_sel


def get_nih_projects():

    nihp = pd.read_csv(f"{PROJECT_DIR}/inputs/data/nih_projects_v2.csv")

    abst = pd.read_csv(f"{PROJECT_DIR}/inputs/data/nih_abstracts_v3.csv")

    nihp["abstract"] = abst["application_id"].map(
        abst.set_index("application_id")["abstract_text"].to_dict()
    )

    return nihp
    nihp = nihp.dropna(axis=0, subset=["abstract", "project_title"])
    nihp["text"] = [
        title + " " + abstract
        for title, abstract in zip(nihp["project_title"], nihp["abstract"])
    ]

    nihp["has_covid"] = [covid_getter(t) for t in nihp["text"]]

    nihp_select = (
        (
            nihp.reset_index(drop=False)[
                [
                    "application_id",
                    "project_title",
                    "abstract",
                    "project_start",
                    "total_cost",
                ]
            ].rename(
                columns={
                    "application_id": "project_id",
                    "project_title": "title",
                    "project_start": "start_date",
                    "total_cost": "cost",
                }
            )
        )
        .assign(currency="USD")
        .assign(source="nih")
    )

    return nihp_select


def get_wellcome():

    url = "https://cms.wellcome.org/sites/default/files/2021-07/Wellcome%20grants%20awarded%201%20October%202005%20to%2030%20June%202021%20as%20at%2012072021.xlsx"
    wellcome = pd.read_excel(url)

    wellcome_w_text = wellcome.dropna(axis=0, subset=["Title", "Description"])

    wellcome_w_text["text"] = [
        " ".join([text, descr])
        for text, descr in zip(wellcome_w_text["Title"], wellcome_w_text["Description"])
    ]

    wellcome_w_text["has_covid"] = [covid_getter(t) for t in wellcome_w_text["text"]]

    wellcome_sel = (
        wellcome_w_text.query("has_covid==True")
        .reset_index(drop=True)[
            [
                "Internal ID",
                "Title",
                "Description",
                "Planned Dates:Start Date",
                "Amount Awarded",
                "Currency",
            ]
        ]
        .rename(
            columns={
                "Internal ID": "project_id",
                "Title": "title",
                "Description": "abstract",
                "Planned Dates:Start Date": "start_date",
                "Amount Awarded": "cost",
                "Currency": "currency",
            }
        )
        .assign(source="wellcome")
    )

    return wellcome_sel
