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
#pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
columns = ["exsymbol", "std_close", "std_body", "std_range", "std_chg", "std_gap", "std_upper"]
result = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 250:
        continue

    df["chg"] = df.close.pct_change()
    df["body"] = (df.close - df.open) / df.close.shift(1)
    df["range"] = (df.high - df.low) / df.close.shift(1)
    df["gap"] = (df.open - df.close.shift(1)) / df.close.shift(1)
    df["upper"] = df[["open","close"]].max(axis=1)
    df["upshad"] = (df.high -df.upper)/df.close.shift(1)
    std_close = np.std(df.iloc[-20:].close/df.iloc[-20].close)
    std_body = np.std(df.iloc[-20:].body)
    std_range = np.std(df.iloc[-20:].range)
    std_chg = np.std(df.iloc[-20:].chg)
    std_gap = np.std(df.iloc[-20:].gap)
    std_upper = np.std(df.iloc[-20:].upshad)
    result.loc[len(result)] = [exsymbol, std_close, std_body, std_range, std_chg, std_gap, std_upper]

print result.sort_values(["std_gap"], ascending=True)
