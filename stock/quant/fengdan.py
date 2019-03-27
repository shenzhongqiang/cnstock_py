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
print("date\tfengdan\tfengdan_money\tpaodan_money")
for date in df.index:
    try:
        date_str = date.strftime("%Y-%m-%d")
        df_rt = get_realtime_by_date(date_str)
        row = df_rt.loc[exsymbol]
        fengdan = row["b1_v"] * row["b1_p"]*100/row["lt_mcap"]/1e8
        fengdan_money = row["b1_v"] * row["b1_p"]*100/1e8
        paodan_money = row["a1_v"] * row["a1_p"]*100/1e8
        print("{}\t{:.5f}\t{:.5f}\t{:.5f}".format(date_str, fengdan, fengdan_money, paodan_money))
    except NoRealtimeData as e:
        continue
