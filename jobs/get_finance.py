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


if __name__ == "__main__":
    pool = Pool(10)

    # get stock symbols
    symbols = stock.utils.symbol_util.get_stock_symbols()

    results = []
    dates = report_dates("2023-01-01")
    for symbol in symbols:
        res = pool.apply_async(download_stock_finance, (symbol, dates))
        results.append(res)

    for i in trange(len(results)):
        res = results[i]
        res.wait()

