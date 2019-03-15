import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols
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
df["lt_mcap"] = outstanding * df.close
df["chgperc"] = df.close / df.close.shift(1) - 1
df["chg_per_vol"] = df.chgperc / (df.volume/outstanding/1e6)
df["range_per_vol"] = (df.high/df.low-1) / (df.volume/outstanding/1e6)
df["body_per_vol"] = (df.close/df.open-1) / (df.volume/outstanding/1e6)
df_plt = df[["chgperc", "chg_per_vol", "range_per_vol", "body_per_vol"]]
print(df_plt[-30:])
