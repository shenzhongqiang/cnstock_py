import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols
from stock.lib.finance import load_stock_basics
from stock.marketdata.storefactory import get_store
from config import store_type

if len(sys.argv) < 2:
    print("Usage: %s <2019-03-13>" % sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
store = get_store(store_type)

df_basics = load_stock_basics()
exsymbols = store.get_stock_exsymbols()
columns = ["exsymbol", "chgperc", "chg_per_vol", "range_per_vol", "body_per_vol", "lt_mcap", "highperc"]
df_date = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 2:
        continue
    if date not in df.index:
        continue

    outstanding = df_basics.loc[exsymbol, "outstanding"]
    if outstanding == 0:
        continue
    idx = df.index.get_loc(date)
    close = df.iloc[idx].close
    high = df.iloc[idx].high
    openp = df.iloc[idx].open
    low = df.iloc[idx].low
    close1 = df.iloc[idx-1].close
    chgperc = close/close1 - 1
    highperc = high/close1 - 1
    volume = df.iloc[idx].volume
    lt_mcap = outstanding * close

    if volume == 0:
        continue

    chg_per_vol = chgperc / (volume/outstanding/1e6)
    range_per_vol = (high/low-1) / (volume/outstanding/1e6)
    body_per_vol = (close/openp-1) / (volume/outstanding/1e6)
    df_date.loc[exsymbol] = [exsymbol, chgperc, chg_per_vol, range_per_vol, body_per_vol, lt_mcap, highperc]

df_date.dropna(how="any", inplace=True)
df_plt = df_date[df_date.highperc>0.099].sort_values("chgperc", ascending=False).tail(20)
print(df_plt)
