from pprint import pprint
from functools import reduce

from stock import TradeDays
from trade_strategy import GamblerStrategy

class TradeLoopBack(object):
    def __init__(self, trade_days, trade_strategy):
        self.trade_days = trade_days
        self.trade_strategy = trade_strategy
        self.profit_days = []
    
    '''
    use enumerate to get index of a iterator object with its value
    '''
    def execute_trade(self):
        for ind, trade_day in enumerate(self.trade_days):
            if self.trade_strategy.keep_days > 0:
                self.profit_days.append(trade_day.change)
            if hasattr(self.trade_strategy, 'buy_strategy'):
                self.trade_strategy.buy_strategy(ind, trade_day, self.trade_days)
            
            if hasattr(self.trade_strategy, 'sell_strategy'):
                self.trade_strategy.sell_strategy(ind, trade_day, self.trade_days)

if __name__ == '__main__':
    trade_days = TradeDays(code='000725.SZ', base_date='20200101')
    loopback = TradeLoopBack(trade_days, GamblerStrategy())
    loopback.execute_trade()
    pprint('{:.2f}%'.format(reduce(lambda a, b: a + b, loopback.profit_days)))
