#!/usr/bin/python
import threading
import Queue
from stock.globalvar import *
from stock.filter import *
from stock.marketdata import *
from jinja2 import Environment, FileSystemLoader
import stock.utils.symbol_util
import os.path
import sys

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <date>\n' % sys.argv[0])
    sys.exit(1)

queue = Queue.Queue()
lock = threading.RLock()
output = []
date = sys.argv[1]
marketdata = backtestdata.BackTestData(lock=lock, date=date)
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

env = Environment(loader=FileSystemLoader(TMPLDIR))
template = env.get_template('stock_list.tmpl')
html = template.render(stocks=filtered)
outfile = os.path.join(OUTDIR, date + '.html')
with open(outfile, 'w') as f:
    f.write(html)
