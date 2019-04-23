import sys
import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from config import store_type


pd.set_option('display.max_rows', None)

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

def main(today):
    yest = today - BDay(1)
    today_str = today.strftime("%Y-%m-%d")
    yest_str = yest.strftime("%Y-%m-%d")

    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today.loc[:, "today_chgperc"] = df_today["chgperc"]
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)[["chgperc"]]
    df_yest.loc[:, "yest_chgperc"] = df_yest["chgperc"]
    df_tick = stock.utils.symbol_util.get_tick_by_date(today_str)
    df_tick.loc[:, "kaipan_money"] = df_tick["kaipan_money"]/1e8
    df_today["opengap"] = df_today.apply(lambda x: x["close"] if x["open"] == 0.0 else x["open"], axis=1)/df_today.yest_close - 1
    df_res = df_today.merge(df_tick, how="left", left_index=True, right_index=True)
    df_res.loc[:, "kaipan"] = df_res.kaipan_money/df_res.lt_mcap
    df_res = df_res[(df_res.lt_mcap<300) & (df_res.opengap<0.03) & (df_res.opengap>0) & (df_res.kaipan_money>0.1)].copy()
    df_res = df_res.merge(df_yest, how="inner", left_index=True, right_index=True)
    df_res = df_res[(df_res.yest_chgperc>0)]
    df_hist = filter_by_history(yest_str, df_res.index)
    df_res = df_res.merge(df_hist, how="inner", left_index=True, right_index=True)
    columns = ["opengap", "increase5", "lt_mcap", "mcap", "kaipan_money", "kaipan", "yest_chgperc", "today_chgperc"]
    print(df_res[columns].sort_values("increase5", ascending=True).tail(20))
    print(df_res[columns].sort_values("kaipan", ascending=True).tail(50))

if __name__ == "__main__":
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")
    main(today)
