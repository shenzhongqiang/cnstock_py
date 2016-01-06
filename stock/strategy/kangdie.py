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

marketdata = backtestdata.BackTestData("160105")
index_hist = marketdata.get_archived_history_in_file("sh000001")
stock_hist = marketdata.get_archived_history_in_file("sh601169")

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
    if chg < -0.1:
        print i
    stock_chg.append(chg)

curr_chg = []
last_chg = []
for i in range(len(stock_chg) - 1):
    if stock_chg[i+1] < -0.02:
        curr_chg.append(stock_chg[i])
        last_chg.append(stock_chg[i+1])

plt.scatter(last_chg, curr_chg, 1)
plt.show()
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
