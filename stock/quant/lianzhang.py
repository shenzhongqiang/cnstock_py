import sys
import datetime
import numpy as np
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd

date = None
if len(sys.argv) == 1:
    date = datetime.date.today().strftime("%Y-%m-%d")
else:
    date = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('sz000001')
date_idx = df_index.index.get_loc(date)
yest_date = df_index.index[date_idx-1].strftime("%Y-%m-%d")

df_res = pd.DataFrame(columns=["tmr_chg", "increase"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    idx = df.index.get_loc(date)
    min10 = np.min(df.iloc[idx-10:].close)
    increase = df.iloc[idx].close/min10 - 1
    tmr_chg = 0
    if idx+1 < len(df):
        tmr_chg = df.iloc[idx+1].close / df.iloc[idx].close - 1
    df_res.loc[exsymbol] = [tmr_chg, increase]

df_res = df_res.dropna(how="any")
pd.set_option('display.max_rows', None)
df_plt = df_res.sort_values("increase", ascending=True).tail(20)
print(df_plt)
