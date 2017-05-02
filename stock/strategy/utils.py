import datetime
import os.path
from multiprocessing import Pool
from stock.filter.utils import *
from stock.globalvar import *
from stock.utils.dt import *
from stock.utils import fuquan
from stock.utils.symbol_util import *
from stock.marketdata.bar import Bar
import pandas as pd

def load_csv(symbol):
    path = os.path.join(HIST_DIR["stock"], symbol)
    df = pd.read_csv(path, dtype=str)
    return df

def get_complete_history(symbol):
    try:
        path = os.path.join(HIST_DIR["stock"], symbol)
        df = pd.read_csv(path, dtype=str, engine="c")
    except IOError, e:
        return [symbol, []]

    all_history = []
    for index, row in df.iloc[::-1].iterrows():
        dt = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
        exsymbol = symbol_to_exsymbol(symbol)
        bar = Bar(exsymbol, date=row["date"], dt=dt, open=float(row["open"]),
            close=float(row["close"]), high=float(row["high"]), low=float(row["low"]),
            volume=float(row["volume"]))
        all_history.append(bar)

    return [symbol, all_history]

def get_exsymbol_history():
    p = Pool(20)
    symbols = get_stock_symbols()
    exsymbol_history = {}

    results = []
    for symbol in symbols:
        res = p.apply_async(get_complete_history, (symbol,))
        results.append(res)

    for res in results:
        data = res.get()
        symbol = data[0]
        exsymbol = symbol_to_exsymbol(symbol)
        exsymbol_history[exsymbol] = data[1]
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

def is_dieting(yest, today):
    dt_price = get_dt_price(yest)
    if abs(dt_price - today) < 1e-5:
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
