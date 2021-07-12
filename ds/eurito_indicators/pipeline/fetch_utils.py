# Utilities to fetch data from DAPS

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from configparser import ConfigParser
import pandas as pd


def get_engine(config_path, database="production", **engine_kwargs):
    '''Get a SQL alchemy engine from config'''
    cp = ConfigParser()
    cp.read(config_path)
    cp = cp["client"]
    url = URL(drivername="mysql+pymysql", database=database,
              username=cp["user"], host=cp["host"], password=cp["password"])
    return create_engine(url, **engine_kwargs)

def fetch_daps_table(table, con, chunks=1000):
    '''Fetch a DAPS table
    '''

    ch = pd.read_sql_table(table, con, chunksize=chunks)

    return pd.concat(ch).reset_index(drop=True)