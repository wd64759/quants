from concurrent.futures import ProcessPoolExecutor, as_completed, wait, ALL_COMPLETED
from itertools import product
from pprint import pprint
import io

from trade_days import TradeDays

import pickle

results = []

def calc(a, b):
    return a*b

def main():
    with ProcessPoolExecutor(max_workers=2) as pool:
        p1, p2 = range(1,20, 1), range(-5, -12, -1)
        future_list = []
        for a,b in product(p1, p2):
            future_task = pool.submit(calc, a, b)
            future_task.add_done_callback(lambda x: results.append(x.result()))
            # future_list.append(future_task)
        
        # for job in as_completed(future_list):
        #     results.append(job.result())
            # print('{} to the end'.format(job.result()))
        wait(future_list, return_when=ALL_COMPLETED)

if __name__ == '__main__':
    main()
    trade_days = TradeDays(code='000725.SZ', base_date='20200101')
    # print(sum(results))
    f = io.BytesIO()
    pickle.Pickler(f).dump(trade_days)
    pprint(f)
