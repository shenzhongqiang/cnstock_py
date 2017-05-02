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

def is_trend_up(history):
    curr_closes = [ x.close for x in history[0:10] ]
    prev_closes = [ x.close for x in history[1:11] ]
    if sum(curr_closes) > sum(prev_closes):
        return True

    return False

def filter_stock(exsymbol_history, date):
    result = []
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

        zt_price3 = get_zt_price(history[2].close)
        if not abs(zt_price3 - history[1].close) < 1e-5:
            continue

        if abs(history[1].open - history[2].close) / history[2].close > 0.03:
            continue
        if abs(history[0].close - history[1].close) / history[1].close > 0.07:
            continue
        if abs(history[0].close - history[0].open) > history[0].open * 0.02:
            continue

        vols = [ x.volume for x in history[2:7] ]
        highs = [ x.high for x in history[2:7] ]
        lows = [ x.low for x in history[2:7] ]
        avg_vol = sum(vols) / len(vols)
        max_vol = max(vols)
        max_high = max(highs)
        min_low = min(lows)

        if max_high / min_low > 1.15:
            continue

        closes = [ x.close for x in history[1:7] ]
        min_close = min(closes)
        chg = history[0].close / min_close - 1
        result.append({"exsymbol": exsymbol, "history": history, "chg": chg})

    result.sort(key=lambda x: x["chg"])
    num = min(len(result), 1)
    return result[0:num]


engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False})
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
order = Order(engine)
order.add_account(80000)

if len(sys.argv) < 3:
    print "Usage: %s <start> <end>" % (sys.argv[0])
    sys.exit(1)
start = sys.argv[1]
end = sys.argv[2]
dates = get_archived_trading_dates(start, end)
dates_asc = dates[::-1]
exsymbol_history = get_exsymbol_history()
for date in dates_asc:
    dt = parse_datetime(date)
    result = filter_stock(exsymbol_history, date)

    positions = order.get_positions()
    for pos in positions:
        history = exsymbol_history[pos.exsymbol]
        history = get_history_by_date(history, date)
        bar = get_bar(history, date)
        if bar != None:
            order.sell(pos.exsymbol, bar.close, dt, pos.amount)
            print "sell %d %s at %f on %s" % (
                pos.amount, pos.exsymbol, bar.close, date)

    for data in result:
        exsymbol = data["exsymbol"]
        history = data["history"]
        bar = get_bar(history, date)
        amount = math.floor(100/bar.close) * 100
        if amount > 0:
            order.buy(exsymbol, bar.close, dt, amount)
            print "buy %d %s at %f on %s" % (
                amount, exsymbol, bar.close, date)

report = Report(engine)
report.print_report()

