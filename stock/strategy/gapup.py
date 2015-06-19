import sys
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <date>\n' % sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData(date=date)
x = []
y = []
for exsymbol in symbols:
    try:
        history = marketdata.get_history_by_date(exsymbol)
        bar0 = history[0]
        bar1 = history[1]
        bar2 = history[2]
        vol = bar0.volume
        if vol == 0:
            print "%s no volume" % exsymbol
            continue
        if bar0.date != date:
            #print "%s no volume" % exsymbol
            continue
        if bar0.high == bar0.low:
            continue

        zt_price = get_zt_price(bar2.close)
        if abs(zt_price - bar1.close) < 1e-10:
            gapup = (bar0.open - bar1.close) / bar1.close
            dayup = (bar0.close - bar0.open) / bar1.close
            x.append(gapup)
            y.append(dayup)
            #print "%s\t%.4f\t%.4f" % (exsymbol, gapup, dayup)
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
