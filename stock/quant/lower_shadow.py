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
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, exsymbol_to_symbol
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
import matplotlib.pyplot as plt
from stock.lib.candlestick import plot_compare_graph
from stock.lib.tick_analysis import get_pulse_info
from config import store_type
import tushare as ts

if len(sys.argv) == 1:
    print "Usage: %s <start>" % (sys.argv[0])
    sys.exit(1)

start = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')

for date in df_index.loc[start:].index:
    for exsymbol in exsymbols:
        symbol = exsymbol_to_symbol(exsymbol)
        df = store.get(exsymbol)
        df["past_low"] = df.close.rolling(window=3).min().shift(1)
        if len(df) < 200:
            continue
        if date not in df.index:
            continue
        df_bar = df.loc[date]
        close = df_bar.close
        upper = max(df_bar.open, df_bar.close)
        lower = min(df_bar.open, df_bar.close)
        ratio = (lower - df_bar.low) / close
        body = (df_bar.close - df_bar.open) / close
        if ratio > 0.05 and df_bar.past_low > df_bar.close:
            date_str = date.strftime("%Y-%m-%d")
            df_tick = ts.get_tick_data(symbol, date=date_str)
            [pulse, pulse_vol] = get_pulse_info(df_tick)
            print date, exsymbol, pulse, pulse_vol

