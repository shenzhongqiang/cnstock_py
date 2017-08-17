import os
import math
import numpy as np
import cPickle as pickle
import pandas as pd
import scipy.stats
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class RangeToCategory(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=0.05):
        self.threshold = threshold

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        result = []
        for rowdata in X:
            if rowdata >= self.threshold:
                result.append(1)
            else:
                result.append(0)
        return np.array(result)

def search_hyperparams(clf, X, y):
    param_grid = [{'n_estimators': [3,10,30]}]
    grid_search = GridSearchCV(clf, param_grid, cv=10, scoring="accuracy")
    grid_search.fit(X_train, y_train)
    cvres = grid_search.cv_results_
    print grid_search.best_params_
    print grid_search.best_estimator_
    print cvres.keys()
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print mean_score, params

def test_data(df):
    print len(df.date.unique())
    print df[df.index_up < -0.015].date.unique()
    s2 = df.groupby('date').apply(lambda subf: (subf["today_up"] - subf["minus_index"]).iloc[0])
    df_test = df[df.trade_vol<5e7]
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.scatter(df_test.trade_vol, df_test.next_week_high, alpha=0.1)
    ax2.scatter(df_test.chg_std, df_test.next_week_high, alpha=0.1)
    plt.show()

folder = os.path.dirname(__file__)
infile = os.path.join(folder, "output")
with open(infile, "rb") as f:
    df = pickle.load(f)
    df["index_up"] = df.today_up - df.minus_index
    df_train = df.loc[:'2016-12-31']
    test_data(df_train)
    df_test = df.loc['2017-01-01':]
    X_train_orig = df_train.drop(["next_day_up", "next_open_gap", "next_week_high", "exsymbol", "date"], axis=1)
    X_train_text = df_train[["exsymbol", "date", "next_open_gap"]].copy()
    y_train_up = df_train["next_day_up"].copy()
    std_tr = StandardScaler()
    X_train_std = std_tr.fit_transform(X_train_orig)
    #pca = PCA(n_components=2)
    #X_train = pca.fit_transform(X_train_std)
    #print pca.explained_variance_ratio_
    X_train = X_train_std
    rtc = RangeToCategory()
    y_train = rtc.transform(y_train_up)

    X_test_orig = df_test.drop(["next_day_up", "next_open_gap", "next_week_high", "exsymbol", "date"], axis=1)
    X_test_text = df_test[["exsymbol", "date", "next_open_gap"]].copy()
    y_test_up = df_test["next_day_up"].copy()
    X_test_std = std_tr.fit_transform(X_test_orig)
    #X_test = pca.fit_transform(X_test_std)
    X_test = X_test_std
    y_test = rtc.transform(y_test_up)

    clf = RandomForestClassifier(n_estimators=30, class_weight="balanced", max_depth=11)
    clf.fit(X_train, y_train)
    scores = cross_val_score(clf, X_train, y_train, scoring="accuracy", cv=10)
    print "===== RandomForestClassifier ====="
    print scores
    y_pre = clf.predict(X_test)
    ids = np.where(y_pre==1)
    print y_test[ids]
    print df.iloc[ids]

