import sys
import datetime
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

df_res = pd.DataFrame(columns=["tmr_chg", "opengap", "increase60", "fengdan1"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    idx = df.index.get_loc(date)
    if df.iloc[idx].close / df.iloc[idx-10].close  -1 > 0.5:
        df.loc[:, "close60"] = df.close.rolling(window=60).min()
        df.loc[:, "increase60"] = df.close / df.close60 - 1
        increase60 = df.iloc[idx].increase60
        opengap = df.iloc[idx-4].open / df.iloc[idx-5].close - 1
        tmr_chg = 0
        if idx+1 < len(df):
            tmr_chg = df.iloc[idx+1].close / df.iloc[idx].close - 1
        df_res.loc[exsymbol] = [tmr_chg, opengap, increase60, 0]

df_res = df_res.dropna(how="any")
pd.set_option('display.max_rows', None)

# get realtime data
df_realtime = get_realtime_by_date(yest_date)
df_realtime = df_realtime.loc[(df_realtime.lt_mcap > 0) & (df_realtime.volume > 0)].copy()
df_realtime.loc[:, "fengdan"] = df_realtime["b1_v"] * df_realtime["b1_p"] *100 / df_realtime["lt_mcap"] / 1e8
df_realtime.loc[:, "fengdan_money"] = df_realtime["b1_v"]*df_realtime["b1_p"]/1e6
df_realtime.loc[:, "fengdanvol"] = df_realtime["b1_v"] / df_realtime["volume"]

df_plt = df_res.sort_values("increase60", ascending=True)
print(df_plt)
