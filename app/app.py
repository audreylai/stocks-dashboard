from flask import Flask, redirect, render_template, request, url_for
from db import *
app = Flask(__name__)

@app.route("/")
def index():
  return render_template("dashboard1.html")

@app.route("/", methods=["POST"])
def set_ticker():
  print("/ticker", request.form["ticker"])
  ticker = request.form["ticker"]
  data = get_ticker(ticker)
  patterns_table = get_patterns(data["df"])
  profit_total = sum(d['profit'] for d in patterns_table)
  print(profit_total)
  return render_template("dashboard1.html", ticker=ticker, data=data["data_dict"], patterns_table=patterns_table, profit_total=profit_total)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port="5000", debug=True)