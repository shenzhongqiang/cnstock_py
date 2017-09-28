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
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type
from stock.lib.candlestick import compare_stock
from stock.lib.finance import load_stock_basics

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

def get_profit(df, idx, stop_loss):
    num = 11
    if len(df) - idx < num:
        return np.nan

    for i in range(idx+1, len(df)):
        if df.ix[i].low <= df.ix[idx].close * (1-stop_loss):
            break
    profit = df.iloc[idx+1:i].close.max() / df.iloc[idx].close - 1
    return profit

def generate_middle():
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    columns = [
        "exsymbol",
        "break_date",
        "profit",
        "chg",
        "prev_chg",
        "up_ratio",
        "close_std",
        "vol_ratio",
        "mean_vol",
        "recent_up_ratio",
        "drawdown",
        "opengap",
        "next_opengap",
        "next_body",
        "next_chg"
    ]
    result = pd.DataFrame(columns=columns)
    df_basics = load_stock_basics()
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        if len(df) >= 240 or len(df) < 22:
            continue

        total_shares = df_basics.loc[exsymbol, "totals"] * 1e6

        df["chg"] = df.close.pct_change()
        df["body"] = df.close - df.open
        df["max_vol"] = df.volume.shift(1).rolling(window=20).max() / total_shares
        df["mean_vol"] = df.volume.shift(1).rolling(window=20).mean() / total_shares
        df["close_std"] = df.close.shift(1).rolling(window=20).std() / df.close.shift(1)
        df["recent_up_ratio"] = df.close /  df.close.shift(1).rolling(window=20).min() -1
        df["opengap"] = df.open / df.close.shift(1) - 1
        df["next_opengap"] = df.open.shift(-1) / df.close - 1
        df["next_body"] = df.close.shift(-1) / df.open.shift(-1) - 1
        df["next_chg"] = df.chg.shift(-1)
        i = 1
        for i in range(1, len(df.index)):
            row = df.ix[i]
            row_yest = df.ix[i-1]
            if row.high < row_yest.high:
                break
        for j in range(i, len(df.index)):
            if j < 20:
                continue
            row = df.ix[j]
            prev_chg = df.ix[j-1].chg
            chg = df.ix[j].chg
            min_close = df.iloc[i:j].close.min()
            up_ratio = df.ix[j].close / min_close - 1
            vol_ratio = row.volume / total_shares
            drawdown = min_close / df.ix[i-1].high - 1
            if vol_ratio > row.max_vol and row.body > 0: # and chg > -0.03 and prev_chg > -0.03 and row.up_ratio < 0.2:
                profit = get_profit(df, j, 0.05)
                break_date = df.index[j]
                result.loc[len(result)] = [
                    exsymbol,
                    break_date,
                    profit,
                    chg,
                    prev_chg,
                    up_ratio,
                    row.close_std,
                    vol_ratio,
                    row.mean_vol,
                    row.recent_up_ratio,
                    drawdown,
                    row.opengap,
                    row.next_opengap,
                    row.next_body,
                    row.next_chg
                ]
        #result.loc[len(result)] = [exsymbol, ipo_date, free_date, break_date, down_days, high_date, high_ratio, max_profit, min_profit, downward, market_cap]

    result.dropna(how="any",inplace=True)
    print "===== zhangting ====="
    zt = result[result.chg > 0.095][result.mean_vol < 0.03]
    print zt
    result.to_csv("/tmp/subnew2.csv")

def parse_middle(filepath="/tmp/subnew2.csv"):
    pd.set_option('display.max_rows', None)
    df = pd.read_csv(filepath, encoding="utf-8", dtype={"exsymbol": str})
    zt = df[df.chg > 0.099][df.next_opengap < 0.05]
    print zt[zt.next_opengap < -.015].sort_values(["next_opengap"], ascending=False)
    #print zt.sort_values(["profit"])


if __name__ == "__main__":
    generate_middle()
    parse_middle()
