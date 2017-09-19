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
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
import matplotlib.pyplot as plt
from stock.lib.candlestick import plot_compare_graph
from config import store_type
import tushare as ts

if len(sys.argv) == 1:
    print "Usage: %s <date>" % (sys.argv[0])
    sys.exit(1)

date = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
store = get_store(store_type)
df_index = store.get('id000001')

for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    df_bar = df.loc[date]
    lower = min(df_bar.open, df_bar.close)
    ratio = (lower - df_bar.low) / lower
    if ratio > 0.05:
        print exsymbol

