import os
import cPickle as pickle
import scipy
import scipy.stats
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
from stock.lib.finance import load_stock_basics
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
columns = ['exsymbol', 'slope', 'mcap', 'up_ratio', 'vol_tvalue', 'low_tvalue', 'score']
result = pd.DataFrame(columns=columns)
index_history = store.get('id000001')
start_date = "2017-11-13"
end_date = "2017-12-06"
dates_len = len(index_history.loc[start_date:end_date])
df_index = index_history.loc[start_date:end_date]
index_lows = df_index.low / df_index.loc[start_date].low
df_basics = load_stock_basics()

for exsymbol in exsymbols:
    if not re.match('sh', exsymbol):
            continue
    df = store.get(exsymbol)
    if len(df) < 100:
        continue
    df_test = df.loc[start_date:end_date]
    if end_date not in df.index:
        continue
    if len(df_test) < dates_len:
        continue
    price = df.loc[end_date].close
    total_shares = df_basics.loc[exsymbol, "totals"]
    mcap = total_shares * price
    X = range(len(df_test))
    lows = df_test.low / df_test.loc[start_date].low
    slope = get_slope(X, lows)
    start_idx = df.index.get_loc(start_date)
    idx = df.index.get_loc(end_date)
    recent_low = df.iloc[idx-90:idx].close.min()
    up_ratio = df.loc[end_date].close / recent_low - 1
    past_vol = df.iloc[start_idx-30:start_idx].volume
    rece_vol = df.iloc[start_idx:idx].volume
    [vol_tvalue, vol_pvalue] = scipy.stats.ttest_ind(past_vol, rece_vol)
    [low_tvalue, low_pvalue] = scipy.stats.ttest_ind(index_lows, lows)
    score = -vol_tvalue / mcap / up_ratio
    result.loc[len(result)] = [exsymbol, slope, mcap, up_ratio, vol_tvalue, low_tvalue, score]

pd.set_option('display.max_rows', None)
low_thrd = result.slope.quantile(0.1)
high_thrd = result.slope.quantile(0.9)
print result[result.mcap > 200][result.low_tvalue < -3][result.vol_tvalue < 0].sort_values(["up_ratio"])
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
