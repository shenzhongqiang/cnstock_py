import datetime
import numpy as np
import scipy
from sklearn.svm import SVR
from sklearn.cross_validation import *
from sklearn import preprocessing
from sklearn import metrics
from sklearn import linear_model
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.utils.fuquan import *
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split

marketdata = backtestdata.BackTestData("160105")
index_hist = marketdata.get_archived_history_in_file("sh000001")
data = []
target = []
for i in range(len(index_hist)-1):
    this_bar = index_hist[i]
    last_bar = index_hist[i+1]
    data.append([last_bar.open, last_bar.close,
        last_bar.high, last_bar.low, last_bar.volume])
    target.append(this_bar.close/last_bar.close - 1)

target = np.array(target)
scaler = preprocessing.StandardScaler().fit(data)
X_train = scaler.transform(data)

pca = PCA(n_components=4, whiten=False)
X_pca = pca.fit_transform(X_train)

idx1 = np.nonzero(X_pca[:,0]>-2)[0]
idx2 = np.nonzero(X_pca[:,0]<=-1)[0]
idx = list(set(idx1) & set(idx2))
print len(idx), np.sum(target[idx])
plt.scatter(X_pca[idx,0], target[idx], s=5)
plt.show()
