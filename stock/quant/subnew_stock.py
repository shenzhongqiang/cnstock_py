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

def dump_ipo_data():
    df = ts.new_stocks()
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "ipodata")
    df.to_csv(filepath, encoding="utf-8")

def load_ipo_data():
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "ipodata")
    df = pd.read_csv(filepath, encoding="utf-8", dtype=str)
    return df



pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
columns = ["exsymbol", "ipo_date", "free_date", "high", "low", "free_open", "free_close", "free_body"]
result = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) >= 400 or len(df) < 10:
        continue

    df["chg"] = df.close.pct_change()
    df["open_gap"] = df.open / df.close.shift(1) - 1
    df["body"] = (df.close - df.open) / df.close.shift(1)
    i = 1
    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) > 1e-3 or row.chg < 0.095:
            break
    max_close = df.iloc[i+1:i+30].close.max()
    ipo_date = df.index[0]
    free_date = df.ix[i].date
    high = max_close / df.ix[i].high - 1
    low = df.iloc[i+1:i+10].low.min() / df.ix[i].high - 1
    free_open = df.ix[i].open_gap
    free_close = df.ix[i].chg
    free_body = df.ix[i].body
    result.loc[len(result)] = [exsymbol, ipo_date, free_date, high, low, free_open, free_close, free_body]


