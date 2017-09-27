import sys
import os
import cPickle as pickle
import scipy
import re
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.plotting import scatter_matrix
import seaborn as sns
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates, exsymbol_to_symbol
from stock.marketdata.storefactory import get_store
from stock.filter.utils import get_zt_price
from stock.lib.finance import get_lrb_data
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from config import store_type

def get_slope(array):
    x = range(len(array))
    reg = linear_model.LinearRegression()
    X = np.array(x).reshape(-1,1)
    reg.fit(X=X, y=array)
    return reg.coef_[0]

def get_quarter_profit(df):
    for i in range(len(df)):
        date = df.index[i]
        if i == 0:
            df.loc[date, "profit"] = np.nan

        dt = date.to_pydatetime()
        if dt.month > 3:
            df.loc[date, "profit"] = df.iloc[i].yylr - df.iloc[i-1].yylr
        else:
            df.loc[date, "profit"] = df.iloc[i].yylr

    return df

def plot_profit(exsymbol):
    df_lrb = get_lrb_data(exsymbol)
    get_quarter_profit(df_lrb)
    plt.plot(df_lrb.index, df_lrb["profit"])
    plt.show()

PLOT = False
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
if PLOT:
    df_lrb = get_lrb_data(sys.argv[2])
    get_quarter_profit(df_lrb)
    plt.plot(df_lrb.index[-12:], df_lrb.profit[-12:])
    plt.axhline(y=0.0, c='r')
    plt.show()
    sys.exit(1)

df_res = pd.DataFrame(columns=["exsymbol", "num"])
for exsymbol in exsymbols:
    df_lrb = get_lrb_data(exsymbol)
    get_quarter_profit(df_lrb)
    if len(df_lrb) < 12:
        continue
    profits_q1 = df_lrb[df_lrb.quarter=="Q1"].profit.iloc[-3:]
    profits_q2 = df_lrb[df_lrb.quarter=="Q2"].profit.iloc[-3:]
    profits_q3 = df_lrb[df_lrb.quarter=="Q3"].profit.iloc[-3:]
    profits_q4 = df_lrb[df_lrb.quarter=="Q4"].profit.iloc[-3:]
    if len(profits_q1) < 3 or \
        len(profits_q2) < 3 or \
        len(profits_q3) < 3 or \
        len(profits_q4) < 3:
        continue
    if profits_q1.isnull().any() or profits_q2.isnull().any() or profits_q3.isnull().any() or profits_q4.isnull().any():
        continue

    num = 0
    for i in range(len(df_lrb)-1, 0, -1):
        if df_lrb.profit[i] > df_lrb.profit[i-1]:
            num += 1
        else:
            break
    #if profits_q1[-1] < profits_q1[-2] or profits_q1[-2] < profits_q1[-3] or profits_q1[-3] < profits_q1[-4]:
    #    continue
    #if profits_q2[-1] < profits_q2[-2] or profits_q2[-2] < profits_q2[-3] or profits_q2[-3] < profits_q2[-4]:
    #    continue
    #if profits_q3[-1] < profits_q3[-2] or profits_q3[-2] < profits_q3[-3] or profits_q3[-3] < profits_q3[-4]:
    #    continue
    #if profits_q4[-1] < profits_q4[-2] or profits_q4[-2] < profits_q4[-3] or profits_q4[-3] < profits_q4[-4]:
    #    continue

    print exsymbol, num
    df_res.loc[len(df_res)] = [exsymbol, num]

print df_res.sort_values(["num"])
