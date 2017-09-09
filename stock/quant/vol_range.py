import os
import cPickle as pickle
import scipy
import scipy.stats
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, exsymbol_to_symbol
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import tushare as ts
from config import store_type

def compute_vol_score(array):
    #score = scipy.stats.percentileofscore(array, array[-1])
    mean = np.mean(array)
    score = array[-1] / mean
    return score

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
df = store.get('sh600208')
df["range"] = df.high / df.low - 1
df["vol_score"] = df.volume.rolling(window=20).apply(compute_vol_score)
df_test = df.loc["2013-01-01":]
print df_test[df_test.close >= df_test.open][df_test.vol_score > 1][df_test.range < 0.03].sort_values(["vol_score"])
