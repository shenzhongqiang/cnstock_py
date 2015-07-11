import sys
import datetime
import math
from stock.filter.utils import *
from stock.globalvar import *
from stock.strategy.utils import *
from stock.trade.order import *
from stock.trade.report import *
from stock.utils.dt import *
from stock.utils.fuquan import *
from stock.utils.symbol_util import *

def filter_stock(exsymbol_history, date):
    result = {}
    for exsymbol in exsymbol_history.keys():
        history  = []
        try:
            history = get_history_by_date(exsymbol_history[exsymbol], date)
        except:
            continue

        if len(history) < 100:
            continue

        if not is_buyable(exsymbol, history, date):
            continue

        zt_price3 = get_zt_price(history[3].close)
        if not abs(zt_price3 - history[2].close) < 1e-5:
            continue

        #if abs(history[0].close - history[0].open) > history[0].open * 0.02:
        #    continue

        vols = [ x.volume for x in history[3:10] ]
        closes = [ x.close for x in history[3:10] ]
        avg_vol = sum(vols) / len(vols)
        max_vol = max(vols)
        max_close = max(closes)
        min_close = min(closes)

        chg = history[0].close / history[1].close - 1

        if history[0].volume > max_vol and \
            history[0].volume > avg_vol * 2 and \
            history[1].volume > max_vol and \
            history[1].volume > avg_vol * 2 and \
            history[2].volume > max_vol and \
            history[2].volume > avg_vol * 2 and \
            not (history[3].volume > max_vol and \
            history[3].volume > avg_vol * 2):
            result[exsymbol] = history

        best_exsymbol = ''
        best_chg = 0.3
        for exsymbol in result.keys():
            history = result[exsymbol]
            closes = [ x.close for x in history[1:10] ]
            min_close = min(closes)
            chg = history[0].close / min_close - 1
            if chg < best_chg:
                best_chg = chg
                best_exsymbol = exsymbol
    return best_exsymbol


engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False})
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
order = Order(engine)

if len(sys.argv) < 3:
    print "Usage: %s <start> <end>" % (sys.argv[0])
    sys.exit(1)
start = int(sys.argv[1])
end = int(sys.argv[2])
dates = get_archived_trading_dates()[start:end]
dates_asc = dates[::-1]
exsymbol_history = get_exsymbol_history()

state = 0
sl = 0
entry = 0
target = 0
pos_exsymbol = ""
for date in dates_asc:
    if state == 0:
        best_exsymbol = filter_stock(exsymbol_history, date)
        if best_exsymbol == "":
            continue
        history = get_history_by_date(exsymbol_history[best_exsymbol], date)
        bar = get_bar(history, date)
        amount = math.floor(100/bar.close) * 100
        order.buy(best_exsymbol, bar.close, date, amount)
        print "buy %d %s at %f on %s" % (
            amount, best_exsymbol, bar.close, date)
        state = 1
        entry = bar.close
        sl = bar.close * 0.9
        target = bar.close * 1.2
        pos_exsymbol = best_exsymbol
        continue

    if state == 1:
        history = exsymbol_history[pos_exsymbol]
        history = get_history_by_date(history, date)
        bar = get_bar(history, date)
        if bar != None:
            if bar.close < sl:
                pos = order.get_positions()[0]
                order.sell(pos.exsymbol, bar.close, date, pos.amount)
                print "sell %d %s at %f on %s" % (
                    pos.amount, pos.exsymbol, bar.close, date)
                state = 0
            if bar.close > target:
                pos = order.get_positions()[0]
                order.sell(pos.exsymbol, bar.close, date, pos.amount)
                print "sell %d %s at %f on %s" % (
                    pos.amount, pos.exsymbol, bar.close, date)
                state = 0
        continue

report = Report(engine)
report.print_report()
