from local_utilities import *

from collections import namedtuple, OrderedDict
from datetime import date, datetime
from sqlalchemy import create_engine
from pprint import pprint

class TradeDays(object):
    def __init__(self, code, base_date=None):
        self.__ts_code = code
        self.__init_hist()

    def __init_hist(self):
        stock_hist = load_as_df('select * from tickers where ts_code = "{}"'.format(self.__ts_code))
        stock_tuple = namedtuple('stock', ('date', 'price', 'change', 'volume'))
        self.__stocks = OrderedDict((x[0], stock_tuple(x[0], x[1], x[2], x[3])) for x in zip(stock_hist['trade_date'], stock_hist['close'], stock_hist['pct_chg'], stock_hist['vol']))
        self.__price_array = [ x.price for x in self.__stocks.values() ]
        self.__date_array  = [ x.date for x in self.__stocks.values() ]
    
    def __str__(self):
        return str(self.__ts_code)
    __repr__ = __str__

    def __len__(self):
        return len(self.__price_array)

    def __iter__(self):
        for key in self.__stocks:
            yield self.__stocks[key]
    
    def __getitem__(self, ind):
        date_key = self.__date_array[ind]
        return self.__stocks[date_key]

    def get_window(self, start_dt, end_dt=date.today()):
        rs = filter(lambda s: s.date>=start_dt and s.date<=end_dt, self.__stocks.values())
        return rs

if __name__ == '__main__':
    trade_days = TradeDays(code='000725.SZ')
    pprint(len(trade_days))
    # x = stock.get_hist(start_dt=datetime.strptime('20200701', '%Y%m%d').date())
    # print([x for x in stock][:10])
    print(trade_days[-1])
