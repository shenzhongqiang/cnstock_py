#!/usr/bin/python
import sys
import pandas as pd
import os.path
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import HIST_DIR
from stock.marketdata.storefactory import get_store
import tushare as ts

# check if directory exists, if not create directory
stock_dir = HIST_DIR['stock']
index_dir = HIST_DIR['index']
if not os.path.isdir(stock_dir):
    os.makedirs(stock_dir)
if not os.path.isdir(index_dir):
    os.makedirs(index_dir)

def download_stock_history(data):
    symbol = data["symbol"]
    is_index = data["is_index"]
    df = ts.get_k_data(symbol, index=is_index, start="2000-01-01")
    if df.empty:
        return
    path = os.path.join(stock_dir, symbol)
    exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol, is_index)
    redis_store = get_store("redis_store")
    file_store = get_store("file_store")
    redis_store.save(exsymbol, df)
    file_store.save(exsymbol, df)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <symbol> <is_index>" % sys.argv[0]
        sys.exit(1)
    symbol = sys.argv[1]
    is_index = int(sys.argv[2]) > 0
    download_stock_history({"symbol": symbol, "is_index": is_index})
