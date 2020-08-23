from abc import ABCMeta, abstractmethod
import numpy as np
import scipy.optimize as sco

class Person(object):
    def __init__(self):
        super().__init__()
        self.lifetime = 27375
        self.happiness = 0
        self.wealth = 0
        self.fame = 0
        self.living_days = 0
    
    def live_one_day(self, lifeway):
        days, happiness, wealth, fame = lifeway.oneday()
        self.lifetime -= days
        self.happiness += happiness
        self.wealth += wealth
        self.fame += fame
        self.living_days += 1
    
    def __str__(self):
        return 'living:{:.2f}, happiness:{:.2f}, wealth:{:.2f}, fame:{:.2f}'.format(self.living_days/365, self.happiness, self.wealth, self.fame)
    
class BaseLifeway(metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.health_base = 0
        self.happiness_base = 0
        self.wealth_base = 0
        self.fame_base = 0
        self.health_factor = [0]
        self.happiness_factor = [0]
        self.wealth_factor = [0]
        self.fame_factor = [0]
        self.take_days = 0
        self._init_self()

    @abstractmethod
    def _init_self(self, *args, **kwargs):
        pass 

    @abstractmethod
    def _gen_factors(self, *args, **kwargs):
        pass
    
    def oneday(self):
        cost_func = lambda m_base, m_factor: m_base * (m_factor[self.take_days] if self.take_days<len(m_factor) else m_factor[-1]) 
        # health = (self.lifetime_factor[self.take_days] if len(self.lifetime_factor)<self.take_days else self.lifetime_factor[-1]) * health_base
        health = cost_func(self.health_base, self.health_factor)
        happiness = cost_func(self.happiness_base, self.happiness_factor)
        wealth = cost_func(self.wealth_base, self.wealth_factor)
        fame = cost_func(self.fame_base, self.fame_factor)
        self.take_days += 1
        return health, happiness, wealth, fame

def regular_mm(group):
    return (group - group.min()) / (group.max() - group.min())

class HealthDay(BaseLifeway):
    def _init_self(self):
        self.health_base = 1
        self.happiness_base = 1
        self._gen_factors()

    def _gen_factors(self):
        # 12000 = 奋斗33年到头
        days = np.arange(1, 12000)
        # 通过平方得到一个初始加速然后平滑的曲线，符合边际效用原则
        living_days = np.sqrt(days)
        # 将数字从[0,1]区间放大到[-1,1]区间，对健康从抵抗衰老到无法抗拒岁月
        self.health_factor = regular_mm(living_days)*2 - 1
        # 喜悦缓慢下降，然而也不会是负值
        self.happiness_factor = regular_mm(days)[::-1]

class StockDay(BaseLifeway):
    def _init_self(self, *args, **kwargs):
        self.health_base = 1.5
        self.happiness_base = 0.5
        self.wealth_base = 10
        self._gen_factors()
    
    def _gen_factors(self, *args, **kwargs):
        days = np.arange(10000)
        living_days = np.sqrt(days)
        self.health_factor = regular_mm(living_days)
        self.wealth_factor = regular_mm(living_days)
        self.happiness_factor = np.power(regular_mm(days), 4)[::-1]

class FameDay(BaseLifeway):
    def _init_self(self, *args, **kwargs):
        # 名望的压力
        self.health_base = 3
        self.happiness_base = 0.6
        self.fame_base = 10
        self._gen_factors()

    def _gen_factors(self, *args, **kwargs):
        days = np.arange(12000)
        living_cost = np.sqrt(days)
        self.health_factor = regular_mm(living_cost)
        self.fame_factor = regular_mm(living_cost)
        self.happiness_factor = np.power(regular_mm(days), 2)[::-1]
        
def simple_life():
    me = Person()
    oneday = FameDay()
    # oneday = HealthDay()
    # oneday = StockDay()
    while me.lifetime > 0:
        me.live_one_day(oneday)
    return me

def complex_life(weights):
    life_choice = [HealthDay(), StockDay(), FameDay()]
    life_plan = np.random.choice([0,1,2], 80000, p=weights)

    me = Person()
    while me.lifetime > 0:
        today_plan = life_plan[me.living_days]
        me.live_one_day(life_choice[today_plan])
    return me

def brute_find_best():
    lives = []
    for _ in range(1000):
        weights = np.random.random(3)
        weights = weights/sum(weights)
        someone = complex_life(weights)
        lives.append((someone, weights))
    best_life = sorted(lives, key=lambda x: x[0].happiness)[-1]
    print('archivement:{}, strategy:{}'.format(best_life[0], best_life[1]))
    return best_life
    
def optimize_best(weights):
    if sum(weights) != 1:
        return 0
    return -complex_life(weights).happiness

if __name__ == '__main__':
    best_ops = sco.brute(optimize_best, ((0, 1.1, 0.1), (0, 1.1, 0.1), (0, 1.1, 0.1)))
    print(best_ops)
    x = complex_life([0.4, 0.3, 0.3])
    print(x)