import threading
import Queue
from stock.filter import *
from stock.marketdata import *
from stock.utils.symbol_util import *
from stock.trade.order import *
from stock.trade.report import *
from stock.globalvar import *
from datetime import datetime
import math

lock = threading.RLock()
f = longuppershadow.LongUpperShadow
dates_desc = get_trading_dates()[60:-30]

engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False})
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

for date in reversed(dates_desc):
    print date
    queue = Queue.Queue()
    output = []

    # filter stocks
    marketdata = backtestdata.BackTestData(lock=lock, date=date)
    for i in range(1):
        t = longuppershadow.LongUpperShadow(queue, marketdata, output,
            params={"high":1.06, "body":0.02, "chg":0.06})
        t.setDaemon(True)
        t.start()

    # download stock symbols
    symbols = get_stock_symbols('all')
    for symbol in symbols:
        queue.put(symbol)

    queue.join()

    output.sort(key=lambda x: x.chgperc, reverse=True)

    # sell all existing positions
    positions = get_positions()
    for pos in positions:
        bar = marketdata.get_data(pos.exsymbol)
        sell(pos.exsymbol, bar.close, date, pos.amount)

    # buy positions
    for cr in output:
        close = cr.bar_today.close
        exsymbol = cr.exsymbol
        amount = math.floor(100 / close) * 100

        if not has_position(exsymbol):
            buy(exsymbol, close, date, amount)

print_report()

def optimize_trade():
    pass
