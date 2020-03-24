import datetime
import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData, get_tick_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts
import numpy as np

if len(sys.argv) < 2:
    print("Usage: %s <sz002750>" % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
store = get_store(store_type)
df = store.get(exsymbol)
df["chg"] = df.close / df.close.shift(1) - 1
print("date\t\tchg\tfengdan\tfengdan_money\tkaipan_money\tzhangting_sell")
for date in df.index[-5:]:
    date_str = date.strftime("%Y-%m-%d")
    fengdan = 0
    fengdan_money = 0
    turnover = 0
    try:
        df_rt = get_realtime_by_date(date_str)
        df_tick = get_tick_by_date(date_str)
        row_rt = df_rt.loc[exsymbol]
        row_tick = df_tick.loc[exsymbol]
        fengdan = row_rt["b1_v"] * row_rt["b1_p"]*100/row_rt["lt_mcap"]/1e8
        fengdan_money = row_rt["b1_v"] * row_rt["b1_p"]*100/1e8
        zhangting_sell = row_tick["zhangting_sell"]
        turnover = row_rt["volume"]/(row_rt["lt_mcap"]/row_rt["close"]*1e6)
    except Exception:
        pass

    chg = df.loc[date_str].chg * 100
    df_tick = get_tick_by_date(date_str)
    row_tick = df_tick.loc[exsymbol]
    kaipan_money = row_tick["kaipan_money"]
    symbol = exsymbol[2:]
    print("{}\t{:.2f}\t{:.5f}\t{:.3f}\t{:.0f}\t{:.3f}".format(date_str, chg, fengdan, fengdan_money, kaipan_money, zhangting_sell))
