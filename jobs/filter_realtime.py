#!/usr/bin/python
import threading
import Queue
from stock.globalvar import *
from stock.filter import *
from stock.marketdata import *
from jinja2 import Environment, FileSystemLoader
import stock.utils.symbol_util
import os.path
import datetime

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
filtered.sort(key=lambda x: x.chgperc, reverse=True)

env = Environment(loader=FileSystemLoader(TMPLDIR))
template = env.get_template('stock_list.tmpl')
html = template.render(stocks=filtered)
dt = datetime.datetime.today()
date = dt.strftime("%y%m%d")
outfile = os.path.join(OUTDIR, date + '.html')
with open(outfile, 'w') as f:
    f.write(html)
