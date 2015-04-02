#!/usr/bin/python
import os.path
import threading
import Queue
import redis
import stock.utils.request
import stock.utils.symbol_util
from stock.globalvar import *

# check if directory exists, if not create directory
for k,v in REAL_DIR.items():
    if not os.path.isdir(v):
        os.makedirs(v)

class Downloader(threading.Thread):
    r = redis.StrictRedis(host='localhost', port=6379, db=1)
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            symbol = self.queue.get()
            print symbol
            self.download_realtime(symbol)
            self.queue.task_done()

    def download_realtime(self, exsymbol):
        request = stock.utils.request.Request()
        url = "http://qt.gtimg.cn/q=" + exsymbol
        content = ""
        if exsymbol in INDEX.values():
            filepath = os.path.join(REAL_DIR['index'], exsymbol)
            content = request.download_file(url, filepath)
        else:
            filepath = os.path.join(REAL_DIR['stock'], exsymbol)
            content = request.download_file(url, filepath)
        self.__class__.r.set(exsymbol, content)

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
