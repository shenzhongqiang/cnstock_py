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
start = '2010-01-01'
end = '2017-09-30'
df_a = store.get('id000001').loc[start:end]
df_b = store.get('id000016').loc[start:end]
print np.corrcoef([df_a.close, df_b.close])
clf = linear_model.LinearRegression()
X = df_a.close.values.reshape(-1,1)
y = df_b.close.values
clf.fit(X, y)
y_pred = clf.predict(X)
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(range(len(y)), y-y_pred, color='k')
#ax2 = ax1.twinx()
#ax1.plot(df_b.close, c='r')
#ax2.plot(df_a.close, c='k')
plt.show()
