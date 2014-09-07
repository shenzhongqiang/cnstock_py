#!/usr/bin/python
import threading
import Queue
from stock.filter import *
from stock.marketdata import *
import stock.utils.symbol_util

queue = Queue.Queue()
lock = threading.RLock()
output = []
marketdata = realtimedata.RealTimeData(lock=lock)
for i in range(1):
    t = zhangting.ZhangTing(queue, marketdata, output)
    t.setDaemon(True)
    t.start()

# download stock symbols
symbols = stock.utils.symbol_util.get_stock_symbols('all')
for symbol in symbols:
    queue.put(symbol)

queue.join()

filtered = filter(lambda x: x.result, output)
for cr in filtered:
    print "%s %s" % (cr.exsymbol, cr.result)
