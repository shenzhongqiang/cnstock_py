import datetime
import json
import re
import sys
import argparse
import os.path

from multiprocessing import Pool
from tqdm import trange
import requests
import pandas as pd
import akshare as ak

from stock.globalvar import HIST_DIR, SYM, BASIC_DIR, REAL_DIR
from stock.utils.symbol_util import is_index_sh, is_sh, load_concept, load_industry


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


def download_wbond_symbols():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df = ak.bond_zh_cov()
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    df = df[df["上市时间"]!="-"]
    df["上市时间"] = pd.to_datetime(df["上市时间"])
    df = df[df["上市时间"]<today]
    df.to_csv(SYM['wbond'], index=False)


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
        url = "https://25.push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=0&end=20500101&lmt=500".format(symbol)
    else:
        url = "https://25.push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=0&end=20500101&lmt=500".format(symbol)
    try:
        r = requests.get(url, verify=False)
        data = r.json()
        df = get_hist_from_data(data)
        filepath = os.path.join(HIST_DIR["stock"], symbol)
        df.to_csv(filepath, index=False)
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_stock():
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


def download_index_hist(symbol):
    if is_index_sh(symbol):
        url = "http://99.push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=500".format(symbol)
    else:
        url = "http://99.push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=500".format(symbol)
    try:
        r = requests.get(url, verify=False)
        data = r.json()
        if data["data"] is None:
            return
        df = get_hist_from_data(data)
        filepath = os.path.join(HIST_DIR["index"], symbol)
        df.to_csv(filepath, index=False)
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_index():
    stock_dir = HIST_DIR['index']
    if not os.path.isdir(stock_dir):
        os.makedirs(stock_dir)

    df = pd.read_csv(SYM["id"], dtype={"symbol": str})
    symbols = df["symbol"].values
    pool = Pool(10)
    results = []
    for symbol in symbols:
        res = pool.apply_async(download_index_hist, (symbol,))
        results.append(res)
    for i in trange(len(results)):
        res = results[i]
        res.wait()


def download_group_hist(symbol):
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=90.{}&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=120".format(symbol)
    try:
        r = requests.get(url, verify=False)
        data = r.json()
        if data["data"] is None:
            return
        df = get_hist_from_data(data)
        filepath = os.path.join(HIST_DIR["group"], symbol)
        df.to_csv(filepath, index=False)
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_group():
    group_dir = HIST_DIR['group']
    if not os.path.isdir(group_dir):
        os.makedirs(group_dir)

    df_concept = load_concept()
    df_industry = load_industry()
    concept_symbols = df_concept["concept_symbol"].unique().tolist()
    industry_symbols = df_industry["industry_symbol"].unique().tolist()
    pool = Pool(10)
    results = []
    for symbol in concept_symbols + industry_symbols:
        res = pool.apply_async(download_group_hist, (symbol, ))
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
    result = list(map(lambda x: {"symbol": x["f12"], "name": x["f14"]}, result))
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

def download_stock_realtime(symbol):
    if is_sh(symbol):
        url = "http://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=2&fields=f43," + \
              "f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136," + \
              "f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183," + \
              "f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f260,f261,f262,f263,f264,f267,f268," + \
              "f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196," + \
              "f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287,f292,f293,f181,f294,f295,f279,f288" + \
              "&secid=1.{}".format(symbol)
    else:
        url = "http://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=2&fields=f43," + \
              "f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136," + \
              "f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183," + \
              "f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f260,f261,f262,f263,f264,f267,f268," + \
              "f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196," + \
              "f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287,f292,f293,f181,f294,f295,f279,f288" + \
              "&secid=0.{}".format(symbol)

    try:
        r = requests.get(url, verify=False)
        data = r.json()["data"]
        date_range_str = data["f80"]
        date_range = json.loads(date_range_str)
        date_str = str(date_range[0]["b"])[:8]
        return {"date": date_str, "name": data["f58"], "symbol": symbol, "b1_p": data["f19"], "b1_v": data["f20"],
                "open": data["f46"], "close": data["f43"], "yest_close": data["f60"], "volume": data["f47"]}
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_realtime():
    stock_dir = HIST_DIR['stock']
    if not os.path.isdir(stock_dir):
        os.makedirs(stock_dir)

    df = pd.read_csv(SYM["all"], dtype={"symbol": str})
    symbols = df["symbol"].values
    pool = Pool(10)
    results = []
    for symbol in symbols:
        res = pool.apply_async(download_stock_realtime, (symbol,))
        results.append(res)
    symbols = []
    names = []
    b1_p = []
    b1_v = []
    opens = []
    closes = []
    yest_closes = []
    volumes = []
    date_str = None
    for i in trange(len(results)):
        res = results[i]
        data = res.get()
        names.append(data["name"])
        symbols.append(data["symbol"])
        b1_p.append(data["b1_p"])
        b1_v.append(data["b1_v"])
        opens.append(data["open"])
        closes.append(data["close"])
        yest_closes.append(data["yest_close"])
        volumes.append(data["volume"])
        date_str = data["date"]
    df = pd.DataFrame({"name": names, "symbol": symbols, "open": opens, "close": closes, "yest_close": yest_closes,
                       "b1_p": b1_p, "b1_v": b1_v, "volume": volumes})
    df.set_index("symbol", inplace=True)
    dt = datetime.datetime.strptime(date_str, "%Y%m%d")
    filename = "{}.csv".format(dt.strftime("%Y-%m-%d"))
    filepath = os.path.join(REAL_DIR["daily"], filename)
    df.to_csv(filepath)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", action="store_true", default=False)
    parser.add_argument("--hist", action="store_true", default=False)
    parser.add_argument("--realtime", action="store_true", default=False)
    parser.add_argument("--concept", action="store_true", default=False)
    parser.add_argument("--industry", action="store_true", default=False)
    args = parser.parse_args()
    if args.symbol:
        download_stock_symbols()
        download_index_symbols()
        download_wbond_symbols()
        sys.exit(0)
    if args.hist:
        download_index()
        download_stock()
        download_group()
        sys.exit(0)
    if args.realtime:
        download_realtime()
        sys.exit(0)
    if args.concept:
        download_all_concepts_stocks()
        sys.exit(0)
    if args.industry:
        download_all_industries_stocks()
        sys.exit(0)
