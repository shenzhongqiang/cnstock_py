import re
import os
import sys
import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from stock.globalvar import *
import tushare as ts
from config import store_type


def get_last_trading_date(today):
    yest = today - BDay(1)
    folder = TICK_DIR["daily"]
    while True:
        yest_str = yest.strftime("%Y-%m-%d")
        filepath = os.path.join(folder, yest_str + ".csv")
        if os.path.isfile(filepath):
            break
        yest = yest - BDay(1)
    return yest

def get_industry():
    df_basics = ts.get_stock_basics()
    df_basics.loc[:, "code"] = df_basics.index
    df_basics.loc[:, "exsymbol"] = df_basics.code.apply(lambda x: 'sh'+x if re.match(r'6', x) else 'sz'+x)
    df_basics.set_index("exsymbol", inplace=True)
    return df_basics[["industry"]]

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

def get_zhangting(today):
    today_str = today.strftime("%Y-%m-%d")
    yest = get_last_trading_date(today)
    yest_str = yest.strftime("%Y-%m-%d")

    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_tick = stock.utils.symbol_util.get_tick_by_date(today_str)
    df_tick.loc[:, "kaipan_money"] = df_tick["kaipan_money"]/1e8
    df_today["opengap"] = df_today.apply(lambda x: x["close"] if x["open"] == 0.0 else x["open"], axis=1)/df_today.yest_close - 1
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)
    df_yest_zt = df_yest[(df_yest.chgperc>9.9) & (df_yest.lt_mcap>0) & (df_yest.volume>0)].copy()
    df_yest_zt.loc[:, "fengdan"] = df_yest_zt["b1_v"] * df_yest_zt["b1_p"] *100 / df_yest_zt["lt_mcap"] / 1e8
    df_yest_zt.loc[:, "fengdan_money"] = df_yest_zt["b1_v"]*df_yest_zt["b1_p"]/1e6
    df_res = df_yest_zt[["fengdan", "fengdan_money"]].merge(df_today, how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_tick[["kaipan_money"]], how="left", left_index=True, right_index=True)
    df_tick_yest = stock.utils.symbol_util.get_tick_by_date(yest_str)
    df_res = df_res.merge(df_tick_yest[["sell_amount", "zhangting_min"]], how="inner", left_index=True, right_index=True)
    df_res["sell_speed"] = df_res["sell_amount"]/df_res["zhangting_min"]
    df_hist = filter_by_history(yest_str, df_res.index)
    df_res = df_res.merge(df_hist, how="inner", left_index=True, right_index=True)
    df_basics = get_industry()
    df_res = df_res.merge(df_basics, how="left", left_index=True, right_index=True)
    df_res.loc[:, "kaipan_by_fengdan"] = df_res.kaipan_money/df_res.fengdan_money
    df_res = df_res[(df_res.opengap<0.05) & (df_res.opengap>0) & (df_res.lt_mcap<200) & (df_res.zhangting_min>100)]
    df_res.loc[:, "money_ratio"] = (df_res.sell_amount+df_res.fengdan_money)/df_res.lt_mcap

    columns = ["opengap", "fengdan", "fengdan_money", "sell_amount", "zhangting_min", "lt_mcap", "kaipan_money", "increase5", "industry"]
    print(df_res[columns].sort_values("sell_amount", ascending=True))

def get_zhangting_begin(today):
    today_str = today.strftime("%Y-%m-%d")
    yest = get_last_trading_date(today)
    yest_str = yest.strftime("%Y-%m-%d")
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)
    df_yest.loc[:, "highperc"] = df_yest["high"]/df_yest["yest_close"]-1
    df_yest.loc[:, "openperc"] = df_yest["open"]/df_yest["yest_close"]-1
    df_yest.loc[:, "yest_chg"] = df_yest["chgperc"]
    df_res = df_yest[(df_yest.highperc>0.099) & (df_yest.chgperc<9.9) & (df_yest.lt_mcap<100) & (df_yest.close>df_yest.open)]
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today.loc[:, "opengap"] = df_today.apply(lambda x: x["close"] if x["open"] == 0.0 else x["open"], axis=1)/df_today.yest_close - 1
    df_tick_yest = stock.utils.symbol_util.get_tick_by_date(yest_str)
    df_tick_yest.loc[:, "yest_kaipan_money"] = df_tick_yest["kaipan_money"]
    df_tick_today = stock.utils.symbol_util.get_tick_by_date(today_str)
    df_res = df_res.merge(df_today[["opengap"]], how="inner", left_index=True, right_index=True)
    df_res = df_res[df_res.opengap>0]
    df_res = df_res.merge(df_tick_yest[["sell_amount", "zhangting_min", "yest_kaipan_money"]], how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_tick_today[["kaipan_money"]], how="inner", left_index=True, right_index=True)
    df_basics = get_industry()
    df_res = df_res.merge(df_basics, how="left", left_index=True, right_index=True)
    columns = ["yest_chg", "opengap", "sell_amount", "zhangting_min", "yest_kaipan_money", "kaipan_money", "lt_mcap", "industry"]
    print(df_res[columns].sort_values("sell_amount", ascending=True))

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

today = None
if len(sys.argv) == 1:
    today = pd.datetime.today()
else:
    today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

get_zhangting(today)
get_zhangting_begin(today)
