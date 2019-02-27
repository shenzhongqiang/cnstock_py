import sys
import os
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


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
df = store.get('sh600516')
df["range"] = df.high / df.low - 1
df["vol_tvalue"] = df.volume.rolling(window=44).apply(compute_vol_tvalue, (22, 22))
df["vol_pvalue"] = df.volume.rolling(window=44).apply(compute_vol_pvalue, (22, 22))
df["min_price"] = df.close.rolling(window=44).min()
df["already_up"] = df.close / df.min_price - 1
df["price_slope"] = df.close.rolling(window=22).apply(get_slope)
df["tvalue_down"] = df.vol_tvalue.rolling(window=5).apply(value_down)
df_test = df.loc["2017-01-01":]
df_test["vol_chg"] = df_test.volume.pct_change()
print(df_test[df_test.vol_pvalue < 0.01][df_test.tvalue_down == True][df_test.price_slope>0].sort_values(["already_up"], ascending=False))
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twinx()
ax1.bar(df_test.index, df_test.volume, color='grey', alpha=0.8)
ax2.plot(df_test.index, df_test.vol_tvalue, c='r')
ax2.axhline(-3, c='r')
plt.show()
