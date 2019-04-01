import sys
import datetime
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, exsymbol_to_symbol, get_kaipan, NoTickData
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

df_res = pd.DataFrame(columns=["time", "open", "openvol", "open_money"])
for exsymbol in exsymbols:
    try:
        bar = get_kaipan(exsymbol)
        open_money = bar.price * bar.volume * 100
        df_res.loc[exsymbol] = [bar.name, bar.price, bar.volume, open_money]
    except NoTickData as e:
        continue

print(df_res.sort_values("open_money", ascending=True).tail(100))
