import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts

def filter_by_history(date, exsymbols):
    store = get_store(store_type)
    result = []
    df = pd.DataFrame(columns=["increase60", "increase5", "future"])
    for exsymbol in exsymbols:
        if not store.has(exsymbol):
            continue
        df_stock = store.get(exsymbol)
        df_past = df_stock.loc[:date].copy()
        if len(df_past) == 0:
            continue
        close_min60 = np.min(df_past.iloc[-60:].close)
        close_min5 = np.min(df_past.iloc[-5:].close)
        increase60 = df_past.iloc[-1].close/close_min60-1
        increase5 = df_past.iloc[-1].close/close_min5-1
        future = df_stock.iloc[-1].close/df_past.iloc[-1].close-1
        df.loc[exsymbol] = [increase60, increase5, future]
    return df

def get_strong_zhangting(date):
    df_base = stock.utils.symbol_util.get_realtime_by_date(date)
    df_tick = stock.utils.symbol_util.get_tick_by_date(date)

    # 10% stock
    df = df_base.loc[(df_base.lt_mcap > 0) & (df_base.volume > 0)].copy()
    df.loc[:, "fengdan"] = df["b1_v"] * df["b1_p"] *100 / df["lt_mcap"] / 1e8
    df.loc[:, "fengdan_money"] = df["b1_v"]*df["b1_p"]/1e6
    df.loc[:, "fengdanvol"] = df["b1_v"] / df["volume"]
    df.loc[:, "chg_per_vol"] = df.chgperc / (df.volume*df.close/df.lt_mcap/1e6)
    df.loc[:, "range_per_vol"] = (df.high/df.low-1) / (df.volume*df.close/df.lt_mcap/1e6)
    df = df.merge(df_tick, how="inner", left_index=True, right_index=True)

    print("============ strong zhangting ============")
    df_part = df.loc[(df.chgperc > 9.9) & (df.a1_v == 0)]
    df_hist = filter_by_history(date, df_part.index)
    df_res = df_part.merge(df_hist, how="inner", left_index=True, right_index=True)
    df_plt = df_res[["fengdan", "fengdan_money", "zhangting_min", "sell_amount", "lt_mcap", "increase5", "increase60"]]
    df_plt = df_plt.dropna(how="any")
    print(df_plt.sort_values("zhangting_min", ascending=False).head(50))

    print("============ biggest fengdan =========")
    print(df.sort_values("fengdan_money", ascending=False)[["fengdan_money", "fengdan", "zhangting_min", "lt_mcap"]].head(10))

def get_zhangting_begin(date):
    print("============ zhangting begin =========")
    df_base = stock.utils.symbol_util.get_realtime_by_date(date)
    df_base.loc[:, "highperc"] = df_base["high"]/df_base["yest_close"]-1
    df_base.loc[:, "openperc"] = df_base["open"]/df_base["yest_close"]-1
    df = df_base.loc[(df_base.highperc > 0.099) & (df_base.chgperc < 9.9) & (df_base.openperc < 0.05)]
    df_tick = stock.utils.symbol_util.get_tick_by_date(date)
    df = df.merge(df_tick, how="inner", left_index=True, right_index=True)
    df_hist = filter_by_history(date, df.index)
    df = df.merge(df_hist, how="inner", left_index=True, right_index=True)
    columns = ["chgperc", "openperc", "zhangting_min", "sell_amount", "increase5", "increase60", "future"]
    print(df[columns].sort_values("zhangting_min", ascending=False))

if len(sys.argv) < 2:
    print("Usage: %s <2019-03-08>" % sys.argv[0])
    sys.exit(1)

pd.set_option('display.max_rows', None)

date = sys.argv[1]
get_strong_zhangting(date)
get_zhangting_begin(date)
