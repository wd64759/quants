from pprint import pprint
from functools import reduce
from itertools import product

from trade_days import TradeDays
from trade_strategies.base_strategy import GamblerStrategy
from trade_strategies.mean_strategy import MeanStrategy

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
    
    '''
    get total profiles
    '''
    def get_total_profit(self):
        return 0.0 if len(self.profit_days) == 0 else reduce(lambda a,b: a + b, self.profit_days)

if __name__ == '__main__':
    # 000001.SZ,  000725.SZ
    trade_days = TradeDays(code='000725.SZ', base_date='20200101')
    chosen_strategy = MeanStrategy()
    loopback = TradeLoopBack(trade_days, chosen_strategy)
    loopback.execute_trade()
    pprint('profit:{:.2f}%'.format(loopback.get_total_profit()))
    


