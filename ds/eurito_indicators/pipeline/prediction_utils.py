# Utilities for discipline and industry prediction
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier


def parse_parametres(parametre_list: list) -> list:
    """Parse Nones in a parameter dict"""
    parametre_copy = []

    for el in parametre_list:
        new_dict = {}
        for k, v in el.items():
            new_dict[k] = [par if par != "None" else None for par in v]
        parametre_copy.append(new_dict)

    return parametre_copy


def make_doc_term_matrix(
    training_features, transformer, max_features=50000, rescale=True
):
    """Creates a document term matrix"""

    # Create and apply tfidf transformer
    vect = transformer(
        ngram_range=[1, 2], stop_words="english", max_features=max_features
    )
    fit = vect.fit(training_features)

    # Create processed text

    X_proc = fit.transform(training_features)

    return fit, X_proc


def grid_search(X, y, model, parametres, metric):
    """Performs grid search for a model and parametre grid"""

    estimator = OneVsRestClassifier(model)
    clf = GridSearchCV(estimator, parametres, scoring=metric, cv=3)
    clf.fit(X, y)
    return clf


def make_predicted_label_df(
    documents,
    vectoriser,
    estimator,
    y_cols,
    text_var="abstractText",
    id_var="project_id",
    min_length=300,
):
    """Takes an unlabelled collection of text documents, vectorises it and predicts labels"""

    documents_not_empty = documents.dropna(axis=0, subset=[text_var])

    documents_long = documents_not_empty.loc[
        [len(desc) > min_length for desc in documents_not_empty[text_var]]
    ]

    docs_vect = vectoriser.transform(documents_not_empty[text_var])

    pred = estimator.predict_proba(docs_vect)

    pred_df = pd.DataFrame(pred, index=documents_long[id_var], columns=y_cols)

    return pred_df
