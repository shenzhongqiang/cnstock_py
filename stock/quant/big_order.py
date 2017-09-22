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
from stock.lib.tick_analysis import get_pulse_in_range
from config import store_type
import tushare as ts

if len(sys.argv) < 2:
    print "Usage: %s <symbol> <start> [<end>]" % (sys.argv[0])
    sys.exit(1)

symbol = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]
store = get_store(store_type)
exsymbol = symbol_to_exsymbol(symbol)
df = store.get(exsymbol)
pd.set_option('display.max_rows', None)
result = pd.DataFrame(columns=["big_order_vol", "big_order_num"])

for date in df.loc[start:end].index:
    day_bar = df.loc[date]
    #if day_bar.close > day_bar.open:
    #    continue
    date_str = date.strftime("%Y-%m-%d")
    df_dd = ts.get_tick_data(symbol, date=date_str)
    times = pd.to_datetime(df_dd.time, format="%H:%M:%S")
    df_dd.set_index(times, inplace=True)
    df_dd = df_dd.iloc[::-1]

    big_order_num = (df_dd.volume > 4000).sum()
    big_order_vol = df_dd[df_dd.volume > 4000].volume.sum()
    print date, big_order_vol, big_order_num
    result.loc[date] = [big_order_vol, big_order_num]
    time.sleep(2)

print result
plt.plot(result.index, result.big_order_vol, c='b')
plt.plot(result.index, result.big_order_num, c='g')
plt.show()
