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

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)

dt = datetime.datetime.today()
date = dt.strftime("%y%m%d")
lock = threading.RLock()
marketdata = realtimedata.RealTimeData(lock=lock)

filters = [
    longlowershadow.LongLowerShadow,
    longuppershadow.LongUpperShadow,
    crossstar.CrossStar,
    zhangting.ZhangTing,
    lianzhang.LianZhang,
    volup.VolUp,
]

result = {}
for f in filters:
    output = filter_mt.FilterMT(f, marketdata).run()
    fname = f.__name__
    result[fname] = output

env = Environment(loader=FileSystemLoader(TMPLDIR))
template = env.get_template('stock_list.tmpl')
html = template.render(stocks=result)
outfile = os.path.join(OUTDIR, 'realtime_' + date + '.html')
with open(outfile, 'w') as f:
    f.write(html)
