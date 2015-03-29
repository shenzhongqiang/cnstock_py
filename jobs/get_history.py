#!/usr/bin/python
import os.path
import threading
import Queue
import redis
import stock.utils.request
import stock.utils.symbol_util
from stock.globalvar import *

# check if directory exists, if not create directory
for k,v in HIST_DIR.items():
    if not os.path.isdir(v):
        os.makedirs(v)

class Downloader(threading.Thread):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.flushall()
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            symbol = self.queue.get()
            print symbol
            self.download_history(symbol)
            self.queue.task_done()

    def download_history(self, symbol):
        request = stock.utils.request.Request()
        url = "http://data.gtimg.cn/flashdata/hushen/latest/daily/%s.js?maxage=43201" % (symbol)
        content = ""
        if symbol in INDEX.values():
            filepath = os.path.join(HIST_DIR['index'], symbol)
            content = request.download_file(url, filepath)
        else:
            filepath = os.path.join(HIST_DIR['stock'], symbol)
            content = request.download_file(url, filepath)
            symbol_digit = symbol[2:]
            fenhong_url = "http://stock.finance.qq.com/corp1/distri.php?zqdm=%s" % (symbol_digit)
            fenhong_path = os.path.join(HIST_DIR['fenhong'], symbol)
            request.download_file(fenhong_url, fenhong_path)

        self.__class__.r.set(symbol, content)

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

