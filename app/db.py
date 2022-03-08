import numpy as np
import talib
import yfinance as yf
import pandas as pd
import datetime
from itertools import compress

def get_ticker(ticker_str):
	if not ticker_str:
		return None
	df = yf.download(ticker_str, period="6mo")
	if df.empty:
		return None

	df.reset_index(inplace=True)
	df["MA10"] = talib.SMA(df.Close, 10)
	df["MA20"] = talib.SMA(df.Close, 20)
	df["MA50"] = talib.SMA(df.Close, 50)
	df["MA150"] = talib.SMA(df.Close, 150)
	df["up"] = df.Close >= df.Open

	data_dict = {
		"dates": list(df.Date),
		"data": {k: df.to_dict("list")[k] for k in set(list(df.to_dict("list").keys())) - set(['Date', 'Adj Close'])},
		"data_records": df.to_dict("records"),
	}
	return {"data_dict": data_dict, "df":df}

def get_patterns(df):
	candle_names = [
		"CDLHAMMER", "CDLINVERTEDHAMMER", "CDLENGULFING", "CDLPIERCING",
		"CDLMORNINGSTAR", "CDL3WHITESOLDIERS", "CDLHANGINGMAN",
		"CDLSHOOTINGSTAR", "CDLEVENINGSTAR", "CDL3BLACKCROWS",
		"CDLDARKCLOUDCOVER"
	]

	candle_names = talib.get_function_groups()['Pattern Recognition']

	for candle in candle_names:
		# below is same as;
		df[candle] = getattr(talib, candle)(df['Open'], df['High'], df['Low'], df['Close'])

	df['candlestick_pattern'] = np.nan
	df['candlestick_match_count'] = np.nan
	df['trend'] = np.nan

	for index, row in df.iterrows():
		# no pattern found
		if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
			df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
			df.loc[index, 'candlestick_match_count'] = 0
			df.loc[index, "trend"] = None

		# single pattern found
		elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
			if any(row[candle_names].values > 0): # bull pattern
				pattern = list(compress(
					row[candle_names].keys(),
					row[candle_names].values != 0
				))[0]
				df.loc[index, "trend"] = "bear"
			else: # bear pattern
				pattern = list(compress(
					row[candle_names].keys(),
					row[candle_names].values != 0
				))[0]
				df.loc[index, "trend"] = "bull"
			df.loc[index, 'candlestick_pattern'] = pattern
			df.loc[index, 'candlestick_match_count'] = 1
		# multiple patterns found
		else:
			patterns = list(compress(
				row[candle_names].keys(),
				row[candle_names].values != 0
			))
			container = []
			for pattern in patterns:
				if row[pattern] > 0:
					container.append([pattern, "bull"])
				else:
					container.append([pattern, "bear"])
			if len(container):
				df.loc[index, 'candlestick_pattern'] = container[0][0]
				df.loc[index, 'trend'] = container[0][1]
				df.loc[index, 'candlestick_match_count'] = len(container)
	df.drop(candle_names, axis=1, inplace=True)

	patterns = df[df["candlestick_pattern"] != "NO_PATTERN"].copy()
	patterns['consecutive'] = 0
	table = []
	patterns.reset_index(drop=True, inplace=True)
	consecutive = 0
	for index, row in patterns.iterrows():
		if index == 0 and row['trend'] == "bull":
			continue
		if index > 0 and row['trend'] == patterns.loc[index-1, 'trend']:
			if row['trend'] == "bear":
				consecutive += 1
			else:
				continue
		profit = 0
		if row['trend'] == "bull":
			last_buy = [d for d in table if d['trend'] == "bear" and d['consecutive_bear'] == 0][-1]
			profit = row["Close"] - last_buy["value"]
			consecutive = 0
		result = {"Date": row['Date'], "value": row["Close"], "candlestick_pattern": row['candlestick_pattern'], "trend": row['trend'],  "profit": profit, "consecutive_bear": consecutive}
		table.append(result)
	# table = patterns[(patterns[['trend']] .ne(patterns[['trend']] .shift())).any(axis=1)].copy()

	return table