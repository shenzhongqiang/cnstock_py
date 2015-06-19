import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *

def construct_data_target(history, i):
    num = 5
    y = history[i].close
    x = []
    for j in range(i+num, i, -1):
        x.append(history[j].open)
        x.append(history[j].close)
        x.append(history[j].high)
        x.append(history[j].low)
        x.append(history[j].volume)
    return (x,y)

def predict_close(history, i):
    days=3
    Xtrain = np.zeros((days,25))
    ytrain = np.zeros((days,))
    for k in range(days):
        [Xtrain[k], ytrain[k]] = construct_data_target(history,i+days-k)

    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=1e-4)
    model = svr_rbf.fit(Xtrain, ytrain)
    [xtest, yreal] = construct_data_target(history, i)
    y_predict =  model.predict(xtest)
    print "predict:%f, real:%f" % (y_predict, yreal)
    return (yreal, y_predict)

marketdata = backtestdata.BackTestData(date="150617")
history = marketdata.get_history_by_date("sh000001")

X = range(70)
yreal = np.zeros((70,))
ypredict = np.zeros((70,))
for i in X:
    [yreal[i], ypredict[i]] = predict_close(history,69-i)
plt.scatter(X, yreal, c='k', label='data')
plt.hold('on')
plt.plot(X, ypredict, c='g', label='RBF model')
plt.xlabel('data')
plt.ylabel('target')
plt.title('Support Vector Regression')
plt.legend()
plt.show()
