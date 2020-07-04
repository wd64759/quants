from stock_proc import sLoader as sl, sFetcher as sf

import pandas as pd
import numpy as np

from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# cnfont = fm.FontProperties(fname=r'C:\Windows\Fonts\simkai.ttf')
plt.rcParams['font.family'] = 'SimHei'

class AnaStock(object):
    '''
    分析函数
    '''
    def __init__(self, ts_code):
        super().__init__()
        self.ts_code = ts_code
       

    def pre_data(self):
        self.tickers = self.get_stock_with_adj()
        self.basic = sf.fetch_stock_info(ts_code=self.ts_code)

    def build_index(self):
        close = self.tickers[['close','trade_date']]
        close.reset_index()
        close['trade_date'] = close['trade_date'].map(matplotlib.dates.date2num)
        close.set_index('trade_date')
        
        ohlc = self.tickers[['open', 'high', 'low', 'close', 'trade_date']]
        ohlc.reset_index()
        ohlc['trade_date'] = ohlc['trade_date'].map(matplotlib.dates.date2num)
        ohlc.set_index('trade_date')
        self.close, self.ohlc = close, ohlc

    def draw_plot(self):
        subplot1 = plt.subplot2grid((2,1), (0,0), rowspan=1, colspan=1)
        subplot1.xaxis_date()
        subplot1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))

        subplot1.plot(self.close['trade_date'], self.close['close'], 'b.')
        # plt.title(self.basic['name'], fontproperties=cnfont)
        plt.title(self.basic['name'])
        plt.show()

    def get_stock_with_adj(self):
        tickers = sl.load_ticker_hist(ts_code=self.ts_code)
        adjDF = sf.fetch_stock_adjfactors(self.ts_code)
        return pd.merge(tickers, adjDF)

class AnaMarket(object):
    def __init__(self, mkt_type):
        super().__init__()
        

class AnaUtil(object):
    def __init__(self):
        super().__init__()


    def set_filter(self, my_filter):
        self.my_filter = my_filter

    def clean_filter(self):
        delattr(self, 'my_filter')

    '''
    e.g. '000008.SZ'
    '''
    def g_tickers(self, ts_code):
        theStock = AnaStock(ts_code)
        theStock.pre_data()
        theStock.build_index()
        theStock.draw_plot()
    
    def g_line(self, d, x_idx='trade_date'):
        p = plt.subplot()
        p.xaxis_date()
        dims = d.columns.tolist()
        dims.remove(x_idx)
        for fig in dims:
            p.plot(d[x_idx], d[fig], marker='o', label=fig)

        p.legend()
        p.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))
        plt.show()

    def g_pie(self, d_series, title=''):
        p_data = d_series.sort_values(ascending=False)[:10]
        x_vals = p_data.values.tolist()
        x_max = np.max(x_vals)
        explode = [x/x_max*.2 for x in x_vals]
        plt.pie(x_vals, labels=p_data.index.tolist(), explode=explode, autopct='%1.2f%%')
        plt.title(title, y=-0.1)
        plt.show()

    def top_performers(self, trade_date=datetime.now().strftime('%Y%m%d'), tpNum=50):
        tickersDF = sl.load_tickers_hist(trade_date)
        stock_names = sl.load_stock_list()
        stock_tops = pd.merge(tickersDF, stock_names)

        if hasattr(self, 'my_filter'):
            stock_tops = self.my_filter(stock_tops)

        return stock_tops.sort_values(by=['pct_chg', 'vol'], ascending=False)[:tpNum]
        # return pd.merge(stock_tops, stock_names)

    '''
    category: market, industry
    '''
    def top_category(self, category, start_date, end_date, tpNum=50):
        d = pd.DataFrame()
        for trade_date in sf.fetch_calendar(start_date=start_date, end_date=end_date):
            df = self.top_performers(trade_date=trade_date, tpNum=tpNum)
            x = df.groupby(df[category]).size()
            x = x.append(pd.Series(trade_date, index=['trade_date']))
            d = d.append(x, ignore_index=True)

        d['trade_date'] = d['trade_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d')).map(matplotlib.dates.date2num)
        d.reset_index()
        d.set_index('trade_date')
        return d

ana = AnaUtil()

def find_mkt_trend(category='market', start_date=datetime.now() - timedelta(days=5), end_date=datetime.now()):
    # .strftime('%Y%m%d')
    df = ana.top_category(category='market', start_date=start_date, end_date=end_date)
    ana.g_line(df)

def find_ticks_trend(ts_code):
    ana.g_tickers(ts_code)

def find_mkt_share(category='industry', tpNum=50, start_date=datetime.now() - timedelta(days=5), end_date=datetime.now()):
    df = ana.top_category(category=category, tpNum=tpNum, start_date=start_date, end_date=end_date).fillna(0)
    del df['trade_date'] 
    ana.g_pie(df.sum(), title='{0} to {1} '.format(start_date.strftime('%b %d'), end_date.strftime('%b %d')))

def mkt_filter(df):
    ''' 主板，中小板，创业板， 科创板 '''
    return df.loc[df["market"] == '主板']

def main():
    # df = ana.top_performers(trade_date='20200701')
    # print(df[['name', 'market', 'industry', 'list_date', 'pct_chg', 'vol', 'open', 'high', 'low', 'close', 'pre_close']])
    # ana.g_tickers('300841.SZ')

    # ana.set_filter(mkt_filter)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=8)
    find_mkt_trend(start_date=start_date, end_date=end_date)
    # find_mkt_share(tpNum=100, start_date=start_date, end_date=end_date)

if __name__ == '__main__':
    main()