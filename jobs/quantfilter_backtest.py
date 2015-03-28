#!/usr/bin/python
import threading
from stock.globalvar import *
from stock.quant import *
from stock.marketdata import *
from jinja2 import Environment, FileSystemLoader
import stock.utils.symbol_util
import os.path
import sys
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <date>\n' % sys.argv[0])
    sys.exit(1)

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)

date = sys.argv[1]
lock = threading.RLock()
marketdata = backtestdata.BackTestData(lock=lock, date=date)

filters = [
    covar.CoVar
]

result = {}
exsymbols = stock.utils.symbol_util.get_stock_symbols('all')
for f in filters:
    fname = f.__name__
    output = f(marketdata).check(exsymbols)
    result[fname] = output

#env = Environment(loader=FileSystemLoader(TMPLDIR))
#template = env.get_template('stock_list.tmpl')
#html = template.render(stocks=result)
#outfile = os.path.join(OUTDIR, 'backtest_' + date + '.html')
#with open(outfile, 'w') as f:
#    f.write(html)
#
