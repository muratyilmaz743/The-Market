from flask import Flask, render_template, request, make_response, jsonify

import yfinance as yf
import json
import backtesting
from backtesting import Backtest
import static.sources.sma_with_backtesting as sma
import static.sources.mean_reversion as mr
import static.sources.stochastic as st
import static.sources.movingAverages as ma

backtesting.set_bokeh_output(notebook=False)


df = yf.download('BTC-USD', start='2018-01-01', end = '2021-01-01')

com = 0.002
cash = 1000000

smaReturn = Backtest(df, sma.SMAcross, cash=cash, commission = com, exclusive_orders = True).run()[6]
mrReturn = Backtest(df, mr.MeanReversion, cash=cash, commission = com, exclusive_orders = True).run()[6]
stochasticReturn = Backtest(df, st.Stochastic, cash=cash, commission = com, exclusive_orders = True).run()[6]
maReturn = Backtest(df, ma.MovingAverages, cash=cash, commission = com, exclusive_orders = True).run()[6]


app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html")

@app.route('/getGraph', methods=['POST'])
def getGraph():
    unit = request.args.get('unit')
    bt = Backtest(df, ma.MovingAverages, cash=cash, commission = com, exclusive_orders = True)
    bt.run()
    bt.plot(open_browser=False,filename="static/myGraph.html");
    return jsonify({"status":"OK",'result':str(unit)})



if __name__ == '__main__':
	app.run(debug=True)