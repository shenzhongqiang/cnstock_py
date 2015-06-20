#!/usr/bin/python
import os.path
import threading
import Queue
import stock.utils.request
import stock.utils.symbol_util
from stock.globalvar import *

# check if directory exists, if not create directory
for k,v in HIST_DIR.items():
    if not os.path.isdir(v):
        os.makedirs(v)
        os.makedirs(os.path.join(v, "latest"))
        for year in ARCHIVED_YEARS:
            os.makedirs(os.path.join(v, year))

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
        request = stock.utils.request.Request()
        url = "http://data.gtimg.cn/flashdata/hushen/latest/daily/%s.js?maxage=43201" % (symbol)
        content = ""
        filepath = os.path.join(HIST_DIR['stock'], "latest", symbol)
        content = request.download_file(url, filepath)
        symbol_digit = symbol[2:]
        fenhong_url = "http://stock.finance.qq.com/corp1/distri.php?zqdm=%s" % (symbol_digit)
        fenhong_path = os.path.join(HIST_DIR['fenhong'], symbol)
        request.download_file(fenhong_url, fenhong_path)

    def download_archived_history(self, symbol):
        request = stock.utils.request.Request()
        urls = ["http://data.gtimg.cn/flashdata/hushen/daily/15/%s.js" % (symbol),
            "http://data.gtimg.cn/flashdata/hushen/daily/14/%s.js" % (symbol),
            "http://data.gtimg.cn/flashdata/hushen/daily/13/%s.js" % (symbol),
            "http://data.gtimg.cn/flashdata/hushen/daily/12/%s.js" % (symbol),
            "http://data.gtimg.cn/flashdata/hushen/daily/11/%s.js" % (symbol)]

        content = ""
        for year in ARCHIVED_YEARS:
            filepath = os.path.join(HIST_DIR['stock'], year, symbol)
            url = "http://data.gtimg.cn/flashdata/hushen/daily/%s/%s.js" % (year, symbol)
            content = request.download_file(url, filepath)
            symbol_digit = symbol[2:]
            fenhong_url = "http://stock.finance.qq.com/corp1/distri.php?zqdm=%s" % (symbol_digit)
        fenhong_path = os.path.join(HIST_DIR['fenhong'], symbol)
        request.download_file(fenhong_url, fenhong_path)

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

