import os.path
import cPickle as pickle
from stock.globalvar import *

def is_flat(quotes):
    sample = quotes[-1:-50:-1]
    if sample[0][5] < 1000000:
        return False

    highs = map(lambda x: x[3], sample)
    lows = map(lambda x: x[4], sample)
    closes = map(lambda x: x[2], sample)
    max_high10 = max(highs[0:10])
    min_low10 = min(lows[0:10])
    min_low = min(lows)
    #if closes[10] >= 1.1 * min_low and \
    if (max_high10 - min_low10) / closes[0] < 0.02:
        return True
    return False

filepath = os.path.join(SYMDIR, "us_ticker")
f = open(filepath)
content = f.read()
tickers = content.split("\n")
f.close()

us_dir = HIST_DIR['us']
result = []
for ticker in tickers:
    datafile = os.path.join(us_dir, ticker)
    if not os.path.isfile(datafile):
        continue

    output = open(datafile, "r")
    quotes = pickle.load(output)
    output.close()

    if len(quotes) < 50:
        continue

    if is_flat(quotes):
        result.append(ticker)

print len(result)
print result
