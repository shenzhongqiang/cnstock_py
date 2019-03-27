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

df_res = pd.DataFrame(columns=["tmr_chg", "yest_one", "opengap", "today_chg", "yest_chg", "vol_ratio", "increase10", "increase60"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    idx = df.index.get_loc(date)
    tmr_chg = 0
    if idx+1 < len(df):
        tmr_chg = df.iloc[idx+1].close/df.iloc[idx].close-1
    df_today = df.iloc[idx]
    df_yest = df.iloc[idx-1]
    today_chg = df_today.close / df_yest.close - 1
    yest_chg = df_yest.close / df.iloc[idx-2].close - 1
    yest_one = df_yest.high == df_yest.low
    opengap = df.iloc[idx].open / df.iloc[idx-1].close - 1
    vol_ratio = df_today.volume - df_yest.volume
    min10 = df[idx-10:].close.min()
    min60 = df[idx-60:].close.min()
    increase10 = df_today.close/min10-1
    increase60 = df_today.close/min60-1
    df_res.loc[exsymbol] = [tmr_chg, yest_one, opengap, today_chg, yest_chg, vol_ratio, increase10, increase60]

df_res = df_res.dropna(how="any")
pd.set_option('display.max_rows', None)

# get realtime data
df_realtime = get_realtime_by_date(yest_date)
df_realtime = df_realtime.loc[(df_realtime.lt_mcap > 0) & (df_realtime.volume > 0)].copy()
df_realtime.loc[:, "fengdan"] = df_realtime["b1_v"] * df_realtime["b1_p"] *100 / df_realtime["lt_mcap"] / 1e8
df_realtime.loc[:, "fengdan_money"] = df_realtime["b1_v"]*df_realtime["b1_p"]/1e6
df_realtime.loc[:, "fengdanvol"] = df_realtime["b1_v"] / df_realtime["volume"]

print("========== opengap ==========")
df_plt2 = df_res[df_res.yest_chg>0.095][df_res.opengap > 0.02][df_res.opengap<0.05]
df_plt2 = df_plt2.merge(df_realtime, how="inner", left_index=True, right_index=True)
columns = ["tmr_chg", "today_chg", "opengap", "fengdan", "fengdan_money", "increase60"]
print(df_plt2[columns].sort_values("fengdan", ascending=False))

