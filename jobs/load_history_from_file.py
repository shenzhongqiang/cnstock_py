#!/usr/bin/python
from multiprocessing import Pool
from tqdm import tqdm, trange
from stock.marketdata.storefactory import get_store
import stock.utils.symbol_util

def worker(filestore, redisstore, exsymbol):
    df = filestore.get(exsymbol)
    redisstore.save(exsymbol, df)

if __name__ == "__main__":
    pool = Pool(20)
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    exsymbols = map(lambda x: stock.utils.symbol_util.symbol_to_exsymbol(x, index=False), symbols)
    id_exsymbols = map(lambda x: stock.utils.symbol_util.symbol_to_exsymbol(x, index=True), index_symbols)
    all_exsymbols = exsymbols
    all_exsymbols.extend(id_exsymbols)
    results = []
    filestore = get_store("file_store")
    redisstore = get_store("redis_store")
    for exsymbol in all_exsymbols:
        res = pool.apply_async(worker, args=(filestore, redisstore, exsymbol,))
        results.append(res)
    for i in trange(len(results)):
        res = results[i]
        res.wait()
