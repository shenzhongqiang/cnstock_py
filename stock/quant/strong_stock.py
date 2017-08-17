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
columns = ['exsymbol', 'date', 'minus_index', 'today_up', 'next_day_up', 'next_week_high', 'open_gap', 'next_open_gap', 'body', 'upper_shadow', 'index_slope', 'stock_slope', 'vol_increase', 'price', 'trade_vol', 'chg_std']
df = pd.DataFrame(columns=columns)
index_history = store.get('id000001')
index_history['chg'] = index_history.close.pct_change()
for date in index_history.loc[:'2017-08-14'].index:
    print date
    if len(index_history[:date].index) < 250:
        continue

    index_bar = index_history.ix[date]
    index_idx = index_history.index.get_loc(date)
    index_closes = index_history.iloc[index_idx-10:index_idx].close/index_history.iloc[index_idx-10].close
    index_X = range(10)
    index_slope = get_slope(index_X, index_closes)
    if index_bar.chg >= 0:
        continue
    for exsymbol in exsymbols:
        if not re.match('sh', exsymbol):
                continue
        all_history = store.get(exsymbol)
        if len(all_history[:date].index) < 250:
            continue
        if date not in all_history.index:
            continue
        all_history['chg'] = all_history.close.pct_change()
        today_bar = all_history.ix[date]
        if today_bar.chg <= 0:
            continue
        minus_index = today_bar.chg - index_bar.chg
        today_up = today_bar.chg
        idx = all_history.index.get_loc(date)
        if today_up > 0.090:
            continue
        if len(all_history.index) < idx + 10:
            continue
        last_bar = all_history.iloc[idx-1]
        next_bar = all_history.iloc[idx+1]
        next_day_up = next_bar.close / today_bar.close - 1
        next_week_high = all_history.high.iloc[idx+1:idx+6].max()
        next_week_high = next_week_high / today_bar.close - 1
        open_gap = today_bar.open / last_bar.close - 1
        next_open_gap = next_bar.open / today_bar.close - 1
        body = (today_bar.close - today_bar.open) / last_bar.close
        upper_body = max(today_bar.open, today_bar.close)
        upper_shadow = (today_bar.high - upper_body) / last_bar.close
        trade_vol = today_bar.close * today_bar.volume
        price = today_bar.close
        #if minus_index > 0.05:
        #    continue
        #if today_up > 0.03 and upper_shadow > 0.02:
        #    continue
        stock_closes = all_history.iloc[idx-10:idx].close / all_history.iloc[idx-10].close
        chg_std = np.std(all_history.chg.iloc[idx-10:idx])
        stock_X = range(10)
        stock_slope = get_slope(stock_X, stock_closes)
        vols = all_history.iloc[idx-240:idx].volume
        vol_increase = scipy.stats.percentileofscore(vols, today_bar.volume)
        df.loc[len(df)] = [exsymbol, date, minus_index, today_up, next_day_up, next_week_high, open_gap, next_open_gap, body, upper_shadow, index_slope, stock_slope, vol_increase, price, trade_vol, chg_std]

folder = os.path.dirname(__file__)
outfile = os.path.join(folder, "output")
with open(outfile, "wb") as f:
    pickle.dump(df, f)
#plot_today_up_mean(df)
#plot_upper_shadow_mean(df)
#plot_scatter_matrix(df)
#plt.show()
