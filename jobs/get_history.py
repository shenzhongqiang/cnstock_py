#!/usr/bin/python
from tqdm import tqdm, trange
import os.path
from multiprocessing import Pool
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
    try:
        symbol = data["symbol"]
        is_index = data["is_index"]
        df = ts.get_k_data(symbol, index=is_index)
        path = None
        if not is_index:
            path = os.path.join(stock_dir, symbol)
        else:
            path = os.path.join(index_dir, symbol)
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol, is_index)
        store = get_store("redis_store")
        store.save(exsymbol, df)
        store.save_into_file(exsymbol, df)
    except Exception, e:
        #print "error getting history due to %s" % str(e)
        pass

if __name__ == "__main__":
    pool = Pool(20)

    # download stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    all_symbols = []
    for symbol in symbols:
        all_symbols.append({"symbol": symbol, "is_index": False})

    for symbol in index_symbols:
        all_symbols.append({"symbol": symbol, "is_index": True})

    store = get_store("redis_store")
    store.flush()
    results = []
    for symbol in all_symbols:
        res = pool.apply_async(download_stock_history, (symbol,))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        res.wait()

