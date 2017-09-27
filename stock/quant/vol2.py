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
    print "Usage: %s <date>" % (sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
for exsymbol in exsymbols:
    df = store.get(exsymbol)[:date]
    if date not in df.index:
        continue
    df["mean_vol"] = df.volume.shift(1).rolling(window=40).mean()
    bar = df.loc[date]
    if bar.volume > bar.mean_vol * 10 and bar.close > bar.open:
        print exsymbol
