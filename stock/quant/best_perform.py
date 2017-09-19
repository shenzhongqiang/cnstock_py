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
import tushare as ts

def get_slope(x, y):
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

store = get_store(store_type)
def get_equity_value(exsymbols, date):
    closes = []
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        if date in df.index:
            closes.append(df.loc[date].close)
        else:
            close = df.loc[:date].iloc[-1].close
            closes.append(close)
    return np.mean(closes)

exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
columns = ["exsymbol", "profit"]
result = pd.DataFrame(columns=columns)
date = "2016-01-03"
index_history = store.get('id000001').loc[date:]
stock_history = store.get('sh601016').loc[date:]
index_history["value"] = index_history.close / index_history.iloc[0].close
dates = index_history.index

df_date = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 400:
        continue
    df["profit"] = df.close / df.close.shift(70)
    profit = df.iloc[-300].profit
    df_date.loc[len(df_date)] = [exsymbol, profit]
df_date.dropna(how="any", inplace=True)
df_top = df_date.sort_values(["profit"]).tail(10)
print df_top
