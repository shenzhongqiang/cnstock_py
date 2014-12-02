import threading
import Queue
from stock.filter import *
from stock.utils.request import *
from stock.marketdata import *
from stock.utils.symbol_util import *
from stock.globalvar import *
from datetime import datetime
import re
import sys
import math

def get_ipo_info(exsymbol):
    symbol = exsymbol[2:]
    url = 'http://data.eastmoney.com/xg/xg/detail/%s.html' % symbol
    req = Request()
    result = req.send_request(url)
    lines = result.split('\n')
    state = 0
    tr_count = 0
    i = 0
    price = 0
    total = 0
    zhuan = 0
    while i < len(lines):
        if state == 0 and \
            re.search('<table cellpadding="0" cellspacing="0" class="tab1">', lines[i]):
            state = 1
        if state == 1:
            if re.search('<tr>', lines[i]):
                tr_count = tr_count + 1
            if tr_count == 3:
                i = i + 5
                price = lines[i].strip()
                price = re.sub(r'&nbsp;', '', price)
                price = float(price)
                i = i + 9
                continue
            if tr_count == 7:
                i = i + 5
                total = lines[i].strip()
                total = re.sub(r'&nbsp;', '', total)
                total = re.sub(r',' , '', total)
                total = int(total)
                i = i + 9
                continue
            if tr_count == 8:
                i = i + 5
                zhuan = lines[i].strip()
                zhuan = re.sub(r'&nbsp;', '', zhuan)
                zhuan = 0 if zhuan == '' else int(zhuan)
                i = i + 9
                state = 2
                continue

        i = i + 1
    return (price, total, zhuan)


if __name__ == "__main__":
    f = open('ipolist', 'r')
    content = f.read()
    f.close()
    lines = content.split('\n')
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        exsymbol = line.split(',')[0]
        print exsymbol
        (price, total, zhuan) = get_ipo_info(exsymbol)
        print "%f, %d, %d" % (price, total, zhuan)
        i = i + 1
