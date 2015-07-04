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
        try:
            history = get_history_by_date(exsymbol_history[exsymbol], date)
        except:
            continue

        if len(history) < 100:
            continue

        vols = [ x.volume for x in history[1:10] ]
        avg_vol = sum(vols) / len(vols)
        max_vol = max(vols)
        chg = history[0].close / history[1].close - 1
        if history[0].volume > max_vol and \
            history[0].volume > avg_vol * 2 and \
            chg > 0.04 and chg < 0.06:
            result[exsymbol] = history
    return result


engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False})
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
order = Order(engine)

dates = get_archived_trading_dates()[50:70]
dates_asc = dates[::-1]
exsymbol_history = get_exsymbol_history()
for date in dates_asc:
    result = filter_stock(exsymbol_history, date)
    for exsymbol in result.keys():
        result[exsymbol] = get_history_by_date(result[exsymbol], date)

    positions = order.get_positions()
    for pos in positions:
        history = exsymbol_history[pos.exsymbol]
        history = get_history_by_date(history, date)
        bar = get_bar(history, date)
        if bar != None:
            order.sell(pos.exsymbol, bar.close, date, pos.amount)
            print "sell %d %s at %f on %s" % (
                pos.amount, pos.exsymbol, bar.close, date)

    if result.keys():
        tradable = get_buyable_exsymbols(result, date)
        if not tradable.keys():
            continue
        exsymbol = tradable.keys()[0]
        history = tradable[exsymbol]
        bar = get_bar(history, date)
        amount = math.floor(100/bar.close) * 100
        order.buy(exsymbol, bar.close, date, amount)
        print "buy %d %s at %f on %s" % (
            amount, exsymbol, bar.close, date)

report = Report(engine)
report.print_report()
