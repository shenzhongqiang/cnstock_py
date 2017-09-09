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

def dump_data():
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "pedata")
    df_basic = ts.get_stock_basics()
    df_report = ts.get_report_data(2017, 2)
    df_report.drop_duplicates(inplace=True)
    df_report.set_index('code', inplace=True)
    df_result = pd.concat([df_report, df_basic], axis=1, join="inner")
    df_result.to_csv(filepath, encoding="utf-8")

def load_data():
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "pedata")
    df = pd.read_csv(filepath, encoding="utf-8", dtype=str)
    return df

pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
dump_data()
df = load_data()

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_close = pd.DataFrame(columns=["code", "close"])
for exsymbol in exsymbols:
    symbol = exsymbol_to_symbol(exsymbol)
    df_stock = store.get(exsymbol)
    close = df_stock.iloc[-1].close
    df_close.loc[len(df_close)] = [symbol, close]

df_result = pd.merge(df, df_close, on="code")
df_result["real_pe"] = df_result.close * df_result.totals.astype(float) * 10000 / df_result.net_profits.astype(float) / 4.0
print df_result[df_result.real_pe > 0].sort_values(["real_pe"], ascending=False)
