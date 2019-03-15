import sys
import datetime
import os
import numpy as np
import pandas as pd
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from config import store_type
import matplotlib.pyplot as plt


date = sys.argv[1]
store = get_store(store_type)
df_basics = load_stock_basics()
exsymbols = store.get_stock_exsymbols()
df_date = pd.DataFrame(columns=["exsymbol", "huanshoulv", "increase"])
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 400:
        continue
    outstanding = df_basics.loc[exsymbol, "outstanding"]
    df_past = df.loc[:date]
    df_past["low60"] = df_past.low.rolling(window=60).min()
    df_past["increase"] = df_past.close / df_past.low60 - 1
    huanshoulv = df_past.iloc[-1].volume * 100/outstanding/1e8
    df_date.loc[len(df_date)] = [exsymbol, huanshoulv, df_past.iloc[-1].increase]

df_date.dropna(how="any", inplace=True)
df_date["score"] = df_date.huanshoulv / df_date.increase
df_top = df_date[df_date.huanshoulv >0.1].sort_values(["score"]).tail(100)
print(df_top)
