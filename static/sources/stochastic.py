import pandas as pd
import ta
from backtesting import Strategy
from backtesting.lib import crossover

class Stochastic(Strategy): 
  def init(self):
    self.index = 0;
    close = self.data.Close 
    self.SMA_200 = self.I(ta.trend.sma_indicator, pd.Series(close), 200)
    self.stoch_k = self.I(ta.momentum.stochrsi_k, pd.Series(close), 10)

    self.Buy = (close > self.SMA_200) & (self.stoch_k < 0.05)
    self.buydates, self.selldates = [], []
    self.buys, self.sells = [], []
    self.last_selldate = pd.to_datetime('1900-01-01')

  def next(self):
    if len(self.selldates) > 0:
      self.last_selldate = self.selldates[-1]

    if self.Buy:
      buyprice = self.data.Close * 0.97
      k = 1
      while True:
        if self.Buy:
          buyprice >= self.data.df.iloc[self.index+k].Low
          buydate = self.data.df.iloc[self.index+k].name
          break
        elif k > 10:
          break
        else: 
          k+=1
      
      if buydate > self.last_selldate: 
        self.buydates.append(buydate)
        self.buys.append(buyprice)
        self.buy()

        print(len(self.buys))
        for j in range(1,11):
          if self.data.df.iloc[self.index+k+j].Close > buyprice:
            sellprice = self.data.df.iloc[self.index+k+j+1].Open
            selldate =  self.data.df.iloc[self.index+k+j+1].name
            self.sell()
            self.selldates.append(selldate)
            break
          elif j == 10:
            sellprice = self.data.df.iloc[self.index+k+j+1].Open
            selldate =  self.data.df.iloc[self.index+k+j+1].name
            self.sell()
            self.selldates.append(selldate)
    self.index += 1;         