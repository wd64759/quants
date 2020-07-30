import numba as nb
from numba import jit

from timeit import timeit
from pprint import pprint

from trade_strategy_runner import StrategySelector
from trade_days import TradeDays
from trade_strategies.mean_strategy import MeanStrategy

@jit
def calc():
    trade_days = TradeDays(code='000153.SZ', base_date='20150101')
    ss = StrategySelector(MeanStrategy, trade_days)
    top_params = ss.rank_strategy(tops=10)
    pprint(top_params)

if __name__ == '__main__':
    # main() cost: 2.056 sec
    # calc_nb = nb.jit(calc)
    # calc_nb()
    calc()
