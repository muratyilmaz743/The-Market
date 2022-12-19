from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

units = [{}];

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/getGraph', methods=['POST'])
def getGraph():
    unit = request.args.get('unit')
    return unit



if __name__ == '__main__':
	app.run(debug=True)