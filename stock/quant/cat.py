import math
import numpy as np
import cPickle as pickle
import scipy.stats
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler

class RangeToCategory(BaseEstimator, TransformerMixin):
    def __init__(self, cat_num=10):
        self.cat_num = cat_num

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        result = []
        for i in range(self.cat_num):
            q = float(i+1) / self.cat_num * 100.0
            print q, np.percentile(X, q)

        for rowdata in X:
            score = scipy.stats.percentileofscore(X, rowdata)
            threshold = 100 - 100.0 / self.cat_num
            if score >= threshold:
                result.append(1)
            else:
                result.append(0)
        return np.array(result)

with open("output", "rb") as f:
    df = pickle.load(f)
    X = df.drop(["next_day_up", "exsymbol", "date"], axis=1)
    X_text = df[["exsymbol", "date"]].copy()
    y = df["next_day_up"].copy()
    std_tr = StandardScaler()
    X_scaled = std_tr.fit_transform(X)
    rtc = RangeToCategory()
    y_cat = rtc.transform(y)
    print y_cat
    svc = SVC(kernel="linear", gamma=5, C=0.001)
    svc.fit(X_scaled, y_cat)
    y_pre = svc.predict(X_scaled)
    scores = cross_val_score(svc, X_scaled, y_cat, scoring="accuracy", cv=10)
    print scores
