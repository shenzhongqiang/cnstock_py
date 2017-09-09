import os
import cPickle as pickle
import scipy
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, exsymbol_to_symbol, symbol_to_exsymbol
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
    df["exsymbol"] = map(lambda x: symbol_to_exsymbol(x), df.code)
    df["market_cap"] = df.amount.astype(float) * df.price.astype(float) / 10000
    df.set_index("exsymbol", inplace=True)
    df.drop_duplicates(subset=["code"], inplace=True)
    return df

df_ipo = load_ipo_data()
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
columns = ["exsymbol", "ipo_date", "free_date", "break_date", "down_days", "high_date", "max_profit", "market_cap"]
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
    ipo_price = df.ix[0].open
    zt_high = df.ix[i].high
    if (df.iloc[i+1:].close > zt_high).sum() == 0:
        continue
    break_date = df.iloc[i+1:][df.iloc[i+1:].close > zt_high].iloc[0].date
    break_idx = df.index.get_loc(break_date)
    if len(df) < break_idx+31:
        continue
    max_profit = df.iloc[break_idx+1:break_idx+31].close.max() / df.iloc[break_idx+1].open - 1
    down_days = break_idx - i

    if len(df) < i+30:
        continue
    if exsymbol not in df_ipo.index:
        continue
    market_cap = df_ipo.loc[exsymbol].get_value("market_cap")
    max_close = df.iloc[i:i+30].close.max()
    high_date = df.iloc[break_idx+1:break_idx+31].close.idxmax()
    ipo_date = df.index[0]
    free_date = df.ix[i].date
    zt_ratio = df.ix[i-1].close / df.ix[0].close - 1
    zt_close = df.ix[i-1].close
    high = max_close / df.ix[i].high - 1
    low = df.iloc[i+1:i+10].low.min() / df.ix[i].high - 1
    free_open = df.ix[i].open_gap
    free_close = df.ix[i].chg
    free_body = df.ix[i].body
    result.loc[len(result)] = [exsymbol, ipo_date, free_date, break_date, down_days, high_date, max_profit, market_cap]

print result.sort_values(["max_profit"], ascending=True)

