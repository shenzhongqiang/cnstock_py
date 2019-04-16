import datetime
import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData, get_tick_by_date
from stock.marketdata.storefactory import get_store
from config import store_type

def get_zhangting_minutes(df_tick):
    high = df_tick.price.max()
    df_tick.loc[:, "last_price"] = df_tick.price.shift(1)
    df_tick.loc[:, "last_time"] = df_tick["time"].shift(1)
    time_diff = df_tick.time.values - df_tick.last_time.values
    df_tick.loc[:, "time_diff"] = time_diff
    zhangting_time = df_tick[(df_tick.price==high) & (df_tick.last_price==high)].time_diff.sum()
    zhangting_min = zhangting_time / datetime.timedelta(minutes=1)
    return zhangting_min

if len(sys.argv) < 2:
    print("Usage: %s <sz002750>" % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
store = get_store(store_type)
df = store.get(exsymbol)
print("date\tfengdan\tfengdan_money\tsell_amount\tzhangting_min\tmoney_ratio")
for date in df.index[-10:]:
    date_str = date.strftime("%Y-%m-%d")
    df_rt = get_realtime_by_date(date_str)
    df_tick = get_tick_by_date(date_str)
    row_rt = df_rt.loc[exsymbol]
    row_tick = df_tick.loc[exsymbol]
    fengdan = row_rt["b1_v"] * row_rt["b1_p"]*100/row_rt["lt_mcap"]/1e8
    fengdan_money = row_rt["b1_v"] * row_rt["b1_p"]*100/1e8
    zhangting_min = row_tick["zhangting_min"]
    sell_amount = row_tick["sell_amount"]
    money_ratio = (fengdan_money+sell_amount)/row_rt["lt_mcap"]
    print("{}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}".format(date_str, fengdan, fengdan_money, sell_amount, zhangting_min, money_ratio))
