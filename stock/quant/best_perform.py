import numpy as np
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from config import store_type

pd.set_option('display.max_rows', None)
store = get_store(store_type)
def get_equity_value(exsymbols, date):
    closes = []
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        if date in df.index:
            closes.append(df.loc[date].close)
        else:
            close = df.loc[:date].iloc[-1].close
            closes.append(close)
    return np.mean(closes)

exsymbols = store.get_stock_exsymbols()
columns = ["exsymbol", "profit"]
df_date = pd.DataFrame(columns=columns)
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 400:
        continue
    close_min = df.close.iloc[-30:].min()
    profit = df.iloc[-1].close / close_min - 1
    df_date.loc[len(df_date)] = [exsymbol, profit]
df_date.dropna(how="any", inplace=True)
df_top = df_date.sort_values(["profit"]).tail(10)
df_bottom = df_date.sort_values(["profit"]).head(100)

print(df_top)
