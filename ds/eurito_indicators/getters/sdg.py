import os

import pandas as pd

from eurito_indicators import PROJECT_DIR


ANNOTATED_DIR = f'{PROJECT_DIR}/inputs/sdg/annotated'


def load_annotated(sdg):
    """Loads annotated data for a single goal.

    Args:
        sdg (int): An integer from 1 to 16 that corresponds to one of the SDGs.

    Returns:
        A DataFrame of annotated samples of CORDIS projects for the given SDG. 
        The fields are:
            - rcn (int): The RCN unique ID as found in CORDIS
            - label (int): The label of SDG relevance given by a crowd 
                annotator. 0 = not related, 1 = related.
            - title (str): The project title
            - abstract (str): The project abstract (The 'objective' in CORDIS)
    """
    sdg = str(sdg).zfill(2)
    annotated_df = pd.read_csv(
        os.path.join(ANNOTATED_DIR, f'sdg_{sdg}.csv'))

    annotated_df['title'], annotated_df['abstract'] = zip(
        *annotated_df['Text'].apply(_clean_annotated_text))
    annotated_df = (annotated_df
        .drop('Text', axis=1)
        .rename(columns={'ID': 'rcn', 'Label': 'label'}))
    annotated_df['label'] = annotated_df['label'].map({'No': 0, 'Yes': 1})
    return annotated_df


def _clean_annotated_text(text):
    """Cleans text from the format that it was presented to annotators in the 
    S.M.A.R.T data annotation tool. Splits the title from the abstract text 
    and strips any trailing whitespace.

    Returns:
        title (str): The project title
        text (str): The project abstract
    """
    text = text.split('=====')
    title = text[1].strip()
    abstract = text[-1].strip()
    return title, abstract
