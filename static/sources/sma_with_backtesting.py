import yfinance as yf
import ta
import pandas as pd
import backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
backtesting.set_bokeh_output(notebook=False)

class SMAcross(Strategy):
  n1 = 50
  n2 = 100

  def init(self): 
    close = self.data.Close
    self.sma1 = self.I(ta.trend.sma_indicator, pd.Series(close),self.n1)
    self.sma2 = self.I(ta.trend.sma_indicator, pd.Series(close),self.n2)

  def next(self):
    if crossover(self.sma1, self.sma2):
      self.buy()
    elif crossover(self.sma2, self.sma1):
      self.sell()
