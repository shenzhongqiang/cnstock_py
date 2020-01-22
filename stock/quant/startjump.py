import argparse
import sys
from stock.marketdata.storefactory import get_store
from config import store_type
from stock.utils.symbol_util import load_concept, load_industry, get_realtime_by_date, get_stock_basics, get_stock_symbols, symbol_to_exsymbol
import numpy as np
import pandas as pd

def get_startjump_stocks(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    for exsymbol in exsymbols:
        df = store.get(exsymbol)
        df.loc[:, "ma10"] = df["close"].rolling(window=10).mean()
        if date not in df.index:
            continue
        idx = df.index.get_loc(date)
        df_recent = df.iloc[idx-10:idx+1].copy()
        df_recent.loc[:, "yest_close"] = df_recent.close.shift(1)
        df_recent.loc[:, "zt_price"] = df_recent.yest_close.apply(lambda x: round(x*1.1+1e-8, 2))
        df_recent.loc[:, "is_zhangting"] = (df_recent["zt_price"]-df_recent["close"])<1e-8
        is_zt_recent = df_recent["is_zhangting"].any()
        if not is_zt_recent:
            continue
        zt_recent_date = df_recent[df_recent.is_zhangting==True].index[-1]
        zt_recent_id = df_recent.index.get_loc(zt_recent_date)
        df_recent.loc[:, "above_ma10"] = df_recent["close"] >= df_recent["ma10"]
        all_above_ma10 = df_recent["above_ma10"].iloc[zt_recent_id:-1].all()
        if not all_above_ma10:
            continue
        s_today = df_recent.iloc[-1]
        dist_to_ma10 = s_today["close"] / s_today["ma10"] - 1
        if abs(dist_to_ma10) < 0.01:
            print(exsymbol)

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    parser = argparse.ArgumentParser()
    parser.add_argument('date', nargs='?', help='date')
    parser.add_argument('--stock', dest='stock', action='store_true', help='list stocks')
    opt = parser.parse_args()
    today = None
    if opt.date is None:
        today = pd.datetime.today().strftime("%Y-%m-%d")
    else:
        today = opt.date

    get_startjump_stocks(today)
