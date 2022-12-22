import yfinance as yf
import ta
import numpy as np
import pandas as pd
import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from ta.volatility import BollingerBands

backtesting.set_bokeh_output(notebook=False)

class MeanReversion(Strategy):
  timePeriod = 14

  def init(self): 
    closes = self.data.Close


    bol = ta.volatility.BollingerBands(pd.Series(closes), window = 14)

    rsiIndicator = ta.momentum.RSIIndicator(pd.Series(closes), window = 14, fillna = True)
    
    self.rsi = rsiIndicator.rsi()
    self.upperBollinger = bol.bollinger_hband()
    self.lowerBollinger = bol.bollinger_lband()

  def next(self):
    if crossover(self.rsi, 30) & crossover(self.data.Close, self.lowerBollinger):
      self.buy()
    elif crossover(self.rsi, 70) & crossover(self.data.Close, self.upperBollinger):
      self.sell()
