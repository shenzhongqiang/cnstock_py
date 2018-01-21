import os
import cPickle as pickle
import scipy
import scipy.stats
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
from stock.lib.finance import load_stock_basics
from config import store_type

def get_slope(x, y):
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
start_date = "2006-07-31"
df_wk = store.get('sz000002').loc[start_date:]
df_bl = store.get('sh600048').loc[start_date:]
df_sz = store.get('id399001').loc[start_date:]
df_sh = store.get('id000001').loc[start_date:]
df_stock = df_wk.join(df_bl, how="outer", lsuffix='_wk', rsuffix='_bl')
df_index = df_sz.join(df_sh, how="outer", lsuffix='_sz', rsuffix='_sh')
result = df_index.join(df_stock, how="outer")
print result
df = result.fillna(method="ffill")
df["chg_wk"] = df.close_wk.pct_change()
df["chg_bl"] = df.close_bl.pct_change()
df["chg_sz"] = df.close_sz.pct_change()
df["chg_sh"] = df.close_sh.pct_change()
df["up_diff"] = df.close_wk / df.close_wk.shift(1) - df.close_bl / df.close_bl.shift(1)
df["pl_wk"] = df.close_wk.shift(-1) / df.close_wk - 1
df["pl_bl"] = df.close_bl.shift(-1) / df.close_bl - 1
print np.corrcoef(df.close_wk, df.close_bl)
print np.corrcoef(df[1:].chg_wk, df[1:].chg_bl)
print np.median(df.close_wk / df.close_bl)
print np.median(df[1:].chg_wk - df[1:].chg_bl)
df_len = len(df)
print np.corrcoef(df.up_diff[1:df_len-1], df.pl_bl[1:df_len-1])


# plot stock price
fig = plt.figure()
# price of wk and bl
ax1 = fig.add_subplot(411)
ax2 = ax1.twinx()
ax1.plot(df.index, df.close_wk, c='b')
ax2.plot(df.index, df.close_bl, c='r')
ax1.set_xlabel('date')
ax1.set_ylabel("wk")
ax2.set_ylabel("bl")
# ratio of wk against bl
ax3 = fig.add_subplot(412)
ax3.plot(df.index, df.close_wk / df.close_bl)
# diff of wk to bl
ax4 = fig.add_subplot(413)
ax4.plot(df.index, df.chg_wk - df.chg_bl)
# relationship
X = np.linspace(-0.10, 0.10, 1000)
y = []
for x in X:
    pl_series = df[df.up_diff < x][df.chg_wk > df.chg_sz].pl_wk
    yp = (pl_series+1).prod()
    y.append(yp)
ax5 = fig.add_subplot(414)
ax5.plot(X, y)

fig.autofmt_xdate()
plt.show()
