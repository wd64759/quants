from itertools import product
from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
from pprint import pprint

from local_utilities import time_me
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

    @time_me
    def rank_strategy(self, tops=10):
        hold_day_list = range(1, 60, 1)
        buy_threshold_list = range(-1, -15, -1)
        profit_rec = []

        for keep_days_threshold, buy_change_threshold in product(hold_day_list, buy_threshold_list):
            total_return = self.run_loopback(keep_days_threshold, buy_change_threshold)
            profit_rec.append((total_return[0], keep_days_threshold, buy_change_threshold))
        all_calc = sorted(profit_rec, key=lambda x: x[0])
        print('total calc:{}'.format(len(all_calc)))
        return all_calc[::-1][:tops]

    '''
    use muti-process pool to accelerate the process
    '''
    @time_me
    def multi_proc_ranking(self, tops=10):
        profit_rec, future_list = [], []
        hold_day_list, buy_threshold_list = range(1, 60, 1), range(-1, -15, -1)
        with ProcessPoolExecutor(max_workers=6) as pool:
            for keep_days_threshold, buy_change_threshold in product(hold_day_list, buy_threshold_list):
                future_task = pool.submit(self.run_loopback, keep_days_threshold, buy_change_threshold)
                future_task.add_done_callback(lambda x: profit_rec.append(x.result()))
                future_list.append(future_task)
            
        wait(future_list, return_when=ALL_COMPLETED)
        return sorted(profit_rec, key=lambda x: x[0])[::-1][:tops]

if __name__ == '__main__':
    trade_days = TradeDays(code='000725.SZ', base_date='20190101')
    ss = StrategySelector(MeanStrategy(), trade_days)
    # profit_rec = ss.rank_strategy(20)
    profit_rec = ss.multi_proc_ranking(20)
    # 1.92
    pprint(profit_rec)