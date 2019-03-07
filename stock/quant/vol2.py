import sys
import os
import scipy
import scipy.stats
import re
import numpy as np
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, exsymbol_to_symbol
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type
from stock.lib.candlestick import plot_price_volume_inday
from stock.lib.finance import load_stock_basics, get_lrb_data

def get_slope(array):
    y = np.copy(array) / array[0]
    x = range(len(y))
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

def compute_vol_tvalue(array, past_len, recent_len):
    past = array[0:past_len]
    recent = array[past_len:past_len+recent_len]
    [tvalue, pvalue] = scipy.stats.ttest_ind(past, recent)
    return tvalue

def compute_vol_pvalue(array, past_len, recent_len):
    past = array[0:past_len]
    recent = array[past_len:past_len+recent_len]
    [tvalue, pvalue] = scipy.stats.ttest_ind(past, recent)
    return pvalue

def value_down(array):
    for i in range(len(array)-1):
        if array[i+1] > array[i]:
            return False
    return True

if len(sys.argv) < 2:
    print("Usage: %s <date>" % (sys.argv[0]))
    sys.exit(1)

date = sys.argv[1]
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_basics = load_stock_basics()

for exsymbol in exsymbols:
    df = store.get(exsymbol)[:date]
    if date not in df.index:
        continue
    if len(df) < 400:
        continue
    if re.match(r"sz3", exsymbol):
        continue
    df["mean_vol"] = df.volume.shift(3).rolling(window=20).mean()
    bar = df.loc[date]
    upper = max(bar.open, bar.close)
    ratio = (bar.high - upper) / upper
    if ratio < 0.05:
        continue
    date_id = df.index.get_loc(date)
    price = df.loc[date].close
    total_shares = df_basics.loc[exsymbol, "totals"]
    mcap = total_shares * price
    df_lrb = get_lrb_data(exsymbol)
    if df_lrb.ix[-1].jlr < 0:
        continue
    if mcap < 200:
        continue
    if df.ix[date_id].volume > df.ix[date_id-3].mean_vol*3 and \
        df.ix[date_id-1].volume > df.ix[date_id-3].mean_vol*3 and \
        df.ix[date_id-2].volume > df.ix[date_id-3].mean_vol*3 and \
        bar.close > bar.open:
        print(exsymbol)
