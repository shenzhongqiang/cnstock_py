from tqdm import tqdm, trange
import datetime
import os.path
from multiprocessing import Pool
import pandas as pd
from stock.filter.utils import get_dt_price
from stock.globalvar import *
from stock.utils.dt import parse_datetime
from stock.utils import fuquan
from stock.utils.symbol_util import *
from stock.marketdata.bar import Bar
from stock.marketdata.utils import load_csv
from stock.marketdata.storefactory import get_store
from config import store_type
from stock.exceptions import NoHistoryOnDate

def get_complete_history(exsymbol):
    store = get_store(store_type)
    history = store.get(exsymbol)
    return history

def get_exsymbol_history():
    p = Pool(10)
    symbols = get_stock_symbols()
    exsymbol_history = {}

    results = []
    for symbol in symbols:
        res = p.apply_async(get_complete_history, (symbol,))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        data = res.get()
        symbol = data[0]
        exsymbol = symbol_to_exsymbol(symbol)
        exsymbol_history[exsymbol] = data[1]
        i += 1
    return exsymbol_history

def get_history_by_date(df, date):
    return df[df.date < date]

def get_history_on_date(df, date):
    try:
        return df.ix[date]
    except KeyError, e:
        raise NoHistoryOnDate(date)

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
