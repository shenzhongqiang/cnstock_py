import os
import sys
import datetime
import tushare as ts
import pandas as pd
from pandas.tseries.offsets import BDay
from stock.globalvar import *

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <datetime> <symbol>" % sys.argv[0])
        sys.exit(1)

    datetime_str = sys.argv[1]
    symbol = sys.argv[2]
    dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    today_str = dt.strftime("%Y-%m-%d")
    yest = get_last_trading_date(dt)
    yest_str = yest.strftime("%Y-%m-%d")
    time_str = dt.strftime("%H:%M:%S")
    df_yest = ts.get_tick_data(symbol, date=yest_str, src='tt')
    df_yest.loc[:, "time"] = pd.to_datetime(yest_str + ' ' + df_yest["time"], format="%Y-%m-%d %H:%M:%S")
    ratio = df_yest[df_yest.time<= yest_str + ' ' + time_str].volume.sum() / \
        df_yest.volume.sum()
    df_today = ts.get_tick_data(symbol, date=today_str, src='tt')
    df_today.loc[:, "time"] = pd.to_datetime(today_str + ' ' + df_today["time"], format="%Y-%m-%d %H:%M:%S")
    volume = df_today[df_today.time<=today_str+' '+time_str].volume.sum()
    print(volume)
    pred_volume = df_today[df_today.time<=today_str + ' ' + time_str].volume.sum() / ratio
    real_volume = df_today.volume.sum()
    yest_volume = df_yest.volume.sum()
    print("pred\treal\tyest")
    print(int(pred_volume), real_volume, yest_volume)
