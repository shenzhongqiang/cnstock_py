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
    df = pd.DataFrame(columns=["increase", "mcap", "zhangting30"])
    for exsymbol in exsymbols:
        if not store.has(exsymbol):
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
        df_past.loc[:, "increase"] = df_past.close / df_past.close60 - 1
        df.loc[exsymbol] = [df_past.iloc[-1].increase, mcap, df_past.iloc[-1].zhangting30]
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
    #df_zt = get_zt_time(date, df_part.index)
    #df_res = df_res.merge(df_zt, how="inner", left_index=True, right_index=True)
    #df_res.loc[:, "bs_ratio"] = df_res.fengdan/df_res.zt_vol
    #df_res.loc[:, "sell_by_vol"] = df_res.zt_vol / df_res.volume
    df_plt = df_res[["fengdan", "fengdan_money", "fengdanvol", "lt_mcap", "increase", "v_diff"]]
    df_plt = df_plt.dropna(how="any")
    print(df_plt.sort_values("fengdan", ascending=False).head(50))

def get_strong_dieting(df):
    print("=========== strong dieting =========")
    df_part = df.loc[(df.chgperc < -9.9) & (df.b1_v == 0)]
    print(df_part.sort_values("v_diff", ascending=True)[["lt_mcap", "v_diff"]].head(10))

def get_big_bid_volume(df):
    print("============ big bid volume =========")
    df_res = df.loc[df.a1_v >0].sort_values("v_diff", ascending=False).head(10)
    df_plt = df_res[["chgperc", "lt_mcap", "fengdan", "v_diff", "a1_v", "b1_v"]]
    print(df_plt)

def get_small_mcap(date, df):
    print("============ small mcap =============")
    df_part = df.loc[df.lt_mcap < 10]
    df_hist = filter_by_history(date, df_part.index)
    df_res = df_part.merge(df_hist, how="inner", left_index=True, right_index=True)
    df_plt = df_res[["chgperc", "lt_mcap", "increase"]]
    df_plt = df_plt.dropna(how="any").sort_values("increase", ascending=True).head(10)
    print(df_plt)

def get_biggest_fengdan(df):
    print("============ biggest fengdan =========")
    print(df.sort_values("fengdan_money", ascending=False)[["fengdan_money", "fengdan", "lt_mcap"]].head(10))

if len(sys.argv) < 2:
    print("Usage: %s <2019-03-08>" % sys.argv[0])
    sys.exit(1)

pd.set_option('display.max_rows', None)

date = sys.argv[1]
df_base = stock.utils.symbol_util.get_realtime_by_date(date)

# 10% stock
df = df_base.loc[(df_base.lt_mcap > 0) & (df_base.volume > 0)].copy()
df.loc[:, "fengdan"] = df["b1_v"] * df["b1_p"] *100 / df["lt_mcap"] / 1e8
df.loc[:, "fengdan_money"] = df["b1_v"]*df["b1_p"]/1e6
df.loc[:, "fengdanvol"] = df["b1_v"] / df["volume"]
df.loc[:, "v_diff"] = (df.b1_v - df.a1_v) * df.close / df.lt_mcap / 1e6
df.loc[:, "chg_per_vol"] = df.chgperc / (df.volume*df.close/df.lt_mcap/1e6)
df.loc[:, "range_per_vol"] = (df.high/df.low-1) / (df.volume*df.close/df.lt_mcap/1e6)

get_strong_zhangting(date, df)
get_strong_dieting(df)
get_big_bid_volume(df)
get_small_mcap(date, df)
get_biggest_fengdan(df)
print(df.loc["sz300414"])
