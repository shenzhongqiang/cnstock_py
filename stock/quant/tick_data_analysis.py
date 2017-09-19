import time
import sys
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
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, symbol_to_exsymbol
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
import matplotlib.pyplot as plt
from stock.lib.candlestick import plot_price_volume_inday
from config import store_type
import tushare as ts

if len(sys.argv) == 1:
    print "Usage: %s <date>" % (sys.argv[0])
    sys.exit(1)

def get_pulse_info(df, idx):
    num = 100
    df_train = df.iloc[idx-num: idx]
    diffs = (df_train.price - df_train.shift(1).price).tolist()[1:]
    min_indice = []
    max_ranges = []
    for i in range(len(diffs)):
        if i == 0:
            max_ranges.append(diffs[i])
            min_indice.append(i)
            continue

        if max_ranges[-1]+diffs[i] > diffs[i]:
            max_ranges.append(max_ranges[-1]+diffs[i])
            min_indice.append(min_indice[-1])
        else:
            max_ranges.append(diffs[i])
            min_indice.append(i)

    idx = np.argmax(max_ranges)
    end_idx = idx + 1
    start_idx = min_indice[idx]
    pulse_range = df_train.iloc[end_idx].price - df_train.iloc[start_idx].price
    pulse_vol = df_train.iloc[start_idx:end_idx+1].volume.sum()
    return [pulse_range, pulse_vol]

date = sys.argv[1]
store = get_store(store_type)
symbol = "300109"
exsymbol = symbol_to_exsymbol(symbol)
df = store.get(exsymbol)
pd.set_option('display.max_rows', None)
for date in df.loc[date:].index:
    day_bar = df.loc[date]
    #if day_bar.close > day_bar.open:
    #    continue
    date_str = date.strftime("%Y-%m-%d")
    df_dd = ts.get_tick_data(symbol, date=date_str)
    times = pd.to_datetime(df_dd.time, format="%H:%M:%S")
    df_dd.set_index(times, inplace=True)
    df_dd = df_dd.iloc[::-1]
    df_dd["min_chg"] = df_dd.price / df_dd.price.shift(100) - 1
    hilo_range = day_bar.high = day_bar.low
    vol_sum = df_dd.volume.sum()
    for i in range(len(df_dd)):
        idx = df_dd.index[i]
        if i < 100:
            continue
        [pulse, pulse_vol] = get_pulse_info(df_dd, i)
        df_dd2 = df_dd.copy()
        df_dd2["price"] = df_dd2.price * -1.0
        [valey, valey_vol] = get_pulse_info(df_dd2, i)
        df_dd.loc[idx, "pulse"] = pulse / hilo_range
        df_dd.loc[idx, "pulse_vol"] = pulse_vol * 1.0 / vol_sum
        df_dd.loc[idx, "valey"] = valey / hilo_range
        df_dd.loc[idx, "valey_vol"] = valey_vol * 1.0 / vol_sum

    avg_price = df_dd.amount.sum() / 100.0 / df_dd.volume.sum()
    dd_num = (df_dd.volume > 4000).sum()
    dd_ratio = df_dd[df_dd.volume > 4000].volume.sum() / float(df_dd.volume.sum())
    #print date, df_dd.min_chg.max()
    #print avg_price / df_dd.iloc[-1].price - 1
    low_range = df_dd.price.quantile(0.1)
    high_range = df_dd.price.quantile(0.9)
    print date, df_dd[df_dd.price < low_range].volume.sum() * 1.0/df_dd.volume.sum(), df_dd[df_dd.price > high_range].volume.sum() * 1.0/df_dd.volume.sum()
    pulse_idx = df_dd.sort_values(["pulse", "pulse_vol"]).dropna().index[-1]
    pulse_row = df_dd.loc[pulse_idx]
    valey_idx = df_dd.sort_values(["valey", "valey_vol"]).dropna().index[-1]
    valey_row = df_dd.loc[valey_idx]
    print pulse_row.pulse, pulse_row.pulse_vol, valey_row.valey, valey_row.valey_vol
    #time.sleep(2)
    plot_price_volume_inday(df_dd.index, df_dd.price, df_dd.volume)
