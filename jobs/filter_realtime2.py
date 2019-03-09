import sys
import pandas as pd
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from config import store_type
from wxpy import Bot

def filter_by_history(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    result = []
    df = pd.DataFrame(columns=["increase"], index=exsymbols)
    for exsymbol in exsymbols:
        df_stock = store.get(exsymbol)
        df_stock = df_stock.loc[:date]
        df_stock["close30"] = df_stock.close.rolling(window=60).min()
        df_stock["increase"] = df_stock.close / df_stock.close30 - 1
        df.at[exsymbol, "increase"] = df_stock.iloc[-1].increase
    return df

if len(sys.argv) < 2:
    print("Usage: %s <2019-03-08>" % sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
df = stock.utils.symbol_util.get_realtime_by_date(date)
df = df[df.close > 0]
# chgperc between -0.03 and 0.02
df_res = df[df.chgperc >= -3][df.chgperc <= 3]
print(df_res)

pd.set_option('display.max_rows', None)
# 10% stock
df_part = df[df.lt_mcap > 0][df.chgperc > 9.9][df.a1_v == 0]
df_part["fengdan"] = df_part["b1_v"] * df_part["b1_p"] *100 / df_part["lt_mcap"] / 1e8
df_part["fengdanvol"] = df_part["b1_v"] / df_part["volume"]
df_hist = filter_by_history(date)
df_res = df_part.merge(df_hist, how="inner", left_index=True, right_index=True)
df_res = df_res[df_res.increase < 0.5]
print(df_res[["fengdan", "fengdanvol", "increase"]].sort_values("fengdan", ascending=False))
