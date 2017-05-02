#!/usr/bin/python
import os.path
import threading
import Queue
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import *
import tushare as ts

# check if directory exists, if not create directory
stock_dir = HIST_DIR['stock']
index_dir = HIST_DIR['index']
if not os.path.isdir(stock_dir):
    os.makedirs(stock_dir)
if not os.path.isdir(index_dir):
    os.makedirs(index_dir)

class Downloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                data = self.queue.get()
                print data["symbol"]
                self.download_stock_history(data["symbol"], is_index=data["is_index"])
                self.queue.task_done()
            except Exception, e:
                print str(e)
                self.queue.task_done()

    def download_stock_history(self, symbol, is_index):
        df = ts.get_k_data(symbol, index=is_index)
        path = None
        if not is_index:
            path = os.path.join(stock_dir, symbol)
        else:
            path = os.path.join(index_dir, symbol)
        df.to_csv(path)

if __name__ == "__main__":
    queue = Queue.Queue()
    for i in range(10):
        t = Downloader(queue)
        t.setDaemon(True)
        t.start()

    # download stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    for symbol in symbols:
        queue.put({"symbol": symbol, "is_index": False})

    for symbol in index_symbols:
        queue.put({"symbol": symbol, "is_index": True})

    queue.join()

