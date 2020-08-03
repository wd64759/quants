import numpy as np

# a = np.linspace(0,1,100)
trade_days = 200
stocks = 50
hist = np.random.standard_normal((stocks, trade_days))
print(hist[:2,-20:])
2     