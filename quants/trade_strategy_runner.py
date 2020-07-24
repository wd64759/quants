from itertools import product
from pprint import pprint

from trade_days import TradeDays
from trade_loopback import TradeLoopBack
from trade_strategies.mean_strategy import MeanStrategy

class StrategySelector(object):

    def __init__(self, trade_strategy, trade_days):
        self.chosen_strategy = trade_strategy
        self.trade_days = trade_days

    def run_loopback(self, keep_days_threshold, buy_change_threshold):
        self.chosen_strategy.set_buy_change_threshold(buy_change_threshold)
        self.chosen_strategy.set_keep_days_threshold(keep_days_threshold)
        
        loopback = TradeLoopBack(self.trade_days, self.chosen_strategy)
        loopback.execute_trade()
        return (loopback.get_total_profit(), keep_days_threshold, buy_change_threshold)

    def rank_strategy(self, tops=10):
        hold_day_list = range(2, 30, 2)
        buy_threshold_list = range(-5, -12, -1)
        profit_rec = []
        for keep_days_threshold, buy_change_threshold in product(hold_day_list, buy_threshold_list):
            total_return = self.run_loopback(keep_days_threshold, buy_change_threshold)
            profit_rec.append((total_return[0], keep_days_threshold, buy_change_threshold))
        return sorted(profit_rec, key=lambda x: x[0])[::-1][:tops]

if __name__ == '__main__':
    trade_days = TradeDays(code='000725.SZ', base_date='20200101')
    ss = StrategySelector(MeanStrategy(), trade_days)
    profit_rec = ss.rank_strategy(20)
    pprint(profit_rec)