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
from stock.lib.candlestick import plot_compare_graph
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type

pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
start = '2015-01-01'
df_a = store.get('id000001').loc[start:]
df_a["norm"] = df_a.close / df_a.ix[0].close
df_b = store.get('id000016').loc[start:]
df_b["norm"] = df_b.close / df_b.ix[0].close
result = df_a.norm - df_b.norm

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = ax1.twinx()
ax1.plot(df_b.norm, c='r')
ax2.plot(df_a.norm, c='k')
plt.show()
