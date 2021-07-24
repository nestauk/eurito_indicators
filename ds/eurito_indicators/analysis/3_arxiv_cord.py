# Comparison between arXiv and CORD dataset

# %%
import logging
from itertools import chain

import altair as alt
import numpy as np
import pandas as pd
import tomotopy as tp

from eurito_indicators import PROJECT_DIR
from eurito_indicators.getters.arxiv_getters import (
    get_covid_papers,
    query_article_discipline,
    query_arxiv_institute,
)
from eurito_indicators.pipeline.processing_utils import make_lq
from eurito_indicators.pipeline.text_processing import text_pipeline
from eurito_indicators.pipeline.topic_utils import make_topic_mix, topic_regression
from eurito_indicators.utils.altair_save_utils import (
    ch_resize,
    google_chrome_driver_setup,
    save_altair,
)


driv = google_chrome_driver_setup()
VAL_PATH = f"{PROJECT_DIR}/outputs/reports/val_figures"
FIG_PATH = f"{PROJECT_DIR}/outputs/reports/final_report_deck"


def get_focus_countries(countries_wide, n=20):
    return countries_wide.mean(axis=1).sort_values(ascending=False)[:n].index


def plot_correlation_shares(countries_wide):
    """Plots correlation between countries shares of activity"""
    correlation = countries_wide.corr(method="spearman").stack()
    correlation_index = correlation.index.rename(["source_1", "source_2"])
    correlation.index = correlation_index
    correlation = correlation.reset_index(name="coefficient")

    correlation["coefficient_value"] = [
        "" if x == 1 else str(np.round(x, 2)) for x in correlation["coefficient"]
    ]

    correlation_base = (
        alt.Chart(correlation)
        .encode(x="source_1", y="source_2")
        .properties(width=400, height=120)
    )

    correlation_heat = correlation_base.mark_rect().encode(color="coefficient")

    correlation_text = correlation_base.mark_text().encode(
        text="coefficient_value",
        color=alt.condition(
            "datum.coefficient>0.9", alt.ColorValue("white"), alt.ColorValue("black")
        ),
    )

    return correlation_heat + correlation_text


def plot_country_shares(countries_wide, n=20):
    """Plot shares of activity in different article categories for focus countries"""
    focus_countries = get_focus_countries(countries_wide, n)

    countries_long = countries_wide.stack().reset_index(name="share")
    countries_plot = countries_long.loc[countries_long["country"].isin(focus_countries)]

    country_chart = (
        alt.Chart(countries_plot)
        .mark_point(filled=True, stroke="black", size=40, strokeWidth=0.5)
        .encode(
            y=alt.Y(
                "country",
                sort=alt.EncodingSortField("share", op="mean", order="descending"),
            ),
            x=alt.X("share", scale=alt.Scale(type="log"), axis=alt.Axis(format="%")),
            color="article_source",
        )
    )

    return country_chart


def plot_article_trends(articles):

    share_papers = (
        articles.groupby(["month_year", "article_source"])
        .size()
        .unstack()
        .apply(lambda x: x / x.sum())
        .stack()
        .reset_index(name="share")
    )

    # %%
    trend_chart = (
        alt.Chart(share_papers)
        .mark_line(point=True)
        .encode(
            x=alt.X("month_year:T", axis=alt.Axis(format=("%b-%Y")), title=None),
            y=alt.Y(
                "share", axis=alt.Axis(format="%"), title="Share of activity in year"
            ),
            color=alt.Color("article_source", title="Article source"),
        )
    )

    return trend_chart


def train_topic_model(k, art_lookup, sample_size=None):
    """Train topic model while grid searching"""
    logging.info(f"training model with {k} topics")

    mdl = tp.LDAModel(k=k)

    texts = list(art_lookup.values())
    ids = list(art_lookup.keys())

    for t in texts:

        mdl.add_doc(t)

    for _ in range(0, 100, 10):
        mdl.train(10)

    return mdl, ids


def make_article_discipline_lookup(topic_mix, art_disc):

    topic_mix_disc = (
        topic_mix.applymap(lambda x: x > 0.2)
        .reset_index(drop=False)
        .merge(
            art_disc[["article_id", "fos_l0_name"]],
            left_on="index",
            right_on="article_id",
            how="left",
        )
    ).drop(axis=1, labels=["index", "article_id"])

    # Aggregate
    topic_mix_agg = (
        topic_mix_disc.melt(id_vars="fos_l0_name")
        .groupby(["fos_l0_name", "variable"])["value"]
        .sum()
    ).unstack(level=0)

    top_disciplines = (
        topic_mix_agg.sum().sort_values(ascending=False).index[:10].tolist()
    )

    # %%
    # Make LQ
    topic_discipline_lookup = make_lq(topic_mix_agg)[top_disciplines].idxmax(axis=1)

    return topic_discipline_lookup


if __name__ == "__main__":

    arts = get_covid_papers()
    insts = query_arxiv_institute()
    art_disc = query_article_discipline()

    insts_cov = arts[["article_id", "article_source", "mag_id"]].merge(
        insts, on=["article_id"], how="left"
    )

    countries_wide = (
        insts_cov.groupby("article_source")["country"]
        .value_counts()
        .unstack(level=0)
        .fillna(0)
        .apply(lambda x: x / x.sum())
    )

    logging.info("Comparison of activity across sources")
    share_correlation = ch_resize(plot_correlation_shares(countries_wide))

    save_altair(share_correlation, "share_correlation", driver=driv, path=VAL_PATH)

    country_chart = plot_country_shares(countries_wide)
    save_altair(country_chart, "country_shares", driver=driv, path=VAL_PATH)

    arts_2020 = arts.loc[
        (arts["month_year"] > "2020-01-01") & (arts["month_year"] < "2020-12-31")
    ]

    art_trends = plot_article_trends(arts_2020).properties(width=350, height=500)

    save_altair(ch_resize(art_trends), "article_trends", driver=driv, path=FIG_PATH)

    logging.info("Thematic comparison")

    arts_abstr = (
        arts.loc[arts["year"] >= 2020]
        .dropna(axis=0, subset=["abstract"])
        .reset_index(drop=True)
    )

    art_tok = text_pipeline(arts_abstr["abstract"])
    art_tok_lookup = {
        _id: tok for _id, tok in zip(arts_abstr["article_id"], art_tok) if len(tok) > 0
    }

    model, ids = train_topic_model(100, art_tok_lookup)
    print(ids)
    print(len(ids))

    topic_mix = make_topic_mix(model, 100, ids)

    logging.info("Topic regression")

    art_cat = [
        "cord" if v == "cord" else "preprint"
        for v in arts_abstr.set_index("article_id").loc[ids]["article_source"]
    ]

    topic_reg = topic_regression(topic_mix, art_cat, ref_class="cord", log=True)

    # Now we want to assign papers to topics
    topic_discipline_lookup = make_article_discipline_lookup(topic_mix, art_disc)

    # %%
    topic_df = (
        pd.concat(topic_reg)
        .rename(columns={"index": "source", 0: "low", 1: "high"})
        .assign(discipline=lambda df: df["label"].map(topic_discipline_lookup))
        .assign(mean=lambda df: (df["low"] + df["high"]) / 2)
        .dropna(axis=0, subset=["discipline"])
        .sort_values(["discipline", "mean"], ascending=[True, False])
        .reset_index(drop=True)
        .assign(rank=lambda df: df.index)
    )

    topic_df_long = topic_df.melt(
        id_vars=["source", "label", "discipline", "mean", "rank"]
    )

    ch = (
        alt.Chart()
        .mark_point(filled=True, size=10, stroke="black", strokeWidth=0.1)
        .encode(
            y=alt.Y(
                "label",
                # axis=alt.Axis(labels=False, ticks=False),
                sort=alt.EncodingSortField("rank"),
                title="Topic",
            ),
            x=alt.X("mean", scale=alt.Scale(type="linear")),
            color="discipline",
            tooltip=["label"],
            # color='community:N'
        )
    ).properties(width=300, height=800)

    line = (
        alt.Chart()
        .mark_line(strokeWidth=1.5)
        .encode(
            y=alt.Y(
                "label",
                axis=alt.Axis(
                    grid=True,
                    # labels=False, ticks=False,
                    labelFontSize=9,
                ),
                sort=alt.EncodingSortField("rank"),
            ),
            x=alt.X("value", title="Regression confidence interval"),
            detail="label",
            tooltip=["label"],
            color=alt.Color(
                "discipline:N",
                sort=alt.EncodingSortField("discipline"),
                scale=alt.Scale(scheme="tableau20"),
            ),
        )
    ).properties(width=300, height=800)

    rule = (
        alt.Chart()
        .transform_calculate(x="0")
        .mark_rule(strokeDash=[4, 1], stroke="black")
        .encode(x="x:Q")
    )

    topical_focus_chart = alt.layer(line, ch, rule, data=topic_df_long).facet(
        "source", columns=3
    )

    save_altair(
        ch_resize(topical_focus_chart),
        "topical_focus_chart",
        driver=driv,
        path=FIG_PATH,
    )

    logging.info("Publication sequence based on topic")

    # We compare publication trends for papers published in preprint specialist
    # and non-preprint specialist topics
    prep_spec = topic_df.sort_values("mean", ascending=False)[:10]["label"].tolist()
    cord_spec = topic_df.sort_values("mean", ascending=False)[10:]["label"].tolist()

    prep_spec, cord_spec = [
        set(
            chain(
                *[topic_mix.loc[topic_mix[t] > 0.5].index.tolist() for t in topic_group]
            )
        )
        for topic_group in [prep_spec, cord_spec]
    ]

    spec_map = {
        **{ind: "preprint_topic" for ind in prep_spec},
        **{ind: "cord_topic" for ind in cord_spec},
    }

    arts_comp = arts.copy()

    arts_comp["topic_type"] = arts_comp["article_id"].map(spec_map)

    pub_trends_prep = (
        arts_comp.query("article_source=='cord'")
        .query("year>=2020")
        .query("month_year<'2021-01-01'")
        .groupby("topic_type")["month_year"]
        .value_counts()
        .unstack(level=0)
        .apply(lambda x: x / x.sum())
        .stack()
        .reset_index(name="share of papers")
    )

    pub_trends_chart = (
        alt.Chart(pub_trends_prep)
        .mark_line(point=True)
        .encode(
            x=alt.X("month_year", axis=alt.Axis(format="%b-%y")),
            y=alt.Y("share of papers", axis=alt.Axis(format="%")),
            color=alt.Color("topic_type", title=["topic type"]),
        )
    )

    save_altair(ch_resize(pub_trends_chart), "pub_trends", driver=driv, path=FIG_PATH)
