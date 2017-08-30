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

def plot_today_up_mean(df):
    mean_up = df['next_day_up'].groupby(pd.cut(df['today_up'], np.arange(0,0.11,0.01))).mean()
    print mean_up
    X = map(lambda x: x.left, np.asarray(mean_up.index.values))
    y = mean_up.tolist()
    plt.scatter(X, y)

def plot_upper_shadow_mean(df):
    mean_up = df['next_day_up'].groupby(pd.cut(df['upper_shadow'], np.arange(0,0.11,0.01))).mean()
    print mean_up
    X = map(lambda x: x.left, np.asarray(mean_up.index.values))
    y = mean_up.tolist()
    plt.scatter(X, y)

def plot_scatter_matrix(df):
    attributes = ["minus_index", "today_up", "next_day_up", "next_week_high", "open_gap", "next_open_gap", "body", "upper_shadow", "index_slope", "stock_slope", "vol_increase", "price", "trade_vol", "chg_std"]
    scatter_matrix(df[attributes], alpha=0.2, figsize=(12, 8))

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
index_history = store.get('id000001')
index_history['chg'] = index_history.close.pct_change()
columns = ['date', 'exsymbol', 'chg']
result = pd.DataFrame(columns=columns)
for date in index_history.loc['2017-01-01':'2017-08-18'].index:
    if index_history.loc[date].chg > -0.01:
        continue

    df_date = pd.DataFrame(columns=columns)
    for exsymbol in exsymbols:
        if not re.match('sh', exsymbol):
                continue
        df = store.get(exsymbol)
        if len(df.loc[:date].index) < 100:
            continue
        if date not in df.index:
            continue
        df['chg'] = df.close.pct_change()
        chg = df.loc[date].chg
        df_date.loc[len(df_date)] = [date, exsymbol, chg]
    thrd = df_date.chg.quantile(0.95)
    result = pd.concat([result, df_date[df_date.chg >= thrd]])

pd.set_option('display.max_rows', None)
print result
