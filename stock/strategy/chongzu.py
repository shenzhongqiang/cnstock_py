from datetime import datetime
import sys
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *

symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData(date="150605")
x=[]
y=[]
for exsymbol in symbols:
    try:
        history = marketdata.get_history_by_date(exsymbol)
        for i in range(len(history)-1):
            bar_today = history[i]
            bar_yest = history[i+1]
            dt_today = datetime.strptime(bar_today.date, '%y%m%d')
            dt_yest = datetime.strptime(bar_yest.date, '%y%m%d')
            delta = dt_today - dt_yest
            if delta.days >= 10 and delta.days < 90:
                zt_price = get_zt_price(bar_yest.close)
                if abs(zt_price - bar_today.close) > 1e-10:
                    chg = bar_today.close / bar_yest.close - 1
                    if chg < -0.11:
                        continue
                    chg2 = history[i-5].close / bar_today.close - 1
                    print "%s:%s,%d,%.2f" % (exsymbol, bar_today.date, delta.days, chg2 * 100)
                    x.append(delta.days)
                    y.append(chg2)

    except Exception, e:
        print "%s: %s" % (type(e), e.message)

x = np.array(x)
x = x.reshape(x.size, 1)
y = np.array(y)
plt.scatter(x, y, c='k', label='data')
plt.xlabel('data')
plt.ylabel('target')
plt.title('Support Vector Regression')
plt.legend()

plt.show()
