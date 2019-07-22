import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from stock.globalvar import *
from config import store_type
import tushare as ts

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

def get_zhangting(today):
    today_str = today.strftime("%Y-%m-%d")
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)

    yest = get_last_trading_date(today)
    yest_str = yest.strftime("%Y-%m-%d")
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)

    df_yest["zt_price"] = np.round(df_yest["yest_close"] * 1.1, 2)
    df_yest["diff2zt"] = df_yest["zt_price"] - df_yest["close"]
    df_zt = df_yest[(df_yest.diff2zt<1e-3) & (df_yest.lt_mcap>0) & (df_yest.volume>0)].copy()
    df_today["range"] = (df_today["high"] - df_today["low"]) / df_today["yest_close"]
    df_today["body"] = np.absolute((df_today["open"]-df_today["close"])/df_today["yest_close"])
    df_zt = df_zt.merge(df_today[["range", "body"]], how="left", left_index=True, right_index=True)
    df_zt.loc[:, "turnover"] = df_zt["volume"]/(df_zt["lt_mcap"]/df_zt["close"]*1e6)
    df_zt.loc[:, "fengdan"] = df_zt["b1_v"] * df_zt["b1_p"] *100 / df_zt["lt_mcap"] / 1e8
    df_zt.loc[:, "fengdan_money"] = df_zt["b1_v"]*df_zt["b1_p"]/1e6
    df_industry = get_industry()
    df_res = df_zt.merge(df_industry, how="left", left_index=True, right_index=True)
    columns = ["fengdan", "fengdan_money", "lt_mcap", "turnover", "range", "body", "industry"]
    print("========================== zhangting ==========================")
    print(df_res[columns].sort_values("range", ascending=True))


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    get_zhangting(today)
