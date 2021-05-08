#!/usr/bin/python
import requests
import pandas as pd
from tqdm import tqdm, trange
import os.path
from multiprocessing import Pool
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import FINANCE_DIR, BASIC_DIR
from stock.marketdata.storefactory import get_store

ZCFZB_URL = "http://quotes.money.163.com/service/zcfzb_%s.html"
LRB_URL = "http://quotes.money.163.com/service/lrb_%s.html"
XJLLB_URL = "http://quotes.money.163.com/service/xjllb_%s.html"

# check if directory exists, if not create directory
stock_dir = FINANCE_DIR['stock']
if not os.path.isdir(stock_dir):
    os.makedirs(stock_dir)
if not os.path.isdir(BASIC_DIR):
    os.makedirs(BASIC_DIR)

def download_zcfzb(symbol):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_zcfzb" % exsymbol
        path = os.path.join(stock_dir, filename)
        url = ZCFZB_URL % symbol
        r = requests.get(url)
        with open(path, "wb") as f:
            content = r.content.decode("gb2312")
            f.write(content.encode("utf-8"))
    except Exception as e:
        print("error getting ZCFZB data due to %s" % str(e))

def download_lrb(symbol):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_lrb" % exsymbol
        path = os.path.join(stock_dir, filename)
        url = LRB_URL % symbol
        r = requests.get(url)
        with open(path, "wb") as f:
            content = r.content.decode("gb2312")
            f.write(content.encode("utf-8"))
    except Exception as e:
        print("error getting LRB data due to %s" % str(e))

def download_xjllb(symbol):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_xjllb" % exsymbol
        path = os.path.join(stock_dir, filename)
        url = XJLLB_URL % symbol
        r = requests.get(url)
        with open(path, "wb") as f:
            content = r.content.decode("gb2312")
            f.write(content.encode("utf-8"))
    except Exception as e:
        print("error getting XJLLB data due to %s" % str(e))

def download_stock_finance(data):
    download_zcfzb(data["symbol"])
    download_lrb(data["symbol"])
    download_xjllb(data["symbol"])

def dump_basics_data():
    df = ts.get_stock_basics()
    filepath = os.path.join(BASIC_DIR, "basics")
    df.to_csv(filepath, encoding="utf-8")

if __name__ == "__main__":
    pool = Pool(20)

    # download stock basics
    # dump_basics_data()

    # download stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()
    all_symbols = []
    for symbol in symbols:
        all_symbols.append({"symbol": symbol})

    results = []
    for symbol in all_symbols:
        res = pool.apply_async(download_stock_finance, (symbol,))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        res.wait()

