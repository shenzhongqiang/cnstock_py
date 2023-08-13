import json
import datetime
import os.path
import requests
import pandas as pd
from tqdm import tqdm, trange
from lxml import etree
from multiprocessing import Pool
from stock.utils import request
import stock.utils.symbol_util
from stock.globalvar import FINANCE_DIR, BASIC_DIR
from stock.marketdata.storefactory import get_store

ZCFZB_URL = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/zcfzbAjaxNew?companyType=%s&reportDateType=0&reportType=1&dates=%s&code=%s"
LRB_URL = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/lrbAjaxNew?companyType=%s&reportDateType=0&reportType=1&dates=%s&code=%s"
XJLLB_URL = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/xjllbAjaxNew?companyType=%s&reportDateType=0&reportType=1&dates=%s&code=%s"
REPORT_DATES = ["%d-03-31", "%d-06-30", "%d-09-30", "%d-12-31"]

# check if directory exists, if not create directory
stock_dir = FINANCE_DIR['stock']
if not os.path.isdir(stock_dir):
    os.makedirs(stock_dir)
if not os.path.isdir(BASIC_DIR):
    os.makedirs(BASIC_DIR)


def split_dates(dates):
    result = []
    for i in range(0, len(dates), 4):
        end = min(i+4, len(dates))
        result.append(dates[i:end])
    return result


def get_company_type(exsymbol):
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=%s" % exsymbol
    r = requests.get(url)
    content = r.content.decode("utf-8")
    root = etree.HTML(content)
    values = root.xpath('.//input[@id="hidctype"]/@value')
    if len(values) != 1:
        raise Exception("cannot find hidctype for ", exsymbol)
    return values[0]


def parse(resp):
    dat = json.loads(resp)
    if "data" not in dat:
        return None
    data = dat["data"]
    df = pd.json_normalize(data)
    df.set_index("REPORT_DATE", inplace=True)
    df.sort_index(inplace=True, ascending=False)
    return df


def download_zcfzb(symbol, dates, company_type):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_zcfzb.csv" % exsymbol
        path = os.path.join(stock_dir, filename)
        group = split_dates(dates)
        df_res = None
        for i in range(len(group)):
            group_dates = group[i]
            date_str = ",".join(group_dates)
            url = ZCFZB_URL % (company_type, date_str, exsymbol)
            r = requests.get(url)
            content = r.content.decode("utf-8")
            df = parse(content)
            if df is None:
                return
            if i == 0:
                df_res = df
            else:
                df_res = pd.concat([df_res, df])
        df_res.to_csv(path)
    except Exception as e:
        print("error getting %s ZCFZB data due to %s" % (symbol, str(e)))

def download_lrb(symbol, dates, company_type):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_lrb.csv" % exsymbol
        path = os.path.join(stock_dir, filename)
        group = split_dates(dates)
        df_res = None
        for i in range(len(group)):
            group_dates = group[i]
            date_str = ",".join(group_dates)
            url = LRB_URL % (company_type, date_str, exsymbol)
            r = requests.get(url)
            content = r.content.decode("utf-8")
            df = parse(content)
            if df is None:
                return
            if i == 0:
                df_res = df
            else:
                df_res = pd.concat([df_res, df])
        df_res.to_csv(path)
    except Exception as e:
        print("error getting %s LRB data due to %s" % (symbol, str(e)))

def download_xjllb(symbol, dates, company_type):
    try:
        exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
        filename = "%s_xjllb.csv" % exsymbol
        path = os.path.join(stock_dir, filename)
        group = split_dates(dates)
        df_res = None
        for i in range(len(group)):
            group_dates = group[i]
            date_str = ",".join(group_dates)
            url = XJLLB_URL % (company_type, date_str, exsymbol)
            r = requests.get(url)
            content = r.content.decode("utf-8")
            df = parse(content)
            if df is None:
                return
            if i == 0:
                df_res = df
            else:
                df_res = pd.concat([df_res, df])
        df_res.to_csv(path)
    except Exception as e:
        print("error getting %s XJLLB data due to %s" % (symbol, str(e)))

def download_stock_finance(symbol, dates):
    exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
    company_type = get_company_type(exsymbol)
    download_zcfzb(symbol, dates, company_type)
    download_lrb(symbol, dates, company_type)
    download_xjllb(symbol, dates, company_type)


def report_dates(date):
    dt = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    result = []
    year = dt.year
    while True:
        q4_dt = datetime.date(year=year, month=12, day=31)
        if q4_dt <= dt:
            result.append(q4_dt)
        q3_dt = datetime.date(year=year, month=9, day=30)
        if q3_dt <= dt:
            result.append(q3_dt)
        q2_dt = datetime.date(year=year, month=6, day=30)
        if q2_dt <= dt:
            result.append(q2_dt)
        q1_dt = datetime.date(year=year, month=3, day=31)
        if q1_dt <= dt:
            result.append(q1_dt)
        if len(result) >= 12:
            break
        year = year - 1

    dates = []
    for dt in result:
        date_str = dt.strftime("%Y-%m-%d")
        dates.append(date_str)
    return dates


def download_earnings(today):
    pool = Pool(10)

    # get stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()

    results = []
    dates = report_dates(today)
    for symbol in symbols:
        res = pool.apply_async(download_stock_finance, (symbol, dates))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        res.wait()


def download_stock_basic(symbol):
    common_url = "https://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&fields=" + \
          "f58%2Cf734%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf170%2Cf152%2Cf177%2Cf111%2Cf46%2Cf60%2Cf44%2Cf45%2Cf47" + \
          "%2Cf260%2Cf48%2Cf261%2Cf279%2Cf277%2Cf278%2Cf288%2Cf19%2Cf17%2Cf531%2Cf15%2Cf13%2Cf11%2Cf20%2Cf18%2Cf16" + \
          "%2Cf14%2Cf12%2Cf39%2Cf37%2Cf35%2Cf33%2Cf31%2Cf40%2Cf38%2Cf36%2Cf34%2Cf32%2Cf211%2Cf212%2Cf213%2Cf214" + \
          "%2Cf215%2Cf210%2Cf209%2Cf208%2Cf207%2Cf206%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf84%2Cf85%2Cf168%2Cf108" + \
          "%2Cf116%2Cf167%2Cf164%2Cf162%2Cf163%2Cf92%2Cf71%2Cf117%2Cf292%2Cf51%2Cf52%2Cf191%2Cf192%2Cf262%2Cf294" + \
          "%2Cf295%2Cf269%2Cf270%2Cf256%2Cf257%2Cf285%2Cf286&secid="
    if stock.utils.symbol_util.is_sh(symbol):
        url = common_url + "1." + symbol
    else:
        url = common_url + "0." + symbol

    try:
        r = requests.get(url, verify=False)
        data = r.json()["data"]
        name = data["f58"]
        if data["f43"] == "-":
            return None
        close = data["f43"] / 100
        mcap = data["f116"]
        liquid_mcap = data["f117"]
        total_share_num = data["f84"]
        liquid_share_num = data["f85"]

        return {"symbol": symbol, "name": name, "close": close, "mcap": mcap, "liquid_mcap": liquid_mcap,
                "total_share": total_share_num, "liquid_share": liquid_share_num}
    except Exception as e:
        print("error getting history due to %s" % str(e))


def download_basics():
    pool = Pool(10)

    # get stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()

    results = []
    for symbol in symbols:
        res = pool.apply_async(download_stock_basic, (symbol,))
        results.append(res)

    basics = []
    for i in trange(len(results)):
        res = results[i]
        data = res.get()
        if data:
            basics.append(data)

    df = pd.DataFrame(basics)
    df.set_index("symbol", inplace=True)
    path = os.path.join(BASIC_DIR, "basics")
    df.to_csv(path)


if __name__ == "__main__":
    download_basics()
    download_earnings("2023-08-13")
