import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--recent", type=int, default=10, help="30")
    parser.add_argument("--end", type=str, default=None, help="e.g. 2022-01-04")
    args = parser.parse_args()

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    today = None
    if args.end is None:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(args.end, "%Y-%m-%d")

    store = get_store(store_type)
    result = []
    df = pd.DataFrame(columns=["days"])
    symbols = stock.utils.symbol_util.get_stock_symbols()
    for symbol in symbols:
        if not store.has(symbol):
            continue
        df_stock = store.get(symbol)
        df_past = df_stock.loc[:today]
        if len(df_past) > args.recent or len(df_past) == 0:
            continue
        df.loc[symbol] = [len(df_past)]
    print(df.sort_values(["days"]))
