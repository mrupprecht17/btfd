from alpha_vantage.timeseries import TimeSeries
import argparse

def average(array):
	return sum(array) / len(array)

def ema(array, days):
	mult = 2 / (1 + days)
	prev = average(array[:days])
	i = days
	while i < len(array):
		prev = mult * (array[i] - prev) + prev
		i += 1
	return prev

def rsi(array, days):
	# initializes the gains and losses arrays
	gains = [0 for i in range(len(array) - 1)]
	losses = [0 for i in range(len(array) - 1)]
	i = 1
	while i < len(array):
		diff = array[i] - array[i - 1]
		if diff > 0:
			gains[i - 1] = diff
		else:
			losses[i - 1] = -diff
		i += 1

	avg_gains = average(gains[:days])
	avg_losses = average(losses[:days])

	# loops through and finds the averages up to the current day
	i = days
	while i < len(gains):
		avg_gains = (avg_gains * (days - 1) + gains[i]) / days
		avg_losses = (avg_losses * (days - 1) + losses[i]) / days
		i += 1

	# gives the current RSI
	try:
		rs = avg_gains / avg_losses
	except ZeroDivisionError: # avg_losses = 0, so rsi is 100 by definition
		rs = None
		rsi = 100
	if rs != None:
		rsi = 100 - (100 / (1 + rs))

	return rsi

def buy_signal(today, yesterday, rsi2, rsi5):
	return ((today > .96 * yesterday) and (rsi2 <= 15 and rsi5 <= 40))

def sell_signal(today, yesterday, ema8, rsi2, rsi5):
	return ((rsi2 >= 95 and rsi5 >= 85) or (today < ema8 and yesterday >= ema8))

if __name__ == '__main__':
	ts = TimeSeries(key="INSERT_KEY_HERE", output_format="pandas")

	EMA = 8
	RSI1 = 2
	RSI2 = 5

	ap = argparse.ArgumentParser()
	ap.add_argument("-t", "--ticker", required=True,
		help="the ticker to track")
	args = vars(ap.parse_args())

	ticker = args["ticker"]

	data = ts.get_daily(ticker)[0]["close"].as_matrix()
	yesterday = data[-2]
	today = data[-1]
	ema8 = ema(data, EMA)
	rsi2 = rsi(data, RSI1)
	rsi5 = rsi(data, RSI2)

	if buy_signal(today, yesterday, rsi2, rsi5):
		print("BUY")
	elif sell_signal(today, yesterday, ema8, rsi2, rsi5):
		print("SELL")
	else:
		print("MAINTAIN CURRENT POSITION")