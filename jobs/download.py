import re
import sys
import argparse
import os.path
import urllib

from multiprocessing import Pool
from urllib.parse import urlsplit, parse_qs, urlencode

from tqdm import trange
import requests
import tushare as ts
import pandas as pd

from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import HIST_DIR, SYM
from stock.marketdata.storefactory import get_store

def is_sh(a_symbol):
    m = re.match(r"6", a_symbol)
    if m:
        return True
    return False

def get_symbols_df(url_pattern):
    pz = 5000
    i = 1
    result = []
    while True:
        url = url_pattern.format(i, pz)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    symbols = list(map(lambda x: x["f12"], result))
    names = list(map(lambda x: x["f14"], result))
    df = pd.DataFrame({"symbol": symbols, "name": names})
    return df

def download_stock_symbols():
    url_pattern = "https://48.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f12,f14"
    df = get_symbols_df(url_pattern)
    df.to_csv(SYM["all"], index=False)

def download_index_symbols():
    url_patterns = [
    "https://77.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+s:2&fields=f12,f14",
    "https://37.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:5&fields=f12,f14",
    "https://41.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:2&fields=f12,f14",
    ]
    dfs = []
    for url_pattern in url_patterns:
        df = get_symbols_df(url_pattern)
        dfs.append(df)
    df = pd.concat(dfs)
    df.to_csv(SYM["id"], index=False)

def get_hist_from_data(data):
    klines = data["data"]["klines"]
    dates = []
    opens = []
    closes = []
    highs = []
    lows = []
    vols = []
    amounts = []
    for kline in klines:
        parts = kline.split(",")
        date_str = parts[0]
        open = float(parts[1])
        close = float(parts[2])
        high = float(parts[3])
        low = float(parts[4])
        vol = float(parts[5])
        amount = float(parts[6])
        dates.append(date_str)
        opens.append(open)
        closes.append(close)
        highs.append(high)
        lows.append(low)
        vols.append(vol)
        amounts.append(amount)
    df = pd.DataFrame({"date": dates, "open": opens, "close": closes, "high": highs, "low": lows, "volume": vols, "amount": amounts})
    return df

def download_stock_hist(symbol):
    if is_sh(symbol):
        url = "https://25.push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=0&end=20500101&lmt=300".format(symbol)
    else:
        url = "https://25.push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=0&end=20500101&lmt=300".format(symbol)
    try:
        r = requests.get(url, verify=False)
        data = r.json()
        df = get_hist_from_data(data)
        filepath = os.path.join(HIST_DIR["stock"], symbol)
        df.to_csv(filepath, index=False)
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_hist():
    stock_dir = HIST_DIR['stock']
    if not os.path.isdir(stock_dir):
        os.makedirs(stock_dir)

    df = pd.read_csv(SYM["all"], dtype={"symbol": str})
    symbols = df["symbol"].values
    pool = Pool(10)
    results = []
    for symbol in symbols:
        res = pool.apply_async(download_stock_hist, (symbol,))
        results.append(res)
    for i in trange(len(results)):
        res = results[i]
        res.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", action="store_true", default=False)
    parser.add_argument("--hist", action="store_true", default=False)
    args = parser.parse_args()
    if args.symbol:
        download_stock_symbols()
        download_index_symbols()
        sys.exit(0)
    if args.hist:
        download_hist()
        sys.exit(0)