#!/usr/bin/python
from stock.globalvar import *
from stock.powerfilter import *
from stock.marketdata import *
from jinja2 import Environment, FileSystemLoader
import stock.utils.symbol_util
import os.path
import sys
import logging
import logging.config
import datetime

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

dt = datetime.datetime.today()
date = dt.strftime("%y%m%d")
marketdata = realtimedata.RealTimeData()

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)

filters = [
    longlowershadow.LongLowerShadow,
    longuppershadow.LongUpperShadow,
    strong.Strong,
]

result = {}
exsymbols = stock.utils.symbol_util.get_stock_symbols('all')
for f in filters:
    fname = f.__name__
    output = f(marketdata).check(exsymbols)
    result[fname] = output

env = Environment(loader=FileSystemLoader(TMPLDIR))
template = env.get_template('stock_list.tmpl')
html = template.render(stocks=result)
outfile = os.path.join(OUTDIR, 'power_realtime_' + date + '.html')
with open(outfile, 'w') as f:
    f.write(html)
