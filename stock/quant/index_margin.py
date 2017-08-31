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

def get_slope(array):
    y = np.copy(array) / array[0]
    x = range(len(y))
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

def dump_margin_data(start, end, symbol):
    df = ts.sh_margin_details(start=start, end=end, symbol=symbol)
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "margindata")
    df.to_csv(filepath, encoding="utf-8")

def load_margin_data():
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "margindata")
    df = pd.read_csv(filepath, encoding="utf-8")
    return df

pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
start = '2016-08-28'
end = '2017-08-28'
exsymbol = 'sh601398'
symbol = exsymbol_to_symbol(exsymbol)
df = store.get(exsymbol).loc[start:end]
#dump_margin_data(start, end, symbol)
df_margin = load_margin_data()
date_index = pd.to_datetime(df_margin.opDate, format='%Y-%m-%d')
df_margin.set_index(date_index, inplace=True)
df["rzye"] = df_margin.rzye
df["rzmre"] = df_margin.rzmre
df["rqmcl"] = df_margin.rqmcl

std = StandardScaler()
df["rzye"] = std.fit_transform(df.rzye)
df["rzmre"] = std.fit_transform(df.rzmre)
df["rqmcl"] = std.fit_transform(df.rqmcl)

print df[df.rqmcl > 2]
df.rqmcl.hist()
plt.show()

