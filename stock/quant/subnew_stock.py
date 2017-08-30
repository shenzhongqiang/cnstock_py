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

def get_zt_num(df):
    num = 1
    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) < 1e-3:
            num += 1
        else:
            break
    return float(num)

def get_zt_ratio(df):
    ratio = 0
    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) < 1e-3:
            continue
        else:
            ratio = row.open / df.ix[0].open - 1
            return ratio

def get_zt_volume(df):
    idx = 0
    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) < 1e-3:
            continue
        else:
            idx = i
            break
    #vol_sum = df.iloc[idx+1:idx+5].volume.sum()/df.iloc[idx].volume
    vol_sum = df.iloc[0:idx+3].volume.sum()
    return vol_sum

def get_zt_chg(df, exsymbol):
    idx = 0
    df["chg"] = df.close.pct_change()
    df_index = None
    store = get_store(store_type)
    if re.match('sh', exsymbol):
        df_index = store.get('id000001')
    else:
        df_index = store.get('id399001')
    df_index['chg'] = df_index.close.pct_change()

    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) < 1e-3:
            continue
        else:
            idx = i
            break
    date = df.iloc[idx].date
    chg_diff = df.loc[date].chg - df_index.loc[date].chg
    return chg_diff

def get_profit(df):
    idx = 0
    for i in range(1, len(df.index)):
        row = df.ix[i]
        if abs(row.close - row.open) < 1e-3:
            continue
        else:
            idx = i
            break
    max_close = df.iloc[idx+1:idx+70].close.max()
    profit = max_close / df.iloc[idx].close - 1
    return profit

pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
index_history = store.get('id000001')
index_history['chg'] = index_history.close.pct_change()
columns = ['exsymbol', 'zt_num', 'zt_ratio', 'profit', 'ipo_price', 'ballot', 'pe', 'zt_volume', 'zt_chg']
result = pd.DataFrame(columns=columns)
df_ipo = load_ipo_data()
for exsymbol in exsymbols:
    if not re.match('sh', exsymbol):
            continue
    df = store.get(exsymbol)
    if len(df.index) >= 400 or len(df.index) <= 70:
        continue
    zt_num = get_zt_num(df)
    zt_ratio = get_zt_ratio(df)
    profit = get_profit(df)
    symbol = exsymbol_to_symbol(exsymbol)
    df_symbol = df_ipo[df_ipo.code == symbol]
    if len(df_symbol) == 0:
        continue

    row = df_symbol.iloc[0]
    ipo_price = float(row.price)
    ballot = float(row.ballot)
    pe = float(row.pe)
    ipo_amount = float(row.amount) * 100
    ipo_market = float(row.markets) * 100
    zt_volume = get_zt_volume(df) / ipo_amount
    zt_chg = get_zt_chg(df, exsymbol)
    result.loc[len(result)] = [exsymbol, zt_num, zt_ratio, profit, ipo_price, ballot, pe, zt_volume, zt_chg]


std_tr = StandardScaler()
X_orig = result[["zt_ratio", "ipo_price"]].copy()
X = std_tr.fit_transform(X_orig)
y = result["profit"].copy()
reg = RandomForestRegressor(max_depth=5)
reg.fit(X,y)
scores = cross_val_score(reg, X, y, scoring="neg_mean_squared_error", cv=5)
print len(X)
print np.sqrt(-scores)
result["pred"] = reg.predict(X)
print result[["exsymbol", "zt_ratio", "ipo_price", "profit", "pred"]].sort_values(["profit"])

#attr = ["zt_ratio", "profit", "ipo_price", "zt_volume", "zt_chg"]
#scatter_matrix(result[attr], alpha=0.5, figsize=(12, 12))
#plt.show()

#price_thrd = result.ipo_price.quantile(0.1)
#ratio_thrd = result.zt_ratio.quantile(0.1)
#vol_thrd = result.zt_volume.quantile(0.9)
#print result[result.ipo_price < price_thrd]
#print result[result.zt_ratio < ratio_thrd]
#print result[result.zt_volume > vol_thrd]
