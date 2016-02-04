import datetime
import numpy as np
import scipy
from sklearn.svm import SVR
from sklearn.cross_validation import *
from sklearn import preprocessing
from sklearn import metrics
from sklearn import linear_model
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.utils import fuquan

def func(exsymbol, lower, upper=-0.05):
    marketdata = backtestdata.BackTestData("160105")
    index_hist = marketdata.get_archived_history_in_file("sh000001")
    stock_hist = marketdata.get_archived_history_in_file(exsymbol)
    fuquan.fuquan_history(index_hist)
    fuquan.fuquan_history(stock_hist)

    i = 0
    synced_index_hist = []
    for data in index_hist:
        if stock_hist[i].dt < data.dt:
            #raise Exception("stock miss trading days %s" % data.date)
            continue
        synced_index_hist.append(data)
        i+=1

    i = 0

    for data in synced_index_hist:
        if stock_hist[i].dt != data.dt:
            raise Exception("still not in sync")
        i+=1

    index_chg = []
    stock_chg = []

    for i in range(len(synced_index_hist)-1):
        chg = index_hist[i].close / index_hist[i+1].close - 1
        index_chg.append(chg)
        chg = stock_hist[i].close / stock_hist[i+1].close - 1
        stock_chg.append({"chg": chg, "dt": stock_hist[i].dt})

    trades = []
    for i in range(len(stock_chg) - 1):
        #if stock_chg[i+1]["chg"] < upper and stock_chg[i+1]["chg"] > -0.09:
        if stock_chg[i+1]["chg"] >= lower and stock_chg[i+1]["chg"] < upper : #and stock_chg[i+1]["chg"] > -0.09:
            # in case -10.00%
            j = i
            while stock_chg[j]["chg"] < -0.0995:
                stock_chg[i]["chg"] += stock_chg[j-1]["chg"]
                j-=1
            #if stock_chg[i] < -0.08:
            #    print "warning: %s, %d, %f, %f, %f" % (exsymbol, i, stock_chg[i], stock_chg[i-1], stock_chg[i-2])
            trades.append({"exsymbol": exsymbol, "dt": stock_chg[i+1]["dt"], "chg": stock_chg[i]["chg"], "last_chg": stock_chg[i+1]["chg"]})

    #print "%0.4f\t%0.4f\t%d" % (np.sum(curr_chg), np.mean(curr_chg)/np.var(curr_chg), len(curr_chg))
    return trades
    #plt.scatter(last_chg, curr_chg, 1)
    #plt.show()
    #index_chg_pos = []
    #stock_chg_pos = []
    #for i in range(len(index_chg)):
    #    if index_chg[i] > 0.03:
    #        index_chg_pos.append(index_chg[i])
    #        stock_chg_pos.append(stock_chg[i])
    #
    #hist, bins = np.histogram(index_chg, bins=30, range=(-0.101, 0.101))
    #plt.hist(stock_chg, bins=bins)
    #plt.show()

def tuning(lower, upper):
    a = ["sh601169", "sh601939", "sh601009", "sh601818",
    "sh601398", "sh601288", "sh600036", "sh601988",
    "sh601328", "sh601998", "sh600016", "sh601166",
    "sh600000", "sh600015", "sz002142", "sz000001"]
    trades = []
    point_x = []
    point_y = []
    for exsymbol in a:
        stock_trades = func(exsymbol, lower, upper)
        stock_trades.sort(key=lambda x: x["dt"])
        for trade in stock_trades:
            x = trade["last_chg"]
            y = trade["chg"]
            point_x.append(x)
            point_y.append(y)
        chgs = map(lambda x: x["chg"], stock_trades)
        total = [0.0,]
        for chg in chgs:
            total.append(total[-1]+chg)
        #print "%s %f" % (stock_trades[0]["exsymbol"], sum(chgs))
        #plt.plot(total)
        #plt.show()
        trades.extend(stock_trades)
    return point_x, point_y
    #return trades

seq = np.linspace(-0.09, 0.090, 20)
for i in range(len(seq)-1):
    lower = seq[i]
    upper = seq[i+1]
    [point_x, point_y] = tuning(lower, upper)
    print np.mean(point_x), np.mean(point_y), len(point_y)


#for upper in seq:
#    #upper = 0.0
#    trades = tuning(upper)
#    pl = sum(map(lambda x: x["chg"], trades))
#    print "%f %f" % (upper, pl)
#    #trades.sort(key=lambda x: x["dt"])

#merged = []
#dt = None
#for trade in trades:
#    if trade["dt"] != dt:
#        merged.append({"dt": trade["dt"], "trades":[{
#            "exsymbol": trade["exsymbol"],
#            "chg": trade["chg"]
#        }]})
#        dt = trade["dt"]
#    else:
#        merged_len = len(merged)
#        merged[merged_len-1]["trades"].append({
#            "exsymbol": trade["exsymbol"],
#            "chg": trade["chg"]
#        })
#
#capital = 1.0
#for item in merged:
#    date = item["dt"].strftime("%Y-%m-%d")
#    pl = sum(map(lambda x: x["chg"], item["trades"])) / len(item["trades"])
#    capital = capital * (1+pl)
#    print "%s %f %d" % (date, pl, len(item["trades"]))

#print "%0.5f,%0.5f,%0.5f" % (upper, np.sum(pl), np.mean(pl)/np.var(pl))
