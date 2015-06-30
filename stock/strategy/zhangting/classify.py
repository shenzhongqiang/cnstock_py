import os.path
import sys
import numpy as np
from sklearn.svm import SVC
from sklearn.cross_validation import *
from sklearn import preprocessing
from sklearn import metrics
from sklearn import linear_model
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <date>\n' % sys.argv[0])
    sys.exit(1)

date = sys.argv[1]
filepath = os.path.join(os.path.dirname(__file__),
    "train")
f = open(filepath)
contents = f.read()
f.close()

lines = contents.split("\n")
X = []
y = []
for line in lines:
    if line == "":
        continue

    data = line.split(",")
    pattern = map(lambda x: float(x), data[2:9])
    X.append(pattern)
    y.append(int(data[9]))

X = np.array(X)
y = np.array(y)
clf = linear_model.SGDClassifier().fit(X, y)

ypred = clf.predict(X)
print metrics.accuracy_score(y, ypred)

symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData(date=date)
for exsymbol in symbols:
    try:
        bars = marketdata.get_history_by_date(exsymbol)
        pattern = [
            bars[3].close/bars[4].close - 1,
            bars[2].open/bars[3].close - 1,
            bars[2].close/bars[3].close - 1,
            bars[1].open/bars[2].close - 1,
            bars[1].close/bars[2].close - 1,
            bars[0].open/bars[1].close - 1,
            bars[0].close/bars[1].close - 1,
        ]
        pred = clf.predict([pattern])
        if pred[0] == 1:
            print exsymbol
    except Exception, e:
        print "%s: %s" % (type(e), e.message)
