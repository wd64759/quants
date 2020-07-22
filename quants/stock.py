from local_utilities import *

from collections import namedtuple
from sqlalchemy import create_engine
from pprint import pprint

class Stock(object):
    def __init__(self, code, base_date=None):
        self.__ts_code = code
        self.__init_hist()

    def __init_hist(self):
        stock_hist = load_as_df('select * from tickers where ts_code = "{}"'.format(self.__ts_code))
        self.__price_array = list(stock_hist['close'])
        self.__date_array  = list(stock_hist['trade_date'])

    def __str__(self):
        return str(self.__ts_code)
    __repr__ = __str__

    def __len__(self):
        return len(self.__price_array)
    
if __name__ == '__main__':
    stock = Stock(code='000725.SZ')
    pprint(len(stock))