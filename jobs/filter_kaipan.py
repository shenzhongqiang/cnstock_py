import sys
import datetime
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from config import store_type


pd.set_option('display.max_rows', None)

today = None
if len(sys.argv) == 1:
    today = pd.datetime.today()
else:
    today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

yest = today - BDay(1)
today_str = today.strftime("%Y-%m-%d")
yest_str = yest.strftime("%Y-%m-%d")

df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
df_tick = stock.utils.symbol_util.get_tick_by_date(today_str)
df_tick.loc[:, "kaipan_money"] = df_tick["kaipan_money"]/1e8
df_today["opengap"] = df_today.apply(lambda x: x["close"] if x["open"] == 0.0 else x["open"], axis=1)/df_today.yest_close - 1
df_res = df_today.merge(df_tick, how="left", left_index=True, right_index=True)
df_res.loc[:, "kaipan"] = df_res.kaipan_money/df_res.lt_mcap
df_res = df_res[(df_res.lt_mcap<100)].copy()
columns = ["opengap", "lt_mcap", "mcap", "kaipan_money", "kaipan"]
print(df_res[columns].sort_values("kaipan", ascending=True).tail(10))
print(df_res[columns].sort_values("kaipan_money", ascending=True).tail(10))
