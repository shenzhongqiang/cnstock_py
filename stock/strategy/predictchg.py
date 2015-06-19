import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *

def construct_data_target(history, i):
    today_chg = history[i].close / history[i+1].close - 1
    yest_chg = history[i+1].close / history[i+2].close - 1
    opengap = history[i].open / history[i+1].close - 1
    return (yest_chg, opengap, today_chg)

marketdata = backtestdata.BackTestData(date="150617")
history = marketdata.get_history_by_date("sh000001")

x = []
y = []
z = []
for i in range(90, 0, -1):
    (yest_chg, opengap, today_chg) = construct_data_target(history, i)
    x.append(yest_chg)
    y.append(opengap)
    z.append(today_chg)

plt.scatter(x, y, c=z, label='data')
plt.xlabel('data')
plt.ylabel('target')
plt.title('Support Vector Regression')
plt.colorbar()
plt.legend()
plt.show()

