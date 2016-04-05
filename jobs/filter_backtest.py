#!/usr/bin/python
import threading
from stock.globalvar import *
from stock.filter import *
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
marketdata = backtestdata.BackTestData(date=date)

filters = [
#    longuppershadow.LongUpperShadow,
#    longlowershadow.LongLowerShadow,
#    crossstar.CrossStar,
#    zhangting.ZhangTing,
#    lianzhang.LianZhang,
    volup.VolUp,
#    high.High,
#    round_bottom.RoundBottom,
#    kangdie.Kangdie,
]

result = {}
for f in filters:
    fname = f.__name__
    output = filter_mt.FilterMT(f, marketdata).filter_stock()
    result[fname] = output

env = Environment(loader=FileSystemLoader(TMPLDIR))
template = env.get_template('stock_list.tmpl')
html = template.render(stocks=result)
outfile = os.path.join(OUTDIR, 'backtest_' + date + '.html')
with open(outfile, 'w') as f:
    f.write(html)
