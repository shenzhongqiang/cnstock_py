from datetime import datetime
import sys
import numpy as np
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.utils.fuquan import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *
import traceback

def get_low(history, n):
    result = []
    if len(history) < n:
        raise Exception("timeseries too short")

    i = 0
    while i < len(history):
        if i < n-1:
            result.append({"time": history[i].date, "value": 0.0})
        else:
            closes = map(lambda x: x.low, history[i-n+1:i+1])
            low = min(closes)
            result.append({"time": history[i].date, "value": low})
        i+=1
    return result

def get_first_order_diff(timeseries):
    result = []
    i = 0
    while i < len(timeseries):
        if i == 0:
            result.append({"time": timeseries[i]["time"], "value": 0})
        else:
            diff = timeseries[i]["value"] - timeseries[i-1]["value"]
            result.append({"time": timeseries[i]["time"], "value": diff})
        i+=1
    return result

def norm_series(timeseries):
    values = map(lambda x: x["value"], timeseries)
    lowest = values[0]
    for i in range(len(timeseries)):
        timeseries[i]["value"] = timeseries[i]["value"] / lowest

def find_start(history, end, price):
    k = end - 1
    while k >= 0:
        if price < history[k].high and price > history[k].low:
            break
        k-=1
    return k

symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData(date="151031")
lm = LinearRegression()
print "exsymbol\ttime\tlen\tcoef\tmse\tavg\tdiff"
for exsymbol in symbols:
    try:
        history = marketdata.get_archived_history_in_file(exsymbol)
        Fuquan.fuquan_history(history)
        history.reverse()
        k = 100
        while k < len(history):
            price = history[k].high
            start = find_start(history, k, price)
            start = k - 22
            if start < 0:
                k+=1
                continue
            n = k - start - 1
            if n < 20 or n > 100:
                k+=1
                continue
            hist = history[start-1:k]
            low_20 = min(map(lambda x: x.low, hist))
            low_100 = min(map(lambda x: x.low, history[k-100:k]))
            if (low_20 - low_100) > 1e-10:
                k+=1
                continue
            seq = range(n)
            X = np.array([seq]).T
            lowseries = map(lambda x: {"time": x.date, "value": x.low}, hist)
            norm_series(lowseries)
            first_order_diff = get_first_order_diff(lowseries)

            time = history[k].date
            m = len(first_order_diff)
            diff = first_order_diff[m-1]["value"]
            data = map(lambda x: x["value"], first_order_diff[m-n:m])
            Y = np.array(data) * 1e3
            avg = np.mean(Y)
            lm.fit(X,Y)
            mse = np.mean((Y - lm.predict(X)) ** 2)
            #if lm.coef_[0] > 2 and mse < 1000 and diff > 0 and abs(avg) < 0.1:
            if lm.coef_[0] > 1 and mse < 150 and diff > 0:
                print "%s\t%s\t%d\t%0.3f\t%0.3f\t%0.3f\t%0.5f" % (exsymbol, time, n, lm.coef_[0], mse, avg, diff)
            k+=1

            #bar_today = history[i]
            #bar_yest = history[i+1]
            #dt_today = datetime.strptime(bar_today.date, '%y%m%d')
            #dt_yest = datetime.strptime(bar_yest.date, '%y%m%d')
            #delta = dt_today - dt_yest
            #if delta.days >= 10 and delta.days < 90:
            #    zt_price = get_zt_price(bar_yest.close)
            #    if abs(zt_price - bar_today.close) > 1e-10:
            #        chg = bar_today.close / bar_yest.close - 1
            #        if chg < -0.11:
            #            continue
            #        chg2 = history[i-5].close / bar_today.close - 1
            #        print "%s:%s,%d,%.2f" % (exsymbol, bar_today.date, delta.days, chg2 * 100)
            #        x.append(delta.days)
            #        y.append(chg2)
    except Exception, e:
        print "%s: %s" % (type(e), e.message)
        traceback.print_exc()
