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
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type

pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
start = '2015-01-01'
df_a = store.get('id000001').loc[start:]
df_a["chg"] = df_a.close.pct_change()
df_b = store.get('id000016').loc[start:]
df_b["chg"] = df_b.close.pct_change()
result = df_a.close / df_b.close
mean = np.mean(result)
std = np.std(result)

result_std = (result-mean) / std
df_a_std = (df_a.close - np.mean(df_a.close)) / np.std(df_a.close)
plt.plot(range(len(result_std)), result_std, c='r')
plt.plot(range(len(df_a_std)), df_a_std, c='g')
print np.corrcoef(result_std, df_a_std)
plt.show()
