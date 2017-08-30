import os
import cPickle as pickle
import scipy
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
from scipy.stats import pearsonr
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
from config import store_type

def get_slope(x, y):
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

def plot_corr(df, thrd=0.001):
    df_test = df[df.open_gap > thrd]
    corr_matrix = df_test.corr()
    corr = corr_matrix["max_profit"]
    print corr
    print df_test["min_profit"].quantile(0.25)
    #plt.plot(x, y)
    #plt.show()

def test_model(df, thrd=0.001):
    df = df.dropna(how="any")
    df_test = df[df.open_gap >= thrd]
    print len(df_test), len(df)
    X_orig = df_test[["volume_yest", "open_gap"]].copy()
    y = df_test["max_profit"].copy()
    X = X_orig
    clf = linear_model.LinearRegression()
    clf.fit(X, y)
    y_pred = clf.predict(X)
    df_test["pred_max_profit"] = y_pred
    #for a, b in zip(y, y_pred):
    #    print "orig: %f, pred: %f" % (a, b)
    y2 = df_test["min_profit"].copy()
    clf2 = linear_model.LinearRegression()
    clf2.fit(X, y2)
    y2_pred = clf2.predict(X)
    df_test["pred_min_profit"] = y2_pred
    scores = cross_val_score(clf, X, y, scoring="neg_mean_squared_error", cv=5)
    print thrd, np.sqrt(-scores)
    print pearsonr(df_test["min_profit"], y_pred)

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_stock = store.get('id000001')
df_stock = df_stock.loc["2007-07-01":"2017-07-01"]
df_stock["open_gap"] = df_stock.open / df_stock.close.shift(1) - 1
df_stock["close_up"] = df_stock.close / df_stock.open - 1
df_stock["chg"] = df_stock.close.pct_change()
df_stock["volume_yest"] = df_stock.volume.shift(1)# + df_stock.volume.shift(2) + df_stock.volume.shift(3)
max_profits = []
for i in xrange(len(df_stock) - 6):
    s = pd.Series(df_stock.iloc[i+1:i+6].high.max(), index=[df_stock.index[i]])
    max_profits.append(s)
df_stock["max_profit"] = pd.concat(max_profits) / df_stock.open - 1

min_profits = []
for i in xrange(len(df_stock) - 6):
    s = pd.Series(df_stock.iloc[i+1:i+6].low.min(), index=[df_stock.index[i]])
    min_profits.append(s)
df_stock["min_profit"] = pd.concat(min_profits) / df_stock.open - 1

slopes = []
for i in xrange(20, len(df_stock)):
    lows = df_stock.iloc[i-20:i].low / df_stock.iloc[i-20].low
    slope = get_slope(range(20), lows)
    s = pd.Series(slope, index=[df_stock.index[i]])
    slopes.append(s)
df_stock["slope"] = pd.concat(slopes)
df_stock = df_stock[df_stock.slope <= 0]

high_thrd = df_stock.open_gap.quantile(0.9)
low_thrd = df_stock.open_gap.quantile(0.1)
high_df = df_stock[df_stock.open_gap >= high_thrd]
low_df = df_stock[df_stock.open_gap <= low_thrd]

print high_thrd, low_thrd
plt.scatter(high_df["open_gap"], high_df["max_profit"], alpha=0.1, c='green')
plt.scatter(low_df["open_gap"], low_df["max_profit"], alpha=0.1, c='red')
plt.show()
#plot_corr(df_stock)
#test_model(df_stock)
