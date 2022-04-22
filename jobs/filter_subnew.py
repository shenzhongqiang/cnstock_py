import sys
import numpy as np
import pandas as pd
import stock.utils.symbol_util
from stock.globalvar import *
from stock.marketdata.storefactory import get_store
from config import store_type
from pandas.tseries.offsets import BDay
import tushare as ts
from stock.utils.calc_price import get_zt_price


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    store = get_store(store_type)
    result = []
    df = pd.DataFrame(columns=["days"])
    symbols = stock.utils.symbol_util.get_stock_symbols()
    for symbol in symbols:
        if not store.has(symbol):
            continue
        df_stock = store.get(symbol)
        df_past = df_stock.loc[:today]
        if len(df_past) >10 or len(df_past) == 0:
            continue
        df.loc[symbol] = [len(df_past)]
    print(df.sort_values(["days"]))
