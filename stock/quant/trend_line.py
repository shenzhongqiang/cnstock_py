import os
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

TEST = False

store = get_store(store_type)
df=store.get("sz000428").loc["2016-01-01":]
df["std_close"] = df.close.rolling(window=10).apply(np.std) / df.close
print df.sort_values(["std_close"], ascending=False)
import sys
sys.exit(1)

def get_trend_resid(y):
    x_seq = np.arange(len(y))
    x = x_seq.reshape(-1, 1)

    reg = linear_model.LinearRegression()
    percent = 0
    x_train = x.copy()
    y_train = y.copy()
    while percent < 0.9 and len(y_train) > 3:
	reg.fit(x_train, y_train)
	pred = reg.predict(x)
	percent = (y>pred).sum() *1.0 / len(y)

	pred_train = reg.predict(x_train)
	x_train = x_train[y_train<pred_train]
	y_train = y_train[y_train<pred_train]

    pred_y = reg.predict(x)
#    plt.plot(x_seq, y, c='b')
#    plt.plot(x_seq, pred_y, c='r')
#    plt.show()
    return reg

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)

df = store.get('id000001')
columns = ["date", "cross_num", "profit"]
result = pd.DataFrame(columns=columns)
reg = linear_model.LinearRegression()

for date in df.loc["2014-07-01":].index:
    idx = df.index.get_loc(date)
    if idx > len(df) - 10:
        break
    df_train = df.iloc[idx-30:idx+1]
    df_test = df.iloc[idx+1:idx+10]
    data = df_train.low.values
    idx = np.argmin(data)
    if idx > 0:
        continue
    train_data = data[idx:]
    data_len = len(train_data)
    profit = df_test.iloc[:10].close.max() / df_train.iloc[-1].close - 1
    reg = get_trend_resid(train_data)
    train_x = np.arange(data_len).reshape(-1, 1)
    pred_y = reg.predict(train_x)
    cross_num = 0
    for i in range(data_len-1):
        if pred_y[i] > train_data[i] and pred_y[i+1] < train_data[i+1]:
            cross_num += 1
    if cross_num >=2 and train_data[data_len-2] < pred_y[data_len-2] and train_data[data_len-1]>=pred_y[data_len-1]:
        result.loc[len(result)] = [date, cross_num, profit]
print result
