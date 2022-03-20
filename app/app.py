from flask import Flask, redirect, render_template, request, url_for
from db import *
import pandas as pd
app = Flask(__name__)

@app.route("/")
def index():
  return render_template("home.html")

@app.route("/", methods=["POST"])
def set_ticker():
  print("/ticker", request.form["ticker"], "PAGE:", request.form["page"])
  ticker = request.form["ticker"]
  data = get_ticker(ticker)
  patterns_table = get_patterns(data["df"])
  profit_total = sum(d['profit'] for d in patterns_table)
  return render_template("home.html", ticker=ticker, data=data["data_dict"], patterns_table=patterns_table, profit_total=profit_total, page=int(request.form["page"]))

@app.route("/stock-list")
def stock_list():
  stock_table = get_stock_info()
  last_update = stock_table['last_update'].strftime("%d/%m/%Y")
  return render_template("stock_list.html", stock_table=stock_table['table'], last_update=last_update)

@app.route("/stock-list", methods=["POST"])
def update_stock_list():
  update_stock_info()
  return redirect(url_for('stock_list'))



if __name__ == "__main__":
  app.run(host='0.0.0.0', port="5000", debug=True)