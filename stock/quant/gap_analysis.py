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
from sklearn.svm import SVR
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
from config import store_type

def plot_corr(df):
    x = []
    y = []
    for thrd in np.arange(-0.01, 0.01, 0.00001):
        df_test = df[df.open_gap > thrd]
        corr_matrix = df_test.corr()
        corr = corr_matrix["max_profit"]["volume_yest"]
        x.append(thrd)
        y.append(corr)
    print df["min_profit"].quantile(0.15)
    #plt.plot(x, y)
    #plt.show()

def test_model(df, thrd=0.004):
    df = df.dropna(how="any")
    df_test = df[df.open_gap > thrd]
    X_orig = df_test[["volume_yest", "open_gap"]].copy()
    y = df_test["max_profit"].copy()
    std_tr = StandardScaler()
    X = std_tr.fit_transform(X_orig)
    clf = linear_model.LinearRegression()
    clf.fit(X, y)
    y_pred = clf.predict(X)
    #for a, b in zip(y, y_pred):
    #    print "orig: %f, pred: %f" % (a, b)
    scores = cross_val_score(clf, X, y, scoring="neg_mean_squared_error", cv=5)
    print thrd, np.sqrt(-scores)

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_stock = store.get('sh601398')
dates_len = len(df_stock.date)
start_date = df_stock.index[0]
columns = ['date']
df = pd.DataFrame(columns=columns)
index_history = store.get('id000001')
index_history['chg'] = index_history.close.pct_change()
df_stock["open_gap"] = df_stock.open / df_stock.close.shift(1) - 1
df_stock["chg"] = df_stock.close.pct_change()
df_stock["volume_yest"] = df_stock.volume.shift(1)# + df_stock.volume.shift(2) + df_stock.volume.shift(3)
max_profits = []
for i in xrange(len(df_stock) - 5):
    s = pd.Series(df_stock.iloc[i+1:i+6].high.max(), index=[df_stock.index[i]])
    max_profits.append(s)
df_stock["max_profit"] = pd.concat(max_profits) / df_stock.close - 1

min_profits = []
for i in xrange(len(df_stock) - 5):
    s = pd.Series(df_stock.iloc[i+1:i+6].low.min(), index=[df_stock.index[i]])
    min_profits.append(s)
df_stock["min_profit"] = pd.concat(min_profits) / df_stock.close - 1
plot_corr(df_stock)

