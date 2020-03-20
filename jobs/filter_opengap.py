import re
import os
import sys
import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
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
    df_industry = stock.utils.symbol_util.load_industry()
    df_res = df_industry.groupby("exsymbol")["industry"].agg({"industry": lambda x: ",".join(x)})
    return df_res

def get_concept():
    df = stock.utils.symbol_util.load_concept()
    df_res = df.groupby("exsymbol")["concept"].agg({"concept": lambda x: ",".join(x)})
    return df_res

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
    df_yest["zt_price"] = np.round(df_yest["yest_close"] * 1.1, 2)
    df_yest.loc[:, "is_zhangting"] = (df_yest["zt_price"]-df_yest["close"])<1e-8
    df_yest_zt = df_yest[(df_yest.is_zhangting==True) & (df_yest.lt_mcap>0) & (df_yest.volume>0)].copy()
    df_yest_zt.loc[:, "turnover"] = df_yest_zt["volume"]/(df_yest_zt["lt_mcap"]/df_yest_zt["close"]*1e6)
    df_yest_zt.loc[:, "fengdan"] = df_yest_zt["b1_v"] * df_yest_zt["b1_p"] *100 / df_yest_zt["lt_mcap"] / 1e8
    df_yest_zt.loc[:, "fengdan_money"] = df_yest_zt["b1_v"]*df_yest_zt["b1_p"]/1e6
    df_yest_zt.loc[:, "yest_lt_mcap"] = df_yest_zt["lt_mcap"]
    df_res = df_yest_zt[["fengdan", "fengdan_money", "yest_lt_mcap", "turnover"]].merge(df_today, how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_tick[["kaipan_money"]], how="left", left_index=True, right_index=True)
    df_tick_yest = stock.utils.symbol_util.get_tick_by_date(yest_str)
    df_res = df_res.merge(df_tick_yest[["zhangting_sell", "zhangting_min"]], how="inner", left_index=True, right_index=True)
    df_hist = filter_by_history(yest_str, df_res.index)
    df_res = df_res.merge(df_hist, how="inner", left_index=True, right_index=True)
    df_industry = get_industry()
    df_concept = get_concept()
    df_res = df_res.merge(df_industry, how="left", left_index=True, right_index=True)
    df_res = df_res.merge(df_concept, how="left", left_index=True, right_index=True)
    df_res = df_res # & (df_res.lt_mcap<100)]# & (df_res.zhangting_min>100)]

    columns = ["opengap", "fengdan_money", "kaipan_money", "lt_mcap", "industry"]
    print("========================== zhangting ==========================")
    print(df_res[columns].sort_values("kaipan_money", ascending=True))

def get_yizi(today):
    today_str = today.strftime("%Y-%m-%d")
    yest = get_last_trading_date(today)
    yest_str = yest.strftime("%Y-%m-%d")
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)
    df_yest.loc[:, "yest_chg"] = df_yest["chgperc"]
    df_yest.loc[:, "lowperc"] = df_yest["low"]/df_yest["yest_close"]-1
    df_res = df_yest[df_yest.lowperc>0.099]
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today.loc[:, "opengap"] = df_today.apply(lambda x: x["close"] if x["open"] == 0.0 else x["open"], axis=1)/df_today.yest_close - 1
    df_res = df_res.merge(df_today[["opengap"]], how="inner", left_index=True, right_index=True)
    df_res.loc[:, "fengdan"] = df_res["b1_v"] * df_res["b1_p"] *100 / df_res["lt_mcap"] / 1e8
    df_res.loc[:, "fengdan_money"] = df_res["b1_v"]*df_res["b1_p"]/1e6
    columns = ["opengap", "fengdan", "fengdan_money"]
    print("========================== yizi zhangting ==========================")
    print(df_res[columns])

if __name__ == "__main__":
    get_industry()
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    get_zhangting(today)
