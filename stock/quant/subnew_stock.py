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
from stock.strategy.utils import is_sellable
from stock.trade.order import Order
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type
from stock.lib.candlestick import compare_stock

class RangeToCategory(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=0.05):
        self.threshold = threshold

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        result = []
        for rowdata in X:
            if rowdata >= self.threshold:
                result.append(1)
            else:
                result.append(0)
        return np.array(result)

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
columns = ["exsymbol", "ipo_date", "free_date", "break_date", "down_days", "high_date", "high_ratio", "max_profit", "min_profit", "downward", "market_cap"]
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
        row_yest = df.ix[i-1]
        if row.high < row_yest.high:
            break
    ipo_price = df.ix[0].open
    zt_high = df.ix[i-1].high
    high_ratio = zt_high / df.ix[0].open - 1
    if (df.iloc[i+1:].close > zt_high).sum() == 0:
        continue
    break_date = df.iloc[i+1:][df.iloc[i+1:].close > zt_high].iloc[0].date
    break_idx = df.index.get_loc(break_date)
    if len(df) < break_idx+31:
        continue
    downward = df.iloc[i:break_idx].close.min() / df.iloc[i-1].high - 1
    max_profit = df.iloc[break_idx+1:break_idx+31].close.max() / df.iloc[break_idx+1].open - 1
    min_profit = df.iloc[break_idx+1:break_idx+31].close.min() / df.iloc[break_idx+1].open - 1
    down_days = break_idx - i

    if len(df) < i+30:
        continue
    if exsymbol not in df_ipo.index:
        continue
    market_cap = df_ipo.loc[exsymbol].get_value("market_cap")
    max_close = df.iloc[i:i+30].close.max()
    high_date = df.iloc[break_idx+1:break_idx+31].close.idxmax()
    ipo_date = df.index[0]
    free_date = df.ix[i-1].date
    result.loc[len(result)] = [exsymbol, ipo_date, free_date, break_date, down_days, high_date, high_ratio, max_profit, min_profit, downward, market_cap]

#print result[result.down_days >2]
#rtc = RangeToCategory(threshold=-0.1)
#y = rtc.transform(result.min_profit)
#X = result[["market_cap", "downward", "down_days", "high_ratio"]].copy()
#clf = RandomForestClassifier(n_estimators=30, class_weight="balanced", max_depth=10)
#scores = cross_val_score(clf, X, y, scoring="accuracy", cv=3)
#print scores
#date_a = result[result.exsymbol == "sz002836"].iloc[0].break_date
#date_b =  result[result.exsymbol == "sz002787"].iloc[0].break_date
#df_a = store.get("sz002811")
#df_b = store.get("sz002787")
#print compare_stock(df_a, df_b, date_a, date_b, 30, show_plot=True)
