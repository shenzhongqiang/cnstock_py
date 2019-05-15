import sys
import datetime
import numpy as np
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd

def print_stocks(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()

    df_res = pd.DataFrame(columns=["tmr_chg", "increase"])
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        if len(df) < 200:
            continue
        if date not in df.index:
            continue
        idx = df.index.get_loc(date)
        min10 = np.min(df.iloc[idx-20:idx].close)
        increase = df.iloc[idx].close/min10 - 1
        tmr_chg = 0
        if idx+1 < len(df):
            tmr_chg = df.iloc[idx+1].close / df.iloc[idx].close - 1
        df_res.loc[exsymbol] = [tmr_chg, increase]

    df_res = df_res.dropna(how="any")
    pd.set_option('display.max_rows', None)
    df_plt = df_res.sort_values("increase", ascending=True).tail(20)
    print(df_plt)

def get_max_drawdown(df_orig):
    df = df_orig.copy()
    df.loc[:, "change"] = df.close - df.close.shift(1)
    drawdowns = []
    starts = []
    for i in range(1, len(df), 1):
        if i == 1:
            drawdowns.append(0)
            starts.append(1)
            continue

        last_drawdown = drawdowns[-1]
        last_start = starts[-1]
        row = df.iloc[i]
        if last_drawdown < 0:
            drawdown = last_drawdown + row.change
            drawdowns.append(drawdown)
            starts.append(last_start)
        else:
            drawdown = row.change
            drawdowns.append(drawdown)
            starts.append(i)

    idxmin = np.argmin(drawdowns)
    drawdown = drawdowns[idxmin]
    start_close = df.iloc[starts[idxmin]-1].close
    max_drawdown = drawdown/start_close
    return max_drawdown

def print_potential(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()

    df_res = pd.DataFrame(columns=["big_close_num", "big_high_num", "increase", "max_drawdown"])
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        if len(df) < 200:
            continue
        if date not in df.index:
            continue
        df.loc[:, "closeperc"] = df["close"] / df["close"].shift(1) - 1
        df.loc[:, "highperc"] = df["high"] / df["close"].shift(1) - 1
        df.loc[:, "big_close"] = df["closeperc"] > 0.06
        df.loc[:, "big_high"] = df["highperc"] > 0.099
        df.loc[:, "big_close_num"] = df["big_close"].rolling(window=22).sum()
        df.loc[:, "big_high_num"] = df["big_high"].rolling(window=22).sum()
        idx = df.index.get_loc(date)
        min10 = np.min(df.iloc[idx-22:idx].close)
        increase = df.iloc[idx].close/min10 - 1
        max10 = np.max(df.iloc[idx-22:idx].close)
        max_drawdown = get_max_drawdown(df.iloc[idx-22:idx+1])
        if max_drawdown < -0.15:
            continue

        big_close_num = df.iloc[idx].big_close_num
        big_high_num = df.iloc[idx].big_high_num
        df_res.loc[exsymbol] = [big_close_num, big_high_num, increase, max_drawdown]

    df_res = df_res.dropna(how="any")
    pd.set_option('display.max_rows', None)
    df_plt = df_res[df_res.big_close_num>=4].sort_values("increase", ascending=True)
    print(df_plt)

date = None
if len(sys.argv) == 1:
    date = datetime.date.today().strftime("%Y-%m-%d")
else:
    date = sys.argv[1]

pd.set_option('display.max_rows', None)
#print_potential(date)
print_stocks(date)
