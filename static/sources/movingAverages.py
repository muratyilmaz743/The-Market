import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover

class MovingAverages(Strategy):
  n1 = 20
  n2 = 50

  def init(self): 
    close = self.data.Close

    closeDataframe = pd.Series(self.data.Close)

    self.ma20 = closeDataframe.rolling(self.n1).mean()
    self.ma50 = closeDataframe.rolling(self.n2).mean()

  def next(self):
    if crossover(self.ma20, self.ma50):
      self.buy()
    elif crossover(self.ma50, self.ma20):
      self.sell()