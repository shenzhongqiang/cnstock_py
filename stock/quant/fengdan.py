import datetime
import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData
from stock.lib.finance import load_stock_basics
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts

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
df_basics = load_stock_basics()
outstanding = df_basics.loc[exsymbol, "outstanding"]
df = store.get(exsymbol)
print("date\tfengdan\tfengdan_money\tsell_amount\tzhangting_min")
for date in df.index:
    try:
        date_str = date.strftime("%Y-%m-%d")
        df_rt = get_realtime_by_date(date_str)
        row = df_rt.loc[exsymbol]
        fengdan = row["b1_v"] * row["b1_p"]*100/row["lt_mcap"]/1e8
        fengdan_money = row["b1_v"] * row["b1_p"]*100/1e8
        df_tick = ts.get_tick_data(exsymbol, date=date_str, src="tt")
        df_tick.loc[:, "time"] = pd.to_datetime(df_tick["time"])
        df_tick1 = df_tick[df_tick.time<="11:30:00"]
        df_tick2 = df_tick[df_tick.time>="13:00:00"]
        zhangting1_min = get_zhangting_minutes(df_tick1)
        zhangting2_min = get_zhangting_minutes(df_tick2)
        zhangting_min = zhangting1_min + zhangting2_min
        high = df_tick.price.max()
        sell_amount = df_tick[df_tick.price==high].volume.sum()*high/1e6
        print("{}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}".format(date_str, fengdan, fengdan_money, sell_amount, zhangting_min))
    except NoRealtimeData as e:
        continue
