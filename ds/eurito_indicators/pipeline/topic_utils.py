# Topic modelling related utils (tomotopy)
import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import tomotopy as tp
from statsmodels.regression.linear_model import OLS

def get_topic_words(topic, top_words=5):
    """Extracts main words for a topic"""

    return "_".join([x[0] for x in topic[:top_words]])


def make_topic_mix(mdl, num_topics, doc_indices):
    """Takes a tomotopy model and products a topic mix"""
    topic_mix = pd.DataFrame(
        np.array([mdl.docs[n].get_topic_dist() for n in range(len(doc_indices))])
    )

    topic_mix.columns = [
        get_topic_words(mdl.get_topic_words(n, top_n=5)) for n in range(num_topics)
    ]

    topic_mix.index = doc_indices
    return topic_mix


def parse_var_name(var):
    """Parses regression outputs when using a reference class"""

    return var.split(".")[1][:-1].strip()


def topic_regression(topic_mix, cat_vector, ref_class, log=True):
    """Carries out a topic regression using a vector of categorical variables as
    predictors. Equivalent to a comparison of means between a category and the
    reference class
    """

    results = []

    for t in topic_mix.columns:

        # We log the results to account for skewedness
        top = topic_mix[t].reset_index(drop=True)

        min_val = top.loc[top > 0].min()

        # We create a floor above zero so we can log all topic values
        if log is True:
            zero_rep = (0 + min_val) / 2

            y = [np.log(x) if x > 0 else np.log(zero_rep) for x in top]
        else:
            y = top.copy()

        reg_df = pd.DataFrame({"y": y, "x": cat_vector})

        if ref_class != None:
            m = smf.ols(
                formula=f"y ~ C(x, Treatment(reference='{ref_class}'))", data=reg_df
            ).fit()
            confint = m.conf_int().assign(label=t).iloc[1:, :].reset_index(drop=False)
            confint["index"] = [parse_var_name(v) for v in confint["index"]]
            results.append(confint)

        else:

            confint = []
            exog = pd.get_dummies(reg_df["x"])
            for e in exog.columns:
                one_var = sm.add_constant(exog[e])
                m = OLS(endog=reg_df["y"], exog=one_var).fit()
                confint_one = (
                    m.conf_int().assign(label=t).iloc[1:, :].reset_index(drop=False)
                )
                confint.append(confint_one)
            results.append(pd.concat(confint))

    return results

def train_topic_model(k, texts, ids):
    """Train topic model while grid searching"""
    logging.info(f"training model with {k} topics")

    mdl = tp.LDAModel(k=k)

    for t in texts:

        mdl.add_doc(t)

    for _ in range(0, 100, 10):
        mdl.train(10)

    return mdl, ids