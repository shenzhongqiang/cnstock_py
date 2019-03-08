import pandas
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from config import store_type
from wxpy import Bot

def filter_by_history():
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    result = []
    for exsymbol in exsymbols:
        df_stock = store.get(exsymbol)
        result.append(exsymbol)
    return result

df = stock.utils.symbol_util.get_today_all()
df = df[df.close > 0]
# chgperc between -0.03 and 0.02
df_res = df[df.chgperc >= -3][df.chgperc <= 3]
print(df_res)

pandas.set_option('display.max_rows', None)
# 10% stock
df_part = df[df.lt_mcap > 0][df.chgperc > 9.9][df.a1_v == 0]
df_part["fengdan"] = df_part["b1_v"] * df_part["b1_p"] *100 / df_part["lt_mcap"] / 1e8

exsymbols = filter_by_history()
df_part = df_part[df_part.index.isin(exsymbols)]
print(df_part[["fengdan"]].sort_values("fengdan", ascending=False))

