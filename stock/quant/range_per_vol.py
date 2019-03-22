import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData
from stock.lib.finance import load_stock_basics
from stock.marketdata.storefactory import get_store
from config import store_type

if len(sys.argv) < 2:
    print("Usage: %s <sz002750>" % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
store = get_store(store_type)
df_basics = load_stock_basics()
outstanding = df_basics.loc[exsymbol, "outstanding"]
df = store.get(exsymbol)
for date in df.index:
    try:
        date_str = date.strftime("%Y-%m-%d")
        df_rt = get_realtime_by_date(date_str)
        row = df_rt.loc[exsymbol]
        fengdan = row["b1_v"] * row["b1_p"]*100/row["lt_mcap"]/1e8
        dt_fengdan = row["a1_v"] * row["a1_p"]*100/row["lt_mcap"]/1e8
        print(date_str, fengdan, dt_fengdan)
    except NoRealtimeData as e:
        continue

df["lt_mcap"] = outstanding * df.close
df["chgperc"] = df.close / df.close.shift(1) - 1
df["chg_per_vol"] = df.chgperc / (df.volume/outstanding/1e6)
df["range_per_vol"] = (df.high/df.low-1) / (df.volume/outstanding/1e6)
df["body_per_vol"] = (df.close/df.open-1) / (df.volume/outstanding/1e6)
df_plt = df[["chgperc", "chg_per_vol", "range_per_vol", "body_per_vol"]]
print(df_plt[-30:])
