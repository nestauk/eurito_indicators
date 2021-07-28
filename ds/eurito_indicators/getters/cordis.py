import json
import os
import pandas as pd

from eurito_indicators import project_dir
from eurito_indicators.utils.misc_utils import camel_to_snake


FRAMEWORK_PROGRAMMES = ['fp1', 'fp2', 'fp3', 'fp4', 'fp5', 'fp6', 'fp7', 'h2020']

CORDIS_DIR = f'{project_dir}/inputs/cordis'


def cordis_file_path(fp_name, resource_name):
    '''Create the file path for a CORDIS dataset given a Framework Programme 
    and an entity such as projects or organizations.

    Args:
        fp_name (str): Name of Framework Programme (from FRAMEWORK_PROGRAMMES)
        resource_name (str): Entity type. One of `projects` or `organizations`

    Returns:
        (str): File path 
    '''
    fname = f'{fp_name}_{resource_name}.csv'
    return os.path.join(CORDIS_DIR, f'{fp_name}/{fname}')


def load_cordis_projects(fp_name):
    '''load_cordis
    Load a datasets of CORDIS projects.

    Args:
        fp_name (str): Name of Framework Programme
        resource_name (str): Entity type e.g., projects, organizations

    Returns:
        (pd.DataFrame): Parsed CORDIS data
    '''
    resource_name = 'projects'
    fin = cordis_file_path(fp_name, resource_name)
    with open(f'{CORDIS_DIR}/cordis_parse_opts.json', 'r') as f:
        parse_opts = json.load(f)[resource_name]

    with open(f'{CORDIS_DIR}/cordis_read_opts.json', 'r') as f:
        read_opts = json.load(f)[resource_name]
    
    df = pd.read_csv(fin, **read_opts)
    df = _parse_cordis_projects(df, **parse_opts)

    if fp_name == 'fp6':
        df = _parse_fp6_projects(df)
    return df


def load_all_cordis_projects():
    '''load_all_cordis_projects
    Loads projects for all CORDIS Framework Programmes as a single DataFrame.

    Args:
        resource_name (str): Entity type e.g., projects, organizations

    Returns:
        (pd.DataFrame): Parsed CORDIS projects for all Framework Programmes
    '''
    fps = ['h2020', 'fp7', 'fp6', 'fp5', 'fp4', 'fp3', 'fp2', 'fp1']
    dfs = []
    for fp in fps:
        dfs.append(load_cordis_projects(fp))
    return pd.concat(dfs)


def _parse_cordis_projects(df, list_cols, list_sep, drop_cols):
    '''parse_cordis_projects
    Parse and clearn raw CORDIS data.
    ''' 
    for col in list_cols:
        df[col] = df[col].str.split(list_sep)

    df = df.drop(drop_cols, axis=1)
    df.columns = [camel_to_snake(col) for col in df.columns]
    return df


def _parse_fp6_projects(df):
    '''parse_fp6_projects
    Correct an issue where some space characters exist in FP6 funding data.
    '''
    correct_cols = ['ec_max_contribution', 'total_cost']
    for c in correct_cols:
        df[c] = (df[c]
                .str.replace(',', '.')
                .str.replace(' ', '')
                .astype(float))
    return df

