#!/usr/bin/python
import os.path
import threading
import Queue
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import *

# check if directory exists, if not create directory
stock_dir = HIST_DIR['stock']
if not os.path.isdir(stock_dir):
    os.makedirs(stock_dir)
    os.makedirs(os.path.join(stock_dir, "latest"))
for year in ARCHIVED_YEARS:
    year_dir = os.path.join(stock_dir, year)
    if not os.path.isdir(year_dir):
        os.makedirs(year_dir)

fuquan_dir = HIST_DIR['fuquan']
if not os.path.isdir(fuquan_dir):
    os.makedirs(fuquan_dir)

class Downloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            symbol = self.queue.get()
            print symbol
            self.download_history(symbol)
            self.download_archived_history(symbol)
            self.queue.task_done()

    def download_history(self, symbol):
        url = "http://data.gtimg.cn/flashdata/hushen/latest/daily/%s.js?maxage=43201" % (symbol)
        content = ""
        filepath = os.path.join(HIST_DIR['stock'], "latest", symbol)
        content = request.download_file(url, filepath)
        symbol_digit = symbol[2:]
        fuquan_url = "http://data.gtimg.cn/flashdata/hushen/fuquan/%s.js?maxage=6000000" % (symbol)
        fuquan_path = os.path.join(HIST_DIR['fuquan'], symbol)
        request.download_file(fuquan_url, fuquan_path)

    def download_archived_history(self, symbol):
        content = ""
        for year in ARCHIVED_YEARS:
            filepath = os.path.join(HIST_DIR['stock'], year, symbol)
            url = "http://data.gtimg.cn/flashdata/hushen/daily/%s/%s.js" % (year, symbol)
            content = request.download_file(url, filepath)

if __name__ == "__main__":
    queue = Queue.Queue()
    for i in range(10):
        t = Downloader(queue)
        t.setDaemon(True)
        t.start()

    # download stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols('all')
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    symbols.extend(index_symbols)
    for symbol in symbols:
        queue.put(symbol)

    queue.join()

