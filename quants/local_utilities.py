from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import matplotlib.pylab as plt

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

def time_me(fn):
    import time
    def _wrapper(*args, **kwargs):
        start = time.perf_counter()
        x = fn(*args, **kwargs)
        print("{} cost {:.3f} second".format(fn.__name__, time.perf_counter() - start))
        return x
    return _wrapper

def find_ticks(ts_code, start_day='2019-01-01'):
    df_days = load_as_df('select * from tickers where ts_code = "{}" and trade_date >= "{}"'.format(ts_code, start_day))
    return df_days

def find_vols(ts_code, start_day='2019-01-01'):
    df_days = trade_days(ts_code, start_day)
    chg_times, vol_times = 0, 0
    try:
        if df_days.shape[0] > 0:
            spec_arr = pd.qcut(np.abs(df_days.pct_chg), 10, duplicates='drop').value_counts()
            bar_chg = spec_arr.keys()[0].left
            bar_vol = pd.qcut(np.abs(df_days.vol), 10).value_counts().keys()[0].left
            chg_times, vol_times = df_days[-10:][df_days.pct_chg > bar_chg].shape[0], df_days[-10:][df_days.vol > bar_vol].shape[0]
    except Exception as e:
        print('ts_code:{}, err:{}'.format(ts_code, e))
    return (ts_code, chg_times, vol_times)

def draw_candle(ticksDF):
    _,ax = plt.subplots(nrows=2, ncols=1, figsize=(16,6))
    # candle chart
    can_ax, vol_ax = ax[0], ax[1]
    can_ax.xaxis_date()
    can_ax.autoscale_view()
    d = date2num(ticksDF.index)
    ochl = zip(d, ticksDF.open, list(ticksDF.close), list(ticksDF.high), list(ticksDF.low))
    mpf.candlestick_ochl(can_ax,quotes=ochl,width=0.6, colorup='red',colordown='green', alpha=0.6)
    # bar chart
    vol_ax.bar(x=d, height=ticksDF.vol, alpha=0.7)
    vol_ax.xaxis_date()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()