from sqlalchemy import create_engine
import pandas as pd

from config_loader import cf as config

__dbURL = config.get('MYSQL_DB', 'conn')
__engine = create_engine(__dbURL, encoding='utf-8', connect_args={'auth_plugin': 'mysql_native_password'})

def load_as_df(query):
    return pd.read_sql_query(query, __engine)

def run_sql(query):
    return __engine.execute(query).fetchall()

def save_to_tbl(tbl, dataset):
    if not isinstance(dataset, pd.Dataframe):
        raise TypeError('dataset is not DataFrame')
    dataset.to_sql(tbl, con=__engine, if_exists='append', index=False)

def trunc(tbl):
    run_sql('truncate table {}'.format(tbl))
