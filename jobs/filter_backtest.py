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

class FilterMT:
    def __init__(self, f, date):
        self.f = f
        self.date = date

    def run(self):
        queue = Queue.Queue()
        lock = threading.RLock()
        output = []
        marketdata = backtestdata.BackTestData(lock=lock, date=self.date)

        for i in range(1):
            t = self.f(queue, marketdata, output)
            t.setDaemon(True)
            t.start()

        # download stock symbols
        symbols = stock.utils.symbol_util.get_stock_symbols('all')
        for symbol in symbols:
            queue.put(symbol)

        queue.join()

        output.sort(key=lambda x: x.chgperc, reverse=True)

        env = Environment(loader=FileSystemLoader(TMPLDIR))
        template = env.get_template('stock_list.tmpl')
        html = template.render(stocks=output)
        outfile = os.path.join(OUTDIR, self.date + '.html')
        with open(outfile, 'w') as f:
            f.write(html)

f = longuppershadow.LongUpperShadow
FilterMT(f, sys.argv[1]).run()

