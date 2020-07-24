from local_utilities import *

from collections import namedtuple, OrderedDict
from datetime import date, datetime
from sqlalchemy import create_engine
from pprint import pprint

class TradeDays(object):
    def __init__(self, code, base_date=None):
        self.__ts_code = code
        self.__base_date = base_date
        self.__init_hist()

    def __init_hist(self):
        data_criteria = "and trade_date >= '{}'".format(self.__base_date) if self.__base_date is not None else ''
        stock_hist = load_as_df('select * from tickers where ts_code = "{}" {}'.format(self.__ts_code, data_criteria))
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

    def get_window(self, start_dt_str, end_dt_str=None):
        end_dt =  datetime.now().date() if end_dt_str is None else datetime.strptime(end_dt_str, '%Y%m%d').date()
        start_dt = datetime.strptime(start_dt_str, '%Y%m%d').date()
        return list(filter(lambda s: s.date>=start_dt and s.date<=end_dt, self.__stocks.values()))

if __name__ == '__main__':
    trade_days = TradeDays(code='000725.SZ', base_date='20200101')
    pprint(len(trade_days))
    # x = trade_days.get_window(start_dt_str='20200701')
    # pprint(x)
    pprint(trade_days[10])
    # pprint([x for x in trade_days][:10])
    # print(trade_days[-1])
