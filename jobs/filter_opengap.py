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
df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)
df_yest_zt = df_yest[(df_yest.chgperc>9.5) & (df_yest.lt_mcap>0) & (df_yest.volume>0)].copy()
df_yest_zt.loc[:, "fengdan"] = df_yest_zt["b1_v"] * df_yest_zt["b1_p"] *100 / df_yest_zt["lt_mcap"] / 1e8
df_yest_zt.loc[:, "fengdan_money"] = df_yest_zt["b1_v"]*df_yest_zt["b1_p"]/1e6
df_res = df_yest_zt[["fengdan", "fengdan_money"]].merge(df_today, how="inner", left_index=True, right_index=True)
df_res = df_res.merge(df_tick, how="left", left_index=True, right_index=True)
df_res.loc[:, "kaipan_ratio"] = df_res["kaipan_money"]/df_res["fengdan_money"]

df_res1 = df_res[df_res.opengap>=0.02]
df_res2 = df_res[df_res.opengap<0.02]

columns = ["opengap", "fengdan", "fengdan_money", "lt_mcap", "mcap", "kaipan_money", "kaipan_ratio"]
print(df_res1[columns].sort_values("kaipan_ratio", ascending=True))
print(df_res2[columns].sort_values("kaipan_ratio", ascending=True))
