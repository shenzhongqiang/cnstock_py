import threading
import Queue
from stock.filter import *
from stock.marketdata import *
from stock.utils.symbol_util import *
from stock.trade.order import *
from stock.trade.report import *
from stock.globalvar import *
from datetime import datetime
import sys
import math

def demo_trade(dates, db_file=DBFILE, high=1.06):
    engine = create_engine('sqlite://', echo=False, \
        connect_args={'check_same_thread':False})
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    demo_ord = Order(engine)

    for date in dates:
        print "demo trade ", date
        queue = Queue.Queue()
        output = []

        # filter stocks
        marketdata = backtestdata.BackTestData(date=date)
        for i in range(1):
            t = longuppershadow.LongUpperShadow(queue, marketdata, output,
                params={"high":high, "body":0.02, "chg":0.06})
            t.setDaemon(True)
            t.start()

        # download stock symbols
        symbols = get_stock_symbols('all')
        for symbol in symbols:
            queue.put(symbol)

        queue.join()

        output.sort(key=lambda x: x.chgperc, reverse=True)

        # sell all existing positions
        positions = demo_ord.get_positions()
        for pos in positions:
            bar = marketdata.get_data(pos.exsymbol)
            demo_ord.sell(pos.exsymbol, bar.close, date, pos.amount)

        # buy positions
        for cr in output:
            close = cr.bar_today.close
            exsymbol = cr.exsymbol
            amount = math.floor(100 / close) * 100

            if not demo_ord.has_position(exsymbol):
                demo_ord.buy(exsymbol, close, date, amount)

    demo_rep = Report(engine)
    pl = demo_rep.get_profit_loss()
    return pl


def optimize_trade(dates):
    print "optimizing ", dates
    max_pl = -sys.maxint - 1
    op_high = 0
    high_list = [x * 0.01  for x in range(104, 110, 1)]

    for high in high_list:
        print "optimize ", high
        pl = demo_trade(dates, high=high)
        print  "pl:", pl
        if pl > max_pl:
            max_pl = pl
            op_high = high

    return (op_high, max_pl)


# real trade
engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False})
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
real_ord = Order(engine)

f = longuppershadow.LongUpperShadow
dates_desc = get_trading_dates()
dates_asc = dates_desc[::-1]

start = 35
end = 40
window = 10

for i in range(start, end):
    op_dates = dates_asc[i - window: i - 1]
    (op_high, pl) = optimize_trade(op_dates)

    date = dates_asc[i]
    print "real trade ", date
    queue = Queue.Queue()
    output = []

    # filter stocks
    marketdata = backtestdata.BackTestData(date=date)
    for j in range(1):
        t = longuppershadow.LongUpperShadow(queue, marketdata, output,
            params={"high":op_high, "body":0.02, "chg":0.06})
        t.setDaemon(True)
        t.start()

    # download stock symbols
    symbols = get_stock_symbols('all')
    for symbol in symbols:
        queue.put(symbol)

    queue.join()

    output.sort(key=lambda x: x.chgperc, reverse=True)

    # sell all existing positions
    positions = real_ord.get_positions()
    for pos in positions:
        bar = marketdata.get_data(pos.exsymbol)
        real_ord.sell(pos.exsymbol, bar.close, date, pos.amount)

    # buy positions
    for cr in output:
        close = cr.bar_today.close
        exsymbol = cr.exsymbol
        amount = math.floor(100 / close) * 100

        if not real_ord.has_position(exsymbol):
            real_ord.buy(exsymbol, close, date, amount)

real_rep = Report(engine)
real_rep.print_report()

