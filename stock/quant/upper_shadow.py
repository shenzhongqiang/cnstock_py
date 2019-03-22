import sys
from stock.utils.symbol_util import get_stock_symbols
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd

if len(sys.argv) == 1:
    print("Usage: %s <date>" % (sys.argv[0]))
    sys.exit(1)

date = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')

df_res = pd.DataFrame(columns=["body", "yest_chg", "highperc", "increase", "closeup", "past_zt"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    idx = df.index.get_loc(date)
    df.loc[:, "highperc"] = df.high / df.close.shift(1) - 1
    df.loc[:, "closeperc"] = df.close / df.close.shift(1) - 1
    df.loc[:, "past_zt"] = df.highperc.rolling(window=30).max()
    df.loc[:, "close60"] = df.close.rolling(window=60).min()
    df.loc[:, "increase"] = df.close / df.close60 - 1
    df_today = df.iloc[idx]
    df_yest = df.iloc[idx-1]
    yest_chg = df_yest.closeperc
    upper = max(df_today.open, df_today.close)
    body = abs(df_today.close-df_today.open)/df_yest.close
    highperc = df_today.high / df_yest.close - 1
    increase = df_today.increase
    closeup = df_today.close > df_today.open and df_today.open > df_yest.close
    past_zt = df_today.past_zt > 0.095
    df_res.loc[exsymbol] = [body, yest_chg, highperc, increase, closeup, past_zt]

df_res = df_res.dropna(how="any")
df_plt = df_res[df_res.highperc>0.04][df_res.highperc<0.06][df_res.body<0.02][df_res.body>-0.02][df_res.closeup==True].sort_values("increase", ascending=False)
pd.set_option('display.max_rows', None)
print(df_plt)
