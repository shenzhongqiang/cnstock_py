import os
import cPickle as pickle
import scipy
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
import matplotlib.pyplot as plt
from config import store_type

def get_slope(x, y):
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
columns = ['exsymbol', 'slope', "slope_close", "pl", "low_std", "high_std", "close_std"]
result = pd.DataFrame(columns=columns)
index_history = store.get('id000001')
dates_len = len(index_history.loc["2017-04-07":"2017-05-11"])

for exsymbol in exsymbols:
    if not re.match('sh', exsymbol):
            continue
    df = store.get(exsymbol)
    if len(df) < 100:
        continue
    df_test = df.loc["2017-04-07":"2017-05-11"]
    if "2017-04-07" not in df_test.index:
        continue
    if len(df_test) < dates_len:
        continue
    X = range(len(df_test))
    lows = df_test.low / df_test.loc["2017-04-07"].low
    highs = df_test.high / df_test.loc["2017-04-07"].high
    closes = df_test.close / df_test.loc["2017-04-07"].close
    slope = get_slope(X, lows)
    slope_close = get_slope(X, closes)
    pl = df.iloc[len(df)-1].close / df.loc["2017-05-11"].close
    low_std = np.std(lows)
    high_std = np.std(highs)
    close_std = np.std(closes)
    result.loc[len(result)] = [exsymbol, slope, slope_close, pl, low_std, high_std, close_std]
    print close_std

pd.set_option('display.max_rows', None)
low_thrd = result.slope.quantile(0.1)
high_thrd = result.slope.quantile(0.9)
df_low = result[result.slope <= low_thrd]
low_stocks = df_low.exsymbol
df_high = result[result.slope >= high_thrd]
high_stocks = df_high.exsymbol
print result[result.pl >= result.pl.quantile(0.95)].sort_values(['pl'], ascending=False)
import sys
sys.exit(1)
trading_dates = index_history.loc["2017-05-11":].index
x = range(len(trading_dates))
y_low = []
y_high = []
for date in trading_dates:
    low_closes = []
    high_closes = []
    for exsymbol in low_stocks:
        df_stock = store.get(exsymbol)
        if date not in df_stock.index:
            continue
        ratio = df_stock.loc[date].close / df_stock.loc["2017-05-11"].close
        low_closes.append(ratio)
    for exsymbol in high_stocks:
        df_stock = store.get(exsymbol)
        if date not in df_stock.index:
            continue
        ratio = df_stock.loc[date].close / df_stock.loc["2017-05-11"].close
        high_closes.append(ratio)
    y_low.append(np.mean(low_closes))
    y_high.append(np.mean(high_closes))

plt.plot(x, y_low, color='g')
plt.plot(x, y_high, color='r')
plt.show()
