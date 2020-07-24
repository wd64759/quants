from trade_strategies.base_strategy import TradeStrategyBase

class MeanStrategy(TradeStrategyBase):
    keep_days_threshold = 20
    buy_change_threshold = -8
    profit_change_threshold = 8

    def __init__(self):
        self.keep_days = 0
        self.profit_sum = 0

    def buy_strategy(self, trade_ind, trade_day, trade_hist):
        pre_change, cur_change = trade_hist[trade_ind-1].change, trade_hist[trade_ind].change
        if (self.keep_days == 0 
                and pre_change < 0 
                and cur_change < 0 
                and sum([pre_change, cur_change]) < MeanStrategy.buy_change_threshold ):
            print('buy on {}, at {:.2f}'.format(trade_day.date, trade_day.price))
            self.keep_days = 1
        elif self.keep_days > 0:
            self.keep_days += 1
            self.profit_sum += cur_change

    def sell_strategy(self, trade_ind, trade_day, trade_hist):
        if (self.keep_days >= MeanStrategy.keep_days_threshold 
                or self.profit_sum >= MeanStrategy.profit_change_threshold):
            print('sell on {}, with profits chg {:.2f}'.format(trade_day.date, self.profit_sum))
            self.keep_days = 0
            self.profit_sum = 0

    @staticmethod
    def set_buy_change_threshold(buy_change_threshold):
        MeanStrategy.buy_change_threshold = buy_change_threshold
    
    @classmethod
    def set_profit_change_threshold(cls, profit_change_threshold):
        cls.profit_change_threshold = profit_change_threshold

    @classmethod
    def set_keep_days_threshold(cls, keep_days_threshold):
        cls.keep_days_threshold = keep_days_threshold

    def __str__(self):
        return 'MeanStrategy'

if __name__ == '__main__':
    tradeStrategy = MeanStrategy()
    print(tradeStrategy)