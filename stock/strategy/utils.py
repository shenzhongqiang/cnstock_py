import os.path
from stock.filter.utils import *
from stock.globalvar import *
from stock.utils.dt import *
from stock.utils.fuquan import *
from stock.utils.symbol_util import *
from stock.marketdata.bar import Bar

def get_complete_history(exsymbol):
    all_history = []
    for year in ARCHIVED_YEARS:
        filepath = os.path.join(HIST_DIR['stock'], year, exsymbol)
        if not os.path.isfile(filepath):
            continue

        f = open(filepath, "r")
        contents = f.read()
        f.close()

        lines = contents.split('\\n\\\n')
        i = len(lines) - 2
        while i >= 1:
            line = lines[i]
            (date, o, close, high, low, volume) = line.split(' ')
            dt = parse_datetime(date)
            bar = Bar(exsymbol, date=date, dt=dt, open=float(o), \
                close=float(close), high=float(high), low=float(low), \
                volume=float(volume))
            all_history.append(bar)
            i = i - 1

    return all_history

def get_exsymbol_history():
    exsymbols = get_stock_symbols('all')
    indice = get_index_symbols()
    exsymbols.extend(indice)
    exsymbol_history = {}
    for exsymbol in exsymbols:
        try:
            all_history = get_complete_history(exsymbol)
        except Exception, e:
            continue

        Fuquan.fuquan_history(all_history)
        exsymbol_history[exsymbol] = all_history
    return exsymbol_history

def get_history_by_date(all_history, date):
    dt = parse_datetime(date)
    result = []
    for bar in all_history:
        if bar.dt <= dt:
            result.append(bar)
    return result

def is_zhangting(exsymbol, history, date):
    yest_close = history[1].close
    today_close = history[0].close
    zt_price = get_zt_price(yest_close)
    if abs(zt_price - today_close) < 1e-5:
        return True
    return False

def is_buyable(exsymbol, history, date):
    dt = parse_datetime(date)
    if history[0].dt == dt and \
        not is_zhangting(exsymbol, history, date):
        return True
    return False

def get_bar(history, date):
    dt = parse_datetime(date)
    if history[0].dt == dt:
        return history[0]

    return None

def get_buyable_exsymbols(exsymbol_history, date):
    result = {}
    for exsymbol in exsymbol_history.keys():
        history = exsymbol_history[exsymbol]
        if is_buyable(exsymbol, history, date):
            result[exsymbol] = history

    return result
