import datetime
import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData, get_tick_by_date
from stock.marketdata.storefactory import get_store
from config import store_type

if len(sys.argv) < 2:
    print("Usage: %s <sz002750>" % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
store = get_store(store_type)
df = store.get(exsymbol)
print("date\tfengdan\tfengdan_money\tzhangting_min\tzhangting_force\tzhangting_sell\tkaipan_money")
for date in df.index[-15:]:
    date_str = date.strftime("%Y-%m-%d")
    df_rt = get_realtime_by_date(date_str)
    df_tick = get_tick_by_date(date_str)
    row_rt = df_rt.loc[exsymbol]
    row_tick = df_tick.loc[exsymbol]
    fengdan = row_rt["b1_v"] * row_rt["b1_p"]*100/row_rt["lt_mcap"]/1e8
    fengdan_money = row_rt["b1_v"] * row_rt["b1_p"]*100/1e8
    zhangting_min = row_tick["zhangting_min"]
    zhangting_force = row_tick["zhangting_force"]
    zhangting_sell = row_tick["zhangting_sell"]
    kaipan_money = row_tick["kaipan_money"]
    print("{}\t{:.5f}\t{:.5f}\t{:.5g}\t{:.5f}\t{:.5f}\t{:.0f}".format(date_str, fengdan, fengdan_money, zhangting_min, zhangting_force, zhangting_sell, kaipan_money))
