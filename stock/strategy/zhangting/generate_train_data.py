import sys
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *

if len(sys.argv) < 4:
    sys.stderr.write('Usage: %s <exsymbol> <date> <1|0>\n' % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
date = sys.argv[2]
yesno = sys.argv[3]
marketdata = backtestdata.BackTestData(date=date)
try:
    bars = marketdata.get_history_by_date(exsymbol)
    print "%s,%s,%f,%f,%f,%f,%f,%f,%f,%s" % (
        exsymbol,
        date,
        bars[3].close/bars[4].close - 1,
        bars[2].open/bars[3].close - 1,
        bars[2].close/bars[3].close - 1,
        bars[1].open/bars[2].close - 1,
        bars[1].close/bars[2].close - 1,
        bars[0].open/bars[1].close - 1,
        bars[0].close/bars[1].close - 1,
        yesno
    )
except Exception, e:
    print "%s: %s" % (type(e), e.message)
