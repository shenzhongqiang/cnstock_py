import os
import cPickle as pickle
import scipy
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from sklearn import linear_model
import matplotlib.pyplot as plt
from config import store_type

def get_slope(x, y):
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=y)
    return reg.coef_[0]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('id000001')
dates_len = len(df_index.date)
start_date = df_index.index[0]
columns = ["exsymbol", "pl", "std", "plstd", "date_min", "date_max"]
result = pd.DataFrame(columns=columns)
index_history = store.get('id000001')

for exsymbol in exsymbols:
    df = store.get(exsymbol)
    if len(df) < 100:
        continue
    try:
        idx = df.index.get_loc('2017-01-16')
        days = 66
        df_test = df.iloc[idx-days:idx]
        if len(df_test) == 0:
            continue
        date_min = df_test.close.argmin()
        date_max = df_test.loc[date_min:].close.argmax()
        if len(df_test.loc[:date_min]) == 1:
            continue
        pl = df.loc[date_max].close / df.loc[date_min].close
        closes = df_test.loc[date_min:date_max].close / df_test.loc[date_min].close
        opens = df_test.loc[date_min:date_max].open / df_test.loc[date_min].close
        highs = df_test.loc[date_min:date_max].high / df_test.loc[date_min].close
        lows = df_test.loc[date_min:date_max].low / df_test.loc[date_min].close
        series = np.append(closes, [opens, highs, lows])
        std = np.std(series)
        plstd = pl / std
        result.loc[len(result)] = [exsymbol, pl, std, plstd, date_min, date_max]
    except KeyError, e:
        print exsymbol, str(e)
    except IndexError, e:
        print exsymbol, str(e)

pd.set_option('display.max_rows', None)
print result[result.pl >= result.pl.quantile(0.95)].sort_values(['pl', 'std'], ascending=False)
