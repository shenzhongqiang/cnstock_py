import re
import argparse
import datetime
import requests
import pandas as pd

def get_locking_period(locking):
    period = locking.rstrip("年")
    m = re.search(r"^([\d.]+)$", period)
    if m:
        start = float(m.group(1))
        return [start, start]
    m = re.search(r"^([\d.]+)\-([\d.]+)$", period)
    if m:
        start = float(m.group(1))
        end = float(m.group(2))
        return [start, end]

def get_dingzeng(date_str):
    url_patt = "https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=ISSUE_DATE&sortTypes=-1&pageSize=100&pageNumber={}&reportName=RPT_SEO_DETAIL&columns=ALL&quoteColumns=f2~01~SECURITY_CODE~NEW_PRICE&source=WEB&client=WEB&filter=(SEO_TYPE%3D%221%22)"
    i = 1
    while True:
        url = url_patt.format(i)
        r = requests.get(url, verify=False)
        data = r.json()
        stocks = data["result"]["data"]
        stop = False
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        for item in stocks:
            listing_date = item["ISSUE_LISTING_DATE"]
            listing_dt = datetime.datetime.strptime(listing_date, "%Y-%m-%d %H:%M:%S")
            if listing_dt < dt:
                stop = True
                break
            symbol = item["SECURITY_CODE"]
            name = item["SECURITY_NAME_ABBR"]
            try:
                raise_fund = float(item["TOTAL_RAISE_FUNDS"])
            except:
                raise_fund = float('nan')
            try:
                issue_price = float(item["ISSUE_PRICE"])
            except:
                issue_price = float('nan')
            try:
                new_price = float(item["NEW_PRICE"])
            except:
                new_price = float('nan')

            locking = item["LOCKIN_PERIOD"]
            if locking:
                [start, end] = get_locking_period(locking)
            chg = new_price/issue_price - 1
            if chg < 0:
                print("{},{},{},{},{:.3f}".format(symbol, listing_date, start, end, chg))

        i += 1
        if stop:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True, default=None, help="e.g. 2022-01-04")
    args = parser.parse_args()
    date_str = args.date
    get_dingzeng(date_str)
