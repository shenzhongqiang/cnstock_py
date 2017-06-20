import datetime
import os.path
import re
import json
from stock.utils import request
from stock.globalvar import *
from stock.marketdata.utils import load_csv
import tushare as ts
import pandas as pd

class InvalidType(Exception):
    pass

def get_stock_symbols():
    df = pd.read_csv(SYM["all"], dtype=str)
    return df.code.tolist()

def get_index_symbols():
    df = pd.read_csv(SYM["all"], dtype=str)
    return df.code.tolist()

def get_index_symbol(type):
    return INDEX[type]

def get_trading_dates():
    index_path = os.path.join(HIST_DIR["index"], "000001")
    df = load_csv(index_path)
    return df.date.tolist()

def get_archived_trading_dates(start, end):
    index_path = os.path.join(HIST_DIR["index"], "000001")
    df = load_csv(index_path)
    dates = df.date.tolist()
    dts = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), dates)
    result = []
    start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    for dt in dts:
        if dt >= start_dt and dt <= end_dt:
            result.append(dt)

    return map(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d"), result)

def get_st(exsymbols):
    exsymbol_str = ",".join(exsymbols)
    url = "http://push2.gtimg.cn/q=%s" % (exsymbol_str)
    result = request.send_request(url)
    lines = result.split("\n")
    st = {}
    for line in lines:
        if line == "":
            continue
        cnname = line.split('~')[1]
        exsymbol = line.split('=')[0][2:]
        match = re.search(r"ST", cnname)
        if match:
            st[exsymbol] = True
        else:
            st[exsymbol] = False
    return st

def download_symbols():
    df = ts.get_stock_basics()
    df.to_csv(SYM["all"])
    index_df = ts.get_index()
    index_df.to_csv(SYM["id"])

def is_symbol_cy(symbol):
    patt = re.compile('^sz3')
    if patt.search(symbol) and symbol != INDEX['cy']:
        return True
    else:
        return False

def is_symbol_sh(symbol):
    patt = re.compile('^sh')
    if patt.search(symbol) and symbol != INDEX['sh']:
        return True
    else:
        return False

def is_symbol_sz(symbol):
    patt = re.compile('^sz0')
    if patt.search(symbol) and symbol != INDEX['sz']:
        return True
    else:
        return False

def symbol_to_exsymbol(symbol):
    exsymbol = ''
    if re.search(r'^6', symbol):
        exsymbol = 'sh' + symbol
    elif re.search(r'^3', symbol):
        exsymbol = 'sz' + symbol
    elif re.search(r'^0', symbol):
        exsymbol = 'sz' + symbol
    return exsymbol

def exsymbol_to_symbol(exsymbol):
    return exsymbol[2:]

