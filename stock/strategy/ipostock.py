# -*- coding: utf-8 -*-

import Queue
from stock.filter.utils import *
from stock.utils.request import *
from stock.marketdata import *
from stock.marketdata.bar import Bar
from stock.utils.symbol_util import *
from stock.globalvar import *
import datetime
import re
import sys
import math
import json
import os.path

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
    zhuan = get_ipo_zhuan(exsymbol)
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
                state = 2
                continue

        i = i + 1
    return (price, total, zhuan)

def get_ipo_zhuan(exsymbol):
    symbol = exsymbol[2:]
    url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=NS&sty=NSD&stat=3&code=%s" % symbol
    req = Request()
    result = req.send_request(url)
    result = re.sub('^\(|\)$', '', result)
    data = json.loads(result)[0]
    return int(data[u'老股转让数量'])

def get_ipo_list():
    f = open(os.path.join(IPO_DIR, '2012'), 'r')
    content = f.read()
    f.close()
    lines = content.split('\n')
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        exsymbol = line.split(',')[0]
        (price, total, zhuan) = get_ipo_info(exsymbol)
        print "%s,%f,%d,%d" % (exsymbol, price, total, zhuan)
        i = i + 1

def get_stock_history():
    f = open(os.path.join(IPO_DIR, '2012'), 'r')
    content = f.read()
    f.close()
    lines = content.split('\n')
    req = Request()
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        exsymbol = line.split(',')[0]
        url = 'http://data.gtimg.cn/flashdata/hushen/daily/12/%s.js' % exsymbol
        filepath = os.path.join(IPO_DIR, exsymbol)
        req.download_file(url, filepath)
        print "downloaded %s" % exsymbol
        i = i + 1

def get_stock_data(exsymbol):
    history = get_history_in_file(exsymbol)
    print history

def get_history_in_file(exsymbol):
    file = os.path.join(IPO_DIR, exsymbol)
    f = open(file, "r")
    contents = f.read()
    f.close()
    lines = contents.split('\\n\\\n')

    history = []
    start = 0
    i = 1
    while i <= len(lines) - 2:
        line = lines[i]
        (date, o, close, high, low, volume) = line.split(' ')
        dt = datetime.datetime.strptime(date, "%y%m%d")
        bar = Bar(exsymbol, date=date, dt=dt, open=float(o), \
            close=float(close), high=float(high), low=float(low), \
            volume=float(volume))
        history.append(bar)
        i = i + 1

    return history

def get_ipo_symbol_table():
    f = open(os.path.join(IPO_DIR, '2012'), 'r')
    content = f.read()
    f.close()
    lines = content.split('\n')
    table = {}
    i = len(lines) - 2
    while i >= 1:
        line = lines[i]
        (exsymbol, price, total) = line.split(",")[0:3]
        table[exsymbol] = {'price': float(price), 'total': int(total)/100}
        i = i - 1

    return table

def get_accu_volume(history, i):
    total = 0
    k = 0
    while k <= i:
        total += history[k].volume
        k = k + 1
    return total

def get_max_price(history, i):
    num = 30
    k = i + 1
    max_price = 0
    max_i = 0
    while k <= i + num and k < len(history):
        if history[k].close > max_price:
            max_price = history[k].close
            max_i = k
        k = k + 1

    return (max_i, max_price)

def get_max_profit():
    table = get_ipo_symbol_table()
    pl = 0.0
    for (exsymbol,v) in table.iteritems():
        history = get_history_in_file(exsymbol)
        i = 1
        while i < len(history):
            zt_price = get_zt_price(history[i-1].close)
            if history[i].close != zt_price:
                break
            i = i + 1

        if i < len(history) - 1:
            accu_vol = get_accu_volume(history, i)
            ipo_vol = v['total']
            perc = accu_vol/ipo_vol
            (max_i, max_price) = get_max_price(history, i)
            max_vol = get_accu_volume(history, max_i)
            max_perc = max_vol / ipo_vol
            price_chg = max_price / history[i].close - 1
            pl += price_chg
            #print "%f,%f" % (history[i].close, max_price)
            print "%s,%d,%d,%f,%f,%.1f%%" % (exsymbol, i, max_i, perc, max_perc, price_chg * 100)

    print pl

def get_profit_volume():
    table = get_ipo_symbol_table()
    nod = 10
    pl = 0.0
    for (exsymbol,v) in table.iteritems():
        history = get_history_in_file(exsymbol)
        i = 1
        while i < len(history):
            zt_price = get_zt_price(history[i-1].close)
            if history[i].close != zt_price:
                break
            i = i + 1

        if i + 9 <= len(history) - 1:
            accu_vol = get_accu_volume(history, i - 1)
            next_vol = get_accu_volume(history, i + 9)
            ipo_vol = v['total']
            accu_perc = accu_vol/ipo_vol
            next_perc = (next_vol - accu_vol) / ipo_vol
            accu_chg = history[i + 9].close / history[i - 1].close - 1
            pl += accu_chg
            #print "%f,%f" % (history[i].close, max_price)
            print "%s,%f,%f,%.1f%%" % (exsymbol, accu_perc, next_perc, accu_chg * 100)

    print pl
if __name__ == "__main__":
    get_max_profit()
