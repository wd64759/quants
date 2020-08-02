import numpy as np
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, as_completed
from local_utilities import time_me
import matplotlib.pyplot as plt

def casino(win_rate, win_once=1, lose_once=1, commission=0.01):
    init_money = 10000
    play_times = 100000
    for _ in np.arange(0, play_times):
        w = np.random.binomial(1, win_rate)
        if w:
            init_money += win_once
        else:
            init_money -= lose_once
        init_money -= commission
        if init_money<=0:
            init_money = 0
            break
    return init_money

@time_me
def start(gamblers=2):
    results = []
    with ProcessPoolExecutor(max_workers=12) as pool:
        tasks = []
        for _ in np.arange(0, gamblers):
            task = pool.submit(casino, 0.5, 1, 1, 0.01)
            tasks.append(task)
        
        for job in as_completed(tasks):
            results.append(job.result())
    return results

if __name__ == '__main__':
    rs = start(20)
    plt.hist(rs, bins=30)
    plt.show()
    # print(rs)