import pandas as pd
import tushare as ts
from sqlalchemy import create_engine
from config_loader import cf as config


import time
from datetime import datetime

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class StockFetcher(object):

    '''
    tsshare API封装
    '''
    def __init__(self):
        super().__init__()
        token = config.get('STOCK_SERVER', 'token')
        ts.set_token(token)
        self.pro = ts.pro_api()
    
    def fetch_calendar(self, start_date, end_date=None):
        now_str = datetime.now().strftime('%Y%m%d') if end_date is None else end_date
        calDF = self.pro.trade_cal(exchange='', start_date=start_date, end_date=now_str)
        openDF = calDF.loc[calDF["is_open"] == 1]
        return openDF['cal_date'].tolist()
    
    def fetch_stock_info(self, ts_code):
        stockDF = self.pro.stock_basic()
        if len(stockDF):
            return list(stockDF[stockDF.ts_code == ts_code].T.to_dict().values())[0]

    def fetch_stock_basic(self):
        stockDF = self.pro.stock_basic()
        return stockDF

    def fetch_daily_tickers(self, trade_date):
        return self.pro.daily(trade_date=trade_date)

    def fetch_stock_adjfactors(self, ts_code):
        adjDF = self.pro.adj_factor(ts_code=ts_code, trade_date='')
        adjDF['trade_date'] = pd.to_datetime(adjDF['trade_date'])
        return adjDF

    def fetch_ticker_hist(self, ts_code):
        try:
            stock_id = ts_code[:-3]
            df = ts.get_hist_data(stock_id)
            df['trade_date'] = df.index
            df['ts_code'] = ts_code
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception as e:
            logging.error('Fail to fetch history data for {}'.format(ts_code))
            logging.error(str(e))
            return None

class StockLoader(object):
    
    '''
    数据库的操作    
    '''
    def __init__(self):
        super().__init__()
        dbURL = config.get('MYSQL_DB', 'conn')
        self.engine = create_engine(dbURL, encoding='utf-8')
        self.data_dict = {
            'stocks':'base_stocks', 
            'tickers': 'tickers', 
            'companies': 'pub_companies', 
            'mkt_indexes': 'shibor'}
    
    def load_stock_list(self):
        sql = 'SELECT * FROM {}'.format(self.data_dict['stocks'])
        try:
            return pd.read_sql_query(sql, self.engine)
        except Exception as e:
            logging.error('Fail to load stocks from DB')
            logging.error(str(e))
            return None

    def save_ticker(self, tickerDF):
        tickerDF.to_sql(self.data_dict['tickers'], con=self.engine, if_exists='append', index=False)
        logging.info('save completed - {:d}'.format(len(tickerDF)))

    def save_stock_basic(self, stock_basic):
        tbl_name = self.data_dict['stocks']
        if len(stock_basic) > 0:
            with self.engine.connect() as conn:
                conn.execute('truncate table {}'.format(tbl_name))
            stock_basic.to_sql(tbl_name, con=self.engine, if_exists='append', index=False)
            logging.info('{:d} records saved into {}'.format(len(stock_basic), tbl_name))

    def load_ticker_hist(self, ts_code):
        dailyDF = pd.read_sql_query('select * from tickers where ts_code="{}"'.format(ts_code), con = self.engine, parse_dates=['trade_date'])
        # dailyDF['trade_date'] = pd.to_datetime(dailyDF['trade_date'])
        return dailyDF
    
    '''
    load tickers of the given date range
    '''
    def load_tickers_hist(self, start_date, end_date=datetime.now().strftime('%Y%m%d')):
        tickerDF = pd.read_sql_query('select * from tickers where trade_date between "{}" and "{}"'.format(start_date, end_date), con = self.engine, parse_dates=['trade_date'])
        # tickerDF['trade_date'] = pd.to_datetime(tickerDF['trade_date'])
        return tickerDF

    def load_companies(self, ts_code=None):
        queryStr = 'select * from pub_companies' if ts_code is None else "select * from pub_companies where ts_code = '{}'".format(ts_code)
        companyDF = pd.read_sql_query(queryStr, con = self.engine, parse_dates=['setup_date'])
        # companyDF['setup_date'] = pd.to_datetime(companyDF['setup_date'])
        return companyDF
    
    def load_stock_basic(self, ts_code=None):
        queryStr = 'select * from base_stocks' if ts_code is None else "select * from base_stocks where ts_code = '{}'".format(ts_code)
        basicDF = pd.read_sql_query(queryStr, con = self.engine, parse_dates=['list_date'])
        # basicDF['list_date'] = pd.to_datetime(basicDF['list_date'])
        return basicDF        

    '''
    delete tickers by given ts_code and trade_date (optional)
    '''    
    def clean_tickers(self, ts_code, trade_date=None):
        if ts_code is None:
            return
        try:
            with self.engine.connect() as conn:
                delSQL = "DELETE FROM {} WHERE ts_code = '{}'".format(self.data_dict['tickers'], ts_code)
                if trade_date is not None:
                    delSQL += " and trade_date = '{}' ".format(trade_date)
                conn.execute(delSQL)
        except Exception as e:
            logging.error(str(e))
    
    '''
    remove tickers of a given date
    '''
    def clean_tickers_of_date(self, trade_date):
        if trade_date is None:
            return
        
        try:
            with self.engine.connect() as conn:
                conn.execute("DELETE FROM {} WHERE trade_date = '{}'".format(self.data_dict['tickers'], trade_date))
        except Exception as e:
            logging.error(str(e))

'''
旧API的daily数据刷新，已经废弃
'''
def rebuildTickers():
    logging.info('start rebuilding ...')
    sLoader = StockLoader()
    sFetcher = StockFetcher()

    df = sLoader.load_stock_list()
    ts_code_list = df['ts_code'].tolist()
    for ts_code in ts_code_list:
        tickerDF = sFetcher.fetch_ticker_hist(ts_code)
        if tickerDF is not None:
            print('saving tickers for {}'.format(ts_code))
            sLoader.save_ticker(tickerDF)


sLoader = StockLoader()
sFetcher = StockFetcher()

'''
将ticker数据刷新到数据库中
e.g.
    start_date, end_date = '20150101', '20151231'
    refreshTickers(start_date, end_date)
'''
def refreshTickers(start_date, end_date):
    logging.info('start refresh tickers ...')

    tradeDtList = sFetcher.fetch_calendar(start_date, end_date)
    for trDt in tradeDtList:
        tickersDF = sFetcher.fetch_daily_tickers(trDt)
        if len(tickersDF) > 0:
            logging.info('start saving tickers of {}'.format(trDt))
            sLoader.clean_tickers_of_date(trDt)
            sLoader.save_ticker(tickersDF)

'''
股票基本信息
'''
def refreshStockInfo():
    sLoader.save_stock_basic(sFetcher.fetch_stock_basic())

def main():
    start_date, end_date = '20200707', '20200710'
    refreshTickers(start_date, end_date)
    refreshStockInfo()
    # sLoader = StockLoader()
    # sLoader.delTicker(ts_code='000829.SZ', trade_date='20200616')
    # sLoader.delTickerByDate(trade_date='20200616')

if __name__ == '__main__':
    main()