import sys
import pandas as pd
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from config import store_type
import tushare as ts

def filter_by_history(date, exsymbols):
    store = get_store(store_type)
    result = []
    df_basics = load_stock_basics()
    df = pd.DataFrame(columns=["increase60", "increase5", "mcap", "zhangting30"])
    for exsymbol in exsymbols:
        if not store.has(exsymbol):
            continue
        if exsymbol not in df_basics.index:
            continue
        outstanding = df_basics.loc[exsymbol, "outstanding"]
        df_stock = store.get(exsymbol)
        mcap = outstanding * df_stock.iloc[-1].close
        df_past = df_stock.loc[:date].copy()
        if len(df_past) == 0:
            continue
        df_past.loc[:, "chg"] = df_past.close / df_past.close.shift(1) - 1
        df_past.loc[:, "zhangting"] = df_past["chg"] > 0.09
        df_past.loc[:, "zhangting30"] = df_past["zhangting"].rolling(window=30).sum()
        df_past.loc[:, "close60"] = df_past.close.rolling(window=60).min()
        df_past.loc[:, "close5"] = df_past.close.rolling(window=5).min()
        df_past.loc[:, "increase60"] = df_past.close / df_past.close60 - 1
        df_past.loc[:, "increase5"] = df_past.close / df_past.close5 - 1
        df.loc[exsymbol] = [df_past.iloc[-1].increase60, df_past.iloc[-1].increase5, mcap, df_past.iloc[-1].zhangting30]
    return df

def get_zt_time(date, exsymbols):
    df_res = pd.DataFrame(columns=["zt_vol"])
    df_basics = load_stock_basics()
    for exsymbol in exsymbols:
        symbol = stock.utils.symbol_util.exsymbol_to_symbol(exsymbol)
        outstanding = df_basics.loc[exsymbol, "outstanding"]
        df = ts.get_tick_data(symbol, date=date, src="tt")
        high = df.price.max()
        zt_vol = df[df.price==high].volume.sum()
        df_res.loc[exsymbol] = [zt_vol]
    return df_res

def get_strong_zhangting(date, df):
    print("============ strong zhangting ============")
    df_part = df.loc[(df.chgperc > 9.9) & (df.a1_v == 0)]
    df_hist = filter_by_history(date, df_part.index)
    df_res = df_part.merge(df_hist, how="inner", left_index=True, right_index=True)
    df_plt = df_res[["fengdan", "fengdan_money", "zhangting_min", "fengdanvol", "lt_mcap", "increase5", "increase60"]]
    df_plt = df_plt.dropna(how="any")
    print(df_plt.sort_values("fengdan", ascending=False).head(50))


def get_big_bid_volume(df):
    print("============ big bid volume =========")
    df_res = df.loc[df.lt_mcap<100][df.chgperc < 0.0][df.fengdan_money <0.03].sort_values("fengdan_money", ascending=False).head(10)
    df_plt = df_res[["chgperc", "lt_mcap", "fengdan", "fengdan_money", "a1_v", "b1_v"]]
    print(df_plt)

def get_biggest_fengdan(df):
    print("============ biggest fengdan =========")
    print(df.sort_values("fengdan_money", ascending=False)[["fengdan_money", "fengdan", "zhangting_min", "lt_mcap"]].head(10))

if len(sys.argv) < 2:
    print("Usage: %s <2019-03-08>" % sys.argv[0])
    sys.exit(1)

pd.set_option('display.max_rows', None)

date = sys.argv[1]
df_base = stock.utils.symbol_util.get_realtime_by_date(date)
df_tick = stock.utils.symbol_util.get_tick_by_date(date)

# 10% stock
df = df_base.loc[(df_base.lt_mcap > 0) & (df_base.volume > 0)].copy()
df.loc[:, "fengdan"] = df["b1_v"] * df["b1_p"] *100 / df["lt_mcap"] / 1e8
df.loc[:, "fengdan_money"] = df["b1_v"]*df["b1_p"]/1e6
df.loc[:, "fengdanvol"] = df["b1_v"] / df["volume"]
df.loc[:, "chg_per_vol"] = df.chgperc / (df.volume*df.close/df.lt_mcap/1e6)
df.loc[:, "range_per_vol"] = (df.high/df.low-1) / (df.volume*df.close/df.lt_mcap/1e6)
df = df.merge(df_tick[["zhangting_min"]], how="inner", left_index=True, right_index=True)

get_strong_zhangting(date, df)
get_big_bid_volume(df)
get_biggest_fengdan(df)
