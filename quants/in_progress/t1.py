from timeit import Timer
import numpy as np
from pprint import pprint

def normal():
    [i**2 for i in range(10000)]

def np_test():
    np.arange(10000)**2

# t1 = Timer('normal()', setup='from __main__ import normal')
# t2 = Timer('np_test()', 'from __main__ import np_test')
# print(t1.timeit(1000))
# print(t2.timeit(1000))
pprint(np.empty((2,3,4)))