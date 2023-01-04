from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message

import yfinance as yf
import backtesting
from backtesting import Backtest
import static.sources.sma_with_backtesting as sma
import static.sources.mean_reversion as mr
import static.sources.stochastic as st
import static.sources.movingAverages as ma
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
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

app.secret_key = '1234'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'TheMarket'
 
mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            msg = 'Logged in successfully !'

            return redirect("/crypto", code=302)
        else:
            msg = 'Incorrect username / password !'
    return render_template('opening.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/crypto")
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
    outcome = bt.run()
    bt.plot(open_browser=False,filename="static/myGraph.html")

    msg = Message('Hello', sender = 'cmmarketbot@gmail.com', recipients = [session['email']])
    msg.body = "These are your probable outcomes: " + str(outcome)
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