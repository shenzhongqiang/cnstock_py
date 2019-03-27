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

df_res = pd.DataFrame(columns=["body", "tmr_chg", "yest_one", "opengap", "today_chg", "yest_chg", "upper", "lower", "vol_ratio", "highperc", "increase10", "increase60", "closeup"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 200:
        continue
    if date not in df.index:
        continue
    idx = df.index.get_loc(date)
    df.loc[:, "closeperc"] = df.close / df.close.shift(1) - 1
    df.loc[:, "close10"] = df.close.rolling(window=10).min()
    df.loc[:, "close60"] = df.close.rolling(window=60).min()
    df.loc[:, "increase10"] = df.close / df.close10 - 1
    df.loc[:, "increase60"] = df.close / df.close60 - 1
    #if idx+1 >= len(df):
    #    continue
    #df_tmr = df.iloc[idx+1]
    df_today = df.iloc[idx]
    df_yest = df.iloc[idx-1]
    today_chg = df_today.closeperc
    yest_chg = df_yest.closeperc
    yest_one = df_yest.high == df_yest.low
    tmr_chg = 0 #df_tmr.closeperc
    opengap = df.iloc[idx].open / df.iloc[idx-1].close - 1
    upper_edge = max(df_today.open, df_today.close)
    lower_edge = min(df_today.open, df_today.close)
    body = (df_today.close-df_today.open)/df_yest.close
    upper = (df_today.high - upper_edge)/df_yest.close
    lower = (lower_edge - df_today.low)/df_yest.close
    vol_ratio = df_today.volume - df_yest.volume
    highperc = df_today.high / df_yest.close - 1
    increase10 = df_today.increase10
    increase60 = df_today.increase60
    closeup = df_today.close > df_today.open
    df_res.loc[exsymbol] = [body, tmr_chg, yest_one, opengap, today_chg, yest_chg, upper, lower, vol_ratio, highperc, increase10, increase60, closeup]

df_res = df_res.dropna(how="any")
pd.set_option('display.max_rows', None)

# get realtime data
df_realtime = get_realtime_by_date(yest_date)
df_realtime = df_realtime.loc[(df_realtime.lt_mcap > 0) & (df_realtime.volume > 0)].copy()
df_realtime.loc[:, "fengdan"] = df_realtime["b1_v"] * df_realtime["b1_p"] *100 / df_realtime["lt_mcap"] / 1e8
df_realtime.loc[:, "fengdan_money"] = df_realtime["b1_v"]*df_realtime["b1_p"]/1e6
df_realtime.loc[:, "fengdanvol"] = df_realtime["b1_v"] / df_realtime["volume"]

print("========== small body ==========")
df_plt = df_res[df_res.highperc>0.04][df_res.highperc<0.099][df_res.body<0.02][df_res.body>-0.02][df_res.closeup==True].sort_values("increase60", ascending=False)
print(df_plt)
print("========== yest zhangting ==========")
df_plt2 = df_res[df_res.yest_chg>0.08][df_res.upper>0.03][df_res.lower<0.03][df_res.body>-0.02]
df_plt2 = df_plt2.merge(df_realtime, how="inner", left_index=True, right_index=True)
print(df_plt2[["tmr_chg", "today_chg", "highperc", "upper", "lower", "fengdan", "fengdan_money"]])

print("========== opengap ==========")
df_plt2 = df_res[df_res.yest_chg>0.095][df_res.opengap > 0.02]
df_plt2 = df_plt2.merge(df_realtime, how="inner", left_index=True, right_index=True)
columns = ["tmr_chg", "today_chg", "opengap", "fengdan", "fengdan_money", "increase60"]
print(df_plt2[columns].sort_values("fengdan", ascending=False))
