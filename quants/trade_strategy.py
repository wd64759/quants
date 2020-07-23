import six
from abc import ABCMeta, abstractmethod
from pprint import pprint

class TradeStrategyBase(metaclass = ABCMeta):
    @abstractmethod
    def buy_strategy(self, *args, **kwargs):
        pass

    @abstractmethod
    def sell_strategy(self, *args, **kwargs):
        pass

class GamblerStrategy(TradeStrategyBase):
    '''
    class level attribute - kinds of static property
    '''
    s_keep_stock_threhold = 20
    def __init__(self):
        self.keep_days = 0
        # 7%
        self.__buy_change_threshold = 7

    def buy_strategy(self, trade_ind, trade_day, trade_days):
        if self.keep_days == 0 and trade_day.change > self.__buy_change_threshold:
            pprint('buy on {}, at {:.2f}'.format(trade_day.date, trade_day.price))
            self.keep_days = 1
        elif self.keep_days > 0:
            self.keep_days += 1

    def sell_strategy(self, trade_ind, trade_day, trade_days):
        if self.keep_days >= GamblerStrategy.s_keep_stock_threhold:
            pprint('sell on {}, at {:.2f}'.format(trade_day.date, trade_day.price))
            self.keep_days = 0

    @property
    def buy_change_threshold(self):
        return self.__buy_change_threshold

    @buy_change_threshold.setter
    def buy_change_threshold(self, buy_change_threshold):
        if not isinstance(buy_change_threshold, float):
            raise TypeError('buy_change_threshold must be float')
        self.__buy_change_threshold = buy_change_threshold


if __name__ == '__main__':
    gs = GamblerStrategy()
    gs.buy_change_threshold = 0.6
    pprint(gs.buy_change_threshold)