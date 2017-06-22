#!/usr/bin/python
from multiprocessing import Pool
from tqdm import tqdm, trange
import stock.marketdata.store
import stock.utils.symbol_util

if __name__ == "__main__":
    pool = Pool(20)
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    exsymbols = map(lambda x: stock.utils.symbol_util.symbol_to_exsymbol(x, index=False), symbols)
    id_exsymbols = map(lambda x: stock.utils.symbol_util.symbol_to_exsymbol(x, index=True), index_symbols)
    all_exsymbols = exsymbols
    all_exsymbols.extend(id_exsymbols)
    results = []
    stock.marketdata.store.init()
    for exsymbol in all_exsymbols:
        res = pool.apply_async(stock.marketdata.store.get_from_file, (exsymbols,))
        results.append(res)
    for i in trange(len(results)):
        res = results[i]
        res.wait()

