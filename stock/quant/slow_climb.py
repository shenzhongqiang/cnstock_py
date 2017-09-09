import datetime
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
from stock.lib.candlestick import plot_compare_graph
from config import store_type

def get_slope(y):
    reg = linear_model.LinearRegression()
    x = np.arange(len(y))
    X = x.reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')["2017-01-03":]
date = "2017-01-03"
columns = ["exsymbol", "low_slope", "vol_slope"]
result = pd.DataFrame(columns=columns)
index_history = store.get('id000001').loc[date:]
dates = index_history.index

idx = dates.get_loc(date)
dt = dates[idx]
df_date = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df.loc[:date]) < 100:
        continue
    if not dt in df.index:
        continue
    df["low_slope"] = df.low.rolling(window=22).apply(get_slope)
    df["vol_slope"] = df.volume.rolling(window=22).apply(get_slope)
    today_bar = df.loc[dt]
    df_date.loc[len(df_date)] = [exsymbol, today_bar.low_slope, today_bar.vol_slope]
print df_date[df_date.low_slope > 0][df_date.vol_slope > 0]
