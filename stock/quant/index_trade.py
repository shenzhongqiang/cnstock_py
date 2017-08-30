import os
import cPickle as pickle
import scipy
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

def get_slope(array):
    y = np.copy(array) / array[0]
    x = range(len(y))
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
start = '2007-01-01'
df = store.get('id000001').loc[start:]
df["chg"] = df.low.pct_change()
df["extra"] = (df.close - df.high.shift(1)) / df.high.shift(1)
df["body"] = (df.close -df.open) /df.close
df["prev_body"] = df.body.shift(1)
df["ma"] = df.close.rolling(window=20).mean()
df["bias"] = (df.close - df.ma)/df.ma
df["max_profit"] = df["close"].rolling(window=10).apply(np.max).shift(-10) / df["close"] - 1
df["min_profit"] = df["close"].rolling(window=10).apply(np.min).shift(-10) / df["close"] - 1

df = df.iloc[20:]
std = StandardScaler()
plt.plot(df.index, std.fit_transform(df.bias), c='b')
plt.plot(df.index, std.fit_transform(df.close), c='r')
plt.show()
