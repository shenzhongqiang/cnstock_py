import re
from stock.utils.request import *

class InvalidValue(Exception):
    pass

class InvalidPrice(Exception):
    pass

def get_all_funds():
    req = Request()
    result = req.send_request('http://www.howbuy.com/fund/ajax/board/index.htm',
        data={'glrm':'', 'keyword':'', 'radio':2, 'orderField': 'hbdr',
            'orderType': 'desc', 'cat': 't', 'level': ''})
    lines = map(lambda x: x.strip(), result.split("\n"))
    patt = re.compile(r'^<tr>')
    patt2 = re.compile(r'value="(\d+)"')
    funds = []
    for line in lines:
        if patt.search(line):
            m = patt2.search(line)
            funds.append(m.group(1))
    return funds

def get_fund_value(fund):
    req = Request()
    url = 'http://www.howbuy.com/fund/%s/' % fund
    result = req.send_request(url)
    lines = map(lambda x: x.strip(), result.split("\n"))
    patt = re.compile(r'<div class="cRed">|<div class="cGreen">')
    patt2 = re.compile(r'\d+')
    i = 0
    for line in lines:
        if patt.search(line):
            if patt2.search(lines[i+1]):
                return float(lines[i+1])
            else:
                raise InvalidValue()
        i = i + 1

def get_fund_price(fund):
    req = Request()
    url = 'http://www.howbuy.com/fund/ajax/gmfund/valuation/valuationnav.htm?jjdm=%s' % fund
    result = req.send_request(url)
    lines = map(lambda x: x.strip(), result.split("\n"))
    patt = re.compile(r'<span class="con_value[^>]+">([\d.]+)</span>')
    for line in lines:
        m = patt.search(line)
        if m:
            return float(m.group(1))

    raise InvalidPrice()

funds = get_all_funds()
to_sort = []
for fund in funds:
    try:
        value = get_fund_value(fund)
        price = get_fund_price(fund)
        perc = abs(value-price)/value
        to_sort.append({"value":value, "price":price, "perc":perc, "fund":fund})
    except Exception, e:
        print e

to_sort.sort(key=lambda x: x["perc"], reverse=True)
for fund in to_sort:
    print "%s %f %f %%%.2f" % (fund["fund"],
        fund["value"], fund["price"], fund["perc"] * 100)
