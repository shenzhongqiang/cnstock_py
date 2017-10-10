import time
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

def get_trade(exsymbol, df, break_idx, start_idx, sl_ratio=0.05, result=None):
    if start_idx >= len(df):
        return
    state = 0
    buy_price = 0.0
    sl_price = 0.0
    record_high = 0.0
    buy_idx = 0
    sell_idx = 0
    chg = 0.0
    prev_chg = 0.0
    vol_ratio = 0.0
    days = 0
    for i in range(start_idx, len(df)):
        row = df.iloc[i]
        if state == 0 and row.prev_chg > 0.099:
            open_date = df.index[i]
            buy_price = row.open
            sl_price = buy_price * (1-sl_ratio)
            record_high = buy_price
            chg = row.chg
            prev_chg = row.prev_chg
            prevprev_chg = row.prevprev_chg
            ppprev_chg = row.ppprev_chg
            vol_ratio = row.vol_ratio
            min_close = df.iloc[break_idx:i].close.min()
            up_ratio = row.close / min_close - 1
            drawdown = min_close / df.ix[break_idx-1].high - 1
            mcap = row.total_shares * buy_price
            buy_idx = i
            state = 1
            days += 1
            continue
        if state == 1:
            if not is_sellable(df, df.index[i]):
                state = -1
                continue

            if row.open <= sl_price:
                sell_price = row.open
                sell_idx = i
                close_date = df.index[i]
                profit = sell_price / buy_price - 1
                result.loc[len(result)] = [exsymbol, row.total_shares, row.ipo_date, mcap, open_date, close_date,
                    profit, chg, prev_chg, prevprev_chg, ppprev_chg, up_ratio, row.close_std, vol_ratio, row.mean_vol, row.recent_up_ratio,
                    drawdown, row.opengap, row.next_opengap, row.next_body, row.next_chg
                ]
                days = 0
                state = 0
                return get_trade(exsymbol, df, break_idx, sell_idx+1, sl_ratio, result)
            elif row.low <= sl_price:
                sell_price = sl_price
                sell_idx = i
                close_date = df.index[i]
                profit = sell_price / buy_price - 1
                result.loc[len(result)] = [exsymbol, row.total_shares, row.ipo_date, mcap, open_date, close_date,
                    profit, chg, prev_chg, prevprev_chg, ppprev_chg, up_ratio, row.close_std, vol_ratio, row.mean_vol, row.recent_up_ratio,
                    drawdown, row.opengap, row.next_opengap, row.next_body, row.next_chg
                ]
                days = 0
                state = 0
                return get_trade(exsymbol, df, break_idx, sell_idx+1, sl_ratio, result)
            elif days == 22:
                sell_price = row.close
                sell_idx = i
                close_date = df.index[i]
                profit = sell_price / buy_price - 1
                result.loc[len(result)] = [exsymbol, row.total_shares, row.ipo_date, mcap, open_date, close_date,
                    profit, chg, prev_chg, prevprev_chg, ppprev_chg, up_ratio, row.close_std, vol_ratio, row.mean_vol, row.recent_up_ratio,
                    drawdown, row.opengap, row.next_opengap, row.next_body, row.next_chg
                ]
                days = 0
                state = 0
                return get_trade(exsymbol, df, break_idx, sell_idx+1, sl_ratio, result)
            elif row.close > record_high:
                record_high = row.close
                sl_price = record_high * (1-sl_ratio)
                days += 1
            continue
        if state == -1:
            if is_sellable(df, df.index[i]):
                sell_price = row.open
                sell_idx = i
                close_date = df.index[i]
                profit = sell_price / buy_price - 1
                result.loc[len(result)] = [exsymbol, row.total_shares, row.ipo_date, mcap, open_date, close_date,
                    profit, chg, prev_chg, prevprev_chg, ppprev_chg, up_ratio, row.close_std, vol_ratio, row.mean_vol, row.recent_up_ratio,
                    drawdown, row.opengap, row.next_opengap, row.next_body, row.next_chg
                ]
                days = 0
                state = 0
                return get_trade(exsymbol, df, break_idx, sell_idx+1, sl_ratio, result)


def get_profit(df, idx, stop_loss):
    num = 22
    if len(df) - idx < num:
        return np.nan

    for i in range(idx+2, idx+num):
        if df.ix[i].low <= df.ix[idx].close * (1-stop_loss):
            break
    profit = df.iloc[idx+2:i].close.max() / df.iloc[idx+1].open - 1
    return profit

def generate_middle():
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    columns = [
        "exsymbol",
        "total_shares",
        "ipo_date",
        "mcap",
        "open_date",
        "close_date",
        "profit",
        "chg",
        "prev_chg",
        "prevprev_chg",
        "ppprev_chg",
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
        if len(df) >= 1000 or len(df) < 22:
            continue

        df = df.iloc[:250]
        total_shares = df_basics.loc[exsymbol, "totals"] * 1e6

        df["total_shares"] = total_shares
        df["ipo_date"] = df.index[0]
        df["chg"] = df.close.pct_change()
        df["prev_chg"] = df.chg.shift(1)
        df["prevprev_chg"] = df.chg.shift(2)
        df["ppprev_chg"] = df.chg.shift(3)
        df["body"] = df.close - df.open
        df["max_vol"] = df.volume.shift(1).rolling(window=20).max() / total_shares
        df["mean_vol"] = df.volume.shift(1).rolling(window=20).mean() / total_shares
        df["close_std"] = df.close.shift(1).rolling(window=20).std() / df.close.shift(1)
        df["recent_up_ratio"] = df.close /  df.close.shift(1).rolling(window=20).min() -1
        df["opengap"] = df.open / df.close.shift(1) - 1
        df["next_opengap"] = df.open.shift(-1) / df.close - 1
        df["next_body"] = df.close.shift(-1) / df.open.shift(-1) - 1
        df["next_chg"] = df.chg.shift(-1)
        df["vol_ratio"] = df.volume / total_shares
        i = 1
        for i in range(1, len(df.index)):
            row = df.ix[i]
            row_yest = df.ix[i-1]
            if row.high < row_yest.high:
                break
        break_idx = i
        get_trade(exsymbol, df, break_idx, break_idx+1, sl_ratio=0.05, result=result)
    result.dropna(how="any",inplace=True)
    zt = result[result.prev_chg > 0.095][result.mean_vol < 0.03]
    result.to_csv("/tmp/subnew2.csv")

def parse_middle(filepath="/tmp/subnew2.csv"):
    pd.set_option('display.max_rows', None)
    df = pd.read_csv(filepath, encoding="utf-8", dtype={"exsymbol": str})
    df = df[df.open_date > "2015-10-01"][df.open_date<"2016-10-01"][df.opengap < 0.05][df.opengap > -0.05]
    print df.drop(["exsymbol", "ipo_date", "open_date", "close_date"], axis=1).corr()["profit"]
    test = df[df.recent_up_ratio > 0.2][df.vol_ratio < 0.01][df.close_std > 0.10]
    print len(test), test.profit.median(), test.profit.mean(), (test.profit+1).prod()
    #print test[["exsymbol", "open_date", "close_date", "profit"]].sort_values(["open_date"])
    x = np.linspace(-0.10, 0.1, 1000)
    y = []
    for i in x:
        zt = df[df.opengap > i]
        result = zt.profit
        y.append(result.median())

    plt.plot(x, y)
    plt.show()
    #print df.sort_values(["profit"])


if __name__ == "__main__":
    #generate_middle()
    parse_middle()
