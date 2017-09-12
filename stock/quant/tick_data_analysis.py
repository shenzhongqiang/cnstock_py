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

date = sys.argv[1]
store = get_store(store_type)
symbol = "600507"
exsymbol = symbol_to_exsymbol(symbol)
df = store.get(exsymbol)
pd.set_option('display.max_rows', None)
for date in df.loc[date:].index:
    date_str = date.strftime("%Y-%m-%d")
    df_dd = ts.get_tick_data(symbol, date=date_str)
    times = pd.to_datetime(df_dd.time, format="%H:%M:%S")
    df_dd.set_index(times, inplace=True)
    df_dd = df_dd.iloc[::-1]
    df_dd["min_chg"] = df_dd.price / df_dd.price.shift(100) - 1
    avg_price = df_dd.amount.sum() / 100.0 / df_dd.volume.sum()
    dd_num = (df_dd.volume > 4000).sum()
    dd_ratio = df_dd[df_dd.volume > 4000].volume.sum() / float(df_dd.volume.sum())
    print date, df_dd.min_chg.max()
    print avg_price / df_dd.iloc[-1].price - 1
    time.sleep(2)
    plot_price_volume_inday(df_dd.index, df_dd.price, df_dd.volume)
    break
