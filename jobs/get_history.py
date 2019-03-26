#!/usr/bin/python
import pandas as pd
from tqdm import tqdm, trange
import os.path
from multiprocessing import Pool
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import HIST_DIR
from stock.marketdata.storefactory import get_store
import tushare as ts
import jobs.get_realtime

# check if directory exists, if not create directory
def init():
    stock_dir = HIST_DIR['stock']
    if not os.path.isdir(stock_dir):
        os.makedirs(stock_dir)

def add_today_data(exsymbol, df, df_realtime, date):
    if exsymbol not in df_realtime.index:
        return
    if date in df.date.values:
        return
    today_bar = df_realtime.loc[exsymbol]
    symbol = stock.utils.symbol_util.exsymbol_to_symbol(exsymbol)
    idx = df.index[-1] + 1
    df.loc[idx] = [date,
        today_bar["open"],
        today_bar["close"],
        today_bar["high"],
        today_bar["low"],
        today_bar["volume"],
        symbol]

def download_stock_history(data, df_realtime, date):
    try:
        symbol = data["symbol"]
        is_index = data["is_index"]
        df = ts.get_k_data(symbol, index=is_index, start="2015-01-01")
        if df.empty:
            return
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, symbol)
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol, is_index)
        add_today_data(exsymbol, df, df_realtime, date)
        #redis_store = get_store("redis_store")
        #redis_store.save(exsymbol, df)
        file_store = get_store("file_store")
        file_store.save(exsymbol, df)
    except Exception as e:
        print("error getting history due to %s" % str(e))
        #import traceback
        #traceback.print_exc()

if __name__ == "__main__":
    init()
    pool = Pool(20)

    # download stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    all_symbols = []
    for symbol in symbols:
        all_symbols.append({"symbol": symbol, "is_index": False})

    for symbol in index_symbols:
        all_symbols.append({"symbol": symbol, "is_index": True})

    # load realtime data
    date_str = stock.utils.symbol_util.get_realtime_date()
    df_realtime = stock.utils.symbol_util.get_realtime_by_date(date_str)

    results = []
    for symbol in all_symbols:
        res = pool.apply_async(download_stock_history, (symbol, df_realtime, date_str))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        res.wait()
