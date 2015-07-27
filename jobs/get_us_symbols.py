#!/usr/bin/python
import os.path
import urllib
import urllib2
import json
from stock.globalvar import *
from stock.utils import request

if not os.path.isdir(SYMDIR):
    os.makedirs(SYMDIR)

base_url = "https://www.google.com/finance?%s"
tickers = []
start = 0
while True:
    query = {
        "output": "json",
        "start": str(start),
        "num": "200",
        "noIL": "1",
        "q": '[currency%20%3D%3D%20%22USD%22%20%26%20%28%28exchange%20%3D%3D%20%22OTCMKTS%22%29%20%7C%20%28exchange%20%3D%3D%20%22OTCBB%22%29%20%7C%20%28exchange%20%3D%3D%20%22NYSEMKT%22%29%20%7C%20%28exchange%20%3D%3D%20%22NYSEARCA%22%29%20%7C%20%28exchange%20%3D%3D%20%22NYSE%22%29%20%7C%20%28exchange%20%3D%3D%20%22NASDAQ%22%29%29%20%26%20%28market_cap%20%3E%3D%20200000000%29%20%26%20%28market_cap%20%3C%3D%20723390000000%29%20%26%20%28pe_ratio%20%3E%3D%200%29%20%26%20%28pe_ratio%20%3C%3D%2010796%29%20%26%20%28dividend_yield%20%3E%3D%200%29%20%26%20%28dividend_yield%20%3C%3D%203900000%29%20%26%20%28price_change_52week%20%3E%3D%20-101%29%20%26%20%28price_change_52week%20%3C%3D%2050901%29]',
        "restype": "company",
    }

    params = "&".join(map(lambda x: x + "=" + query[x], query.keys()))
    url = base_url % params
    req = request.Request()
    try:
        content = req.send_request(url)
        content = content.replace(r"\x", r"\\x")
        data = json.loads(content)
        results = map(lambda x: x["ticker"], data['searchresults'])
        tickers.extend(results)
        data_start = int(data["start"])
        data_num = int(data["num"])
        data_total = int(data["num_company_results"])
        print "%d/%d" % (len(tickers), data_total)
        if data_start + data_num >= data_total:
            break

        start = start + 200
    except Exception, e:
        print e

f = open(os.path.join(SYMDIR, "us_ticker"), "w")
f.write('\n'.join(tickers))
f.close()
