import re
import sys
import argparse
import os.path

from multiprocessing import Pool
from tqdm import trange
import requests
import pandas as pd

from stock.globalvar import HIST_DIR, SYM, BASIC_DIR

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


def download_concepts():
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://11.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:3+f:!50&fields=f12,f14".format(i, pz)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"symbol": x["f2"], "name": x["f14"]}, result))
    return result

def download_industries():
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://24.push2.eastmoney.com/api/qt/clist/get?pn={}&pz={}&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f12,f14".format(i, pz)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"symbol": x["f12"], "name": x["f14"]}, result))
    return result

def download_concept_stocks(concept_id):
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://push2.eastmoney.com/api/qt/clist/get?fid=f62&pn={}&po=1&pz={}&np=1&fltt=2&invt=2&fs=b%3A{}&fields=f12,f14".format(i, pz, concept_id)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"symbol": x["f12"], "name": x["f14"]}, result))
    return result

def download_industry_stocks(industry_symbol):
    pz = 500
    i = 1
    result = []
    while True:
        url = "https://push2.eastmoney.com/api/qt/clist/get?fid=f62&po={}&pz={}&pn=1&np=1&fltt=2&invt=2&fs=b%3A{}&fields=f12,f14".format(i, pz, industry_symbol)
        r = requests.get(url, verify=False)
        data = r.json()
        total = data["data"]["total"]
        items = data["data"]["diff"]
        result.extend(items)
        if (i-1)*pz+len(items) >= total:
            break
        i += 1
    result = list(map(lambda x: {"symbol": x["f12"], "name": x["f14"]}, result))
    return result

def download_all_concepts_stocks():
    concepts = download_concepts()
    s_concept_symbol = []
    s_concept_name = []
    s_symbol = []
    s_name = []
    for concept in concepts:
        concept_name = concept["name"]
        concept_symbol = concept["symbol"]
        stocks = download_concept_stocks(concept_symbol)
        symbols = list(map(lambda x: x["symbol"], stocks))
        names = list(map(lambda x: x["name"], stocks))
        s_concept_symbol.extend([concept_symbol]*len(stocks))
        s_concept_name.extend([concept_name]*len(stocks))
        s_symbol.extend(symbols)
        s_name.extend(names)
    df = pd.DataFrame({"concept_symbol": s_concept_symbol, "concept_name": s_concept_name, "symbol": s_symbol, "name": s_name})
    filepath = os.path.join(BASIC_DIR, "concept")
    df.to_csv(filepath, index=False)

def download_all_industries_stocks():
    industries = download_industries()
    s_industry_symbol = []
    s_industry_name = []
    s_symbol = []
    s_name = []
    for industry in industries:
        industry_name = industry["name"]
        industry_symbol = industry["symbol"]
        stocks = download_industry_stocks(industry_symbol)
        symbols = list(map(lambda x: x["symbol"], stocks))
        names = list(map(lambda x: x["name"], stocks))
        s_industry_symbol.extend([industry_symbol]*len(stocks))
        s_industry_name.extend([industry_name]*len(stocks))
        s_symbol.extend(symbols)
        s_name.extend(names)
    df = pd.DataFrame({"industry_symbol": s_industry_symbol, "industry_name": s_industry_name, "symbol": s_symbol, "name": s_name})
    filepath = os.path.join(BASIC_DIR, "industry")
    df.to_csv(filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", action="store_true", default=False)
    parser.add_argument("--hist", action="store_true", default=False)
    parser.add_argument("--concept", action="store_true", default=False)
    parser.add_argument("--industry", action="store_true", default=False)
    args = parser.parse_args()
    if args.symbol:
        download_stock_symbols()
        download_index_symbols()
        sys.exit(0)
    if args.hist:
        download_hist()
        sys.exit(0)
    if args.concept:
        download_all_concepts_stocks()
        sys.exit(0)
    if args.industry:
        download_all_industries_stocks()
        sys.exit(0)