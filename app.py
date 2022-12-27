from flask import Flask, render_template, request, make_response, jsonify
from flask_mail import Mail, Message

import yfinance as yf
import json
import backtesting
from backtesting import Backtest
import static.sources.sma_with_backtesting as sma
import static.sources.mean_reversion as mr
import static.sources.stochastic as st
import static.sources.movingAverages as ma
import numpy as np
from datetime import datetime, timedelta
backtesting.set_bokeh_output(notebook=False)

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cmmarketbot@gmail.com'
app.config['MAIL_PASSWORD'] = 'mrschhqdlxzhtvgg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/getGraph', methods=['POST'])
def getGraph():
    
    unit = request.args.get('unit')
    time = day_before_x_months(request.args.get('time'))
    df = getPairData(unit,time)
    myAlgorithm = findBest(df)
    com = 0.002
    cash = 1000000
    bt = Backtest(df, myAlgorithm, cash=cash, commission = com, exclusive_orders = True)
    bt.run()
    bt.plot(open_browser=False,filename="static/myGraph.html")

    msg = Message('Hello', sender = 'cmmarketbot@gmail.com', recipients = ['mrt.yilmaz743@gmail.com'])
    msg.body = "Bu mailde bizim işler olacak."
    mail.send(msg)
    
    return jsonify({"status":"OK",'result':str(unit)})


def getPairData(unit,time):
    pair = unit + '-USD'
    df = yf.download(pair, start=time, end = '2021-01-01')
    return df

def findBest(df):
    dictOfAlg={
        'SMAcross': 0,
        'MeanReversion': 0,
        'Stochastic': 0,
        'MovingAverages': 0,
    }
    com = 0.002
    cash = 1000000

    smaReturn = Backtest(df, sma.SMAcross, cash=cash, commission = com, exclusive_orders = True).run()[6]
    mrReturn = Backtest(df, mr.MeanReversion, cash=cash, commission = com, exclusive_orders = True).run()[6]
    stochasticReturn = Backtest(df, st.Stochastic, cash=cash, commission = com, exclusive_orders = True).run()[6]
    maReturn = Backtest(df, ma.MovingAverages, cash=cash, commission = com, exclusive_orders = True).run()[6]

    dictOfAlg['SMAcross'] = smaReturn
    dictOfAlg['MeanReversion'] = mrReturn
    dictOfAlg['Stochastic'] = stochasticReturn
    dictOfAlg['MovingAverages'] = maReturn
    
    return getBestAlg(dictOfAlg)

def getBestAlg(dict):

    sortedDictOfAlgorithms= sorted(dict.items(), key=lambda x:x[1])
    lastAlg = list(sortedDictOfAlgorithms)[-1]
    print(lastAlg[0])

    match lastAlg[0]:
        case 'SMAcross':
            strategy = sma.SMAcross
        case 'MeanReversion':
            strategy = mr.MeanReversion;
        case 'Stochastic':
            strategy = st.Stochastic
        case 'MovingAverages':
            strategy = ma.MovingAverages

    return strategy


def day_before_x_months(month):
  start_date = datetime(year=2021, month=1, day=1)
  print(start_date)
  num_months = int(month.split()[0])
  x_months_ago = start_date - timedelta(days=30*num_months)
  print(x_months_ago)
  return x_months_ago.strftime("%Y-%m-%d")

if __name__ == '__main__':
	app.run(debug=True)