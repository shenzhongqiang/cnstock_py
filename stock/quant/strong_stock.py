import sys
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
from config import store_type

def get_slope(y):
    reg = linear_model.LinearRegression()
    x = range(len(y))
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

def get_max_drawdown(df, num):
    df_copy = df.iloc[len(df)-num:].copy()
    min_dates = []
    max_ranges = []
    for i in range(len(df_copy)-1):
        min_date = df_copy.iloc[i+1:].close.idxmin()
        min_idx = df_copy.index.get_loc(min_date)
        min_dates.append(min_date)
        diff = df_copy.iloc[i].close - df_copy.iloc[min_idx].close
        max_ranges.append(diff)
    start_date = df_copy.index[np.argmax(max_ranges)]
    end_date = min_dates[np.argmax(max_ranges)]
    max_range = np.max(max_ranges)
    if max_range < 0:
        return [None, None]
    return [start_date, end_date]

def get_up_ratio(df):
    num = 22 * 2
    df_test = df.iloc[-num:]
    min_date = df_test.close.idxmin()
    i = 1
    while min_date == df_test.index[0]:
        df_test = df.iloc[-num*(i+1):]
        min_date = df_test.close.idxmin()
        i = i + 1

    min_close = df.loc[min_date].close.min()
    return df.iloc[-1].close / min_close - 1

def get_tvalue(array_a, array_b):
    [tvalue, pvalue] = scipy.stats.ttest_ind(array_a, array_b)
    return tvalue

def get_strong_tvalue(df_index, df_stock):
    [start_date, end_date] = get_max_drawdown(df_index, 22)
    if start_date == None:
        return np.nan
    array_a = df_index.loc[start_date: end_date].close / df_index.loc[start_date].close
    array_b = df_stock.loc[start_date: end_date].close / df_stock.loc[start_date:].iloc[0].close
    tvalue = get_tvalue(array_a.values, array_b.values)
    return tvalue

def get_vol_tvalue(df):
    num = 22
    past = df.iloc[len(df)-num*2:len(df)-num].volume
    recent = df.iloc[len(df)-num:].volume
    tvalue = get_tvalue(past.values, recent.values)
    return tvalue

if len(sys.argv) < 2:
    print "Usage: %s <date>" % (sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001').loc[:date]
dates_len = len(df_index.date)
index_history = store.get('id000001')
index_history['chg'] = index_history.close.pct_change()
columns = ['exsymbol', 'slope', 'vol_tvalue', 'up_ratio', 'strong_tvalue', 'tick_pulse', 'market_profit_tvalue']
result = pd.DataFrame(columns=columns)

for exsymbol in exsymbols:
    if not re.match('sh', exsymbol):
            continue
    df_orig = store.get(exsymbol)
    df = df_orig.loc[:date]
    if len(df.loc[:date]) < 200:
        continue
    if date not in df.index:
        continue
    slope = get_slope(df.iloc[-22:].low) / df.iloc[0].low
    vol_tvalue = get_vol_tvalue(df)
    up_ratio = get_up_ratio(df)
    strong_tvalue = get_strong_tvalue(df_index, df)
    if slope > 0.0 and vol_tvalue < 0 and up_ratio > 0 and strong_tvalue < 0:
        print exsymbol, slope, vol_tvalue, up_ratio, strong_tvalue
        result.loc[len(result)] = [exsymbol, slope, vol_tvalue, up_ratio, strong_tvalue, 0, 0]

print result.sort_values(["vol_tvalue"], ascending=False)
