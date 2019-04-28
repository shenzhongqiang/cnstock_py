import re
import asyncio
import aiohttp
import os
import sys
import datetime
import tushare as ts
import pandas as pd
from stock.globalvar import TICK_DIR
from jobs.get_tick import init, run


def filter_open(date):
    folder = TICK_DIR["stock"]
    files = os.listdir(folder)
    df_res = pd.DataFrame(columns=["up_speed", "chg", "kaipan_money", "opengap"])
    tasks = []
    for filename in files:
        exsymbol = filename
        filepath = os.path.join(folder, exsymbol)
        if not os.path.isfile(filepath):
            continue
        df = pd.read_csv(filepath, sep='\t', header=0, names=['time', 'price', 'change', 'volume', 'amount', 'type'])
        df_open = df.iloc[:2]
        if len(df_open) == 0:
            continue
        df.loc[:, "time"] = pd.to_datetime(date + ' ' + df["time"], format="%Y-%m-%d %H:%M:%S")
        open_dt = datetime.datetime.strptime(date+" 09:30:00", "%Y-%m-%d %H:%M:%S")
        if df.iloc[0].time >= open_dt:
            continue
        yest_close = df.iloc[0].price - df.iloc[0].change
        opengap = df.iloc[0].price / yest_close - 1
        kaipan_money = 0
        kaipan_money = df.iloc[0].amount
        chg = df_open.iloc[1].price / yest_close - 1
        up_speed = df_open.iloc[1].price/df_open.iloc[0].price - 1
        if opengap > 0.03 and chg < 0.08:
            df_res.loc[exsymbol] = [up_speed, chg, kaipan_money, opengap]
    return df_res

def filter_speed(date):
    folder = TICK_DIR["stock"]
    files = os.listdir(folder)
    df_res = pd.DataFrame(columns=["up_speed", "down_speed", "chg", "kaipan_money", "opengap"])
    tasks = []
    for filename in files:
        exsymbol = filename
        filepath = os.path.join(folder, exsymbol)
        if not os.path.isfile(filepath):
            continue
        df = pd.read_csv(filepath, sep='\t', header=0, names=['time', 'price', 'change', 'volume', 'amount', 'type'])
        df.loc[:, "time"] = pd.to_datetime(date + ' ' + df["time"], format="%Y-%m-%d %H:%M:%S")
        df_5min = df[(df.time<=date+" 09:35:00") & (df.time>=date+" 09:30:00")]
        if len(df_5min) == 0:
            continue
        yest_close = df.iloc[0].price - df.iloc[0].change
        opengap = df.iloc[0].price / yest_close - 1
        kaipan_money = 0
        open_dt = datetime.datetime.strptime(date+" 09:30:00", "%Y-%m-%d %H:%M:%S")
        if df.iloc[0].time < open_dt:
            kaipan_money = df.iloc[0].amount
        #df1.loc[:, "time_diff"] = (df1.time-df1.time.shift(20)) / datetime.timedelta(seconds=1)
        #df1.loc[:, "price_diff"] = df1.price-df1.price.shift(20)
        #df1.loc[:, "speed"] = df1.price_diff/yest_close/df1.time_diff
        idxmin = df_5min.price.idxmin()
        idxmax = df_5min.price.idxmax()
        min_time = df_5min.loc[idxmin].time
        max_time = df_5min.loc[idxmax].time
        dtime = (df_5min.iloc[-1].time - min_time) / datetime.timedelta(minutes=1)
        dprice = df_5min.iloc[-1].price - df_5min.loc[idxmin].price
        up_speed  = dprice/yest_close
        dtime = (df_5min.iloc[-1].time - max_time) / datetime.timedelta(minutes=1)
        dprice = df_5min.iloc[-1].price - df_5min.loc[idxmax].price
        down_speed = dprice/yest_close
        chg = df_5min.iloc[-1].price / yest_close - 1
        #speed = df_5min.iloc[-1].speed
        #chg = df_5min.iloc[-1].price/yest_close-1
        if up_speed > 0.03 and down_speed == 0:
            df_res.loc[exsymbol] = [up_speed, down_speed, chg, kaipan_money, opengap]
    return df_res

def filter_close(date):
    folder = TICK_DIR["stock"]
    files = os.listdir(folder)
    df_res = pd.DataFrame(columns=["up_speed", "down_speed", "chg", "amount", "opengap"])
    tasks = []
    for filename in files:
        exsymbol = filename
        filepath = os.path.join(folder, exsymbol)
        if not os.path.isfile(filepath):
            continue
        df = pd.read_csv(filepath, sep='\t', header=0, names=['time', 'price', 'change', 'volume', 'amount', 'type'])
        df.loc[:, "time"] = pd.to_datetime(date + ' ' + df["time"], format="%Y-%m-%d %H:%M:%S")
        df_5min = df[(df.time<=date+" 14:55:00") & (df.time>=date+" 14:45:00")]
        if len(df_5min) == 0:
            continue
        yest_close = df.iloc[0].price - df.iloc[0].change
        opengap = df.iloc[0].price / yest_close - 1
        idxmin = df_5min.price.idxmin()
        idxmax = df_5min.price.idxmax()
        min_time = df_5min.loc[idxmin].time
        max_time = df_5min.loc[idxmax].time
        dtime = (df_5min.iloc[-1].time - min_time) / datetime.timedelta(minutes=1)
        dprice = df_5min.iloc[-1].price - df_5min.loc[idxmin].price
        amount = df_5min.loc[idxmin:].amount.sum()
        up_speed  = dprice/yest_close
        dtime = (df_5min.iloc[-1].time - max_time) / datetime.timedelta(minutes=1)
        dprice = df_5min.iloc[-1].price - df_5min.loc[idxmax].price
        down_speed = dprice/yest_close
        chg = df_5min.iloc[-1].price / yest_close - 1
        if up_speed > 0.02 and down_speed == 0:
            df_res.loc[exsymbol] = [up_speed, down_speed, chg, amount, opengap]
    return df_res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <date>".format(sys.argv(0)))
        sys.exit(1)

    pd.set_option('display.max_rows', None)
    date = sys.argv[1]

    #df_res = filter_speed(date)
    df_res = filter_close(date)
    print(df_res.sort_values("up_speed"))
