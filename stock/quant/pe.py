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
from stock.lib.finance import load_stock_basics

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

def generate_middle():
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()

    date = "2017-04-28"
    df_res = pd.DataFrame(columns=["exsymbol", "incr_ratio", "pe", "mcap", "past_profit", "future_profit"])
    for exsymbol in exsymbols:
        try:
            df_lrb = get_lrb_data(exsymbol).loc[:date]
            get_quarter_profit(df_lrb)
            if len(df_lrb) < 16:
                continue
            profits_q1 = df_lrb[df_lrb.quarter=="Q1"].profit.iloc[-3:]
            profits_q2 = df_lrb[df_lrb.quarter=="Q2"].profit.iloc[-3:]
            profits_q3 = df_lrb[df_lrb.quarter=="Q3"].profit.iloc[-3:]
            profits_q4 = df_lrb[df_lrb.quarter=="Q4"].profit.iloc[-3:]
            year_profits = df_lrb[df_lrb.quarter=="Q4"].yylr
            if len(profits_q1) < 3 or \
                len(profits_q2) < 3 or \
                len(profits_q3) < 3 or \
                len(profits_q4) < 3:
                continue
            if df_lrb.iloc[-16:].profit.isnull().any():
                continue
            if np.sum(df_lrb.iloc[-16:].profit <= 0) > 0:
                continue
            low1 = df_lrb.loc["2014-01-01":"2014-12-31"].profit.min()
            low2 = df_lrb.loc["2015-01-01":"2015-12-31"].profit.min()
            low3 = df_lrb.loc["2016-01-01":"2016-12-31"].profit.min()
            if low3 < low2 or low2 < low1:
                continue
            #if profits_q1[-1] < profits_q1[-2] or profits_q1[-2] < profits_q1[-3] or profits_q1[-3] < profits_q1[-4]:
            #    continue
            #if profits_q2[-1] < profits_q2[-2] or profits_q2[-2] < profits_q2[-3] or profits_q2[-3] < profits_q2[-4]:
            #    continue
            #if profits_q3[-1] < profits_q3[-2] or profits_q3[-2] < profits_q3[-3] or profits_q3[-3] < profits_q3[-4]:
            #    continue
            #if profits_q4[-1] < profits_q4[-2] or profits_q4[-2] < profits_q4[-3] or profits_q4[-3] < profits_q4[-4]:
            #    continue

            df = store.get(exsymbol)
            if date not in df.index:
                continue
            if year_profits[-1] > year_profits[-2] and year_profits[-2] > year_profits[-3]:
                price = df.loc[date].close
                df_basics = load_stock_basics()
                total_shares = df_basics.loc[exsymbol, "totals"]
                mcap = total_shares * price
                slope = get_slope(np.log(df_lrb.profit[-16:]))
                pe = mcap / year_profits[-1] * 10000
                future_profit = df.iloc[-1].close / price - 1
                past_profit = price / df.loc["2017-01-01":].iloc[0].close - 1
                print exsymbol, slope, pe
                df_res.loc[len(df_res)] = [exsymbol, slope, pe, mcap, past_profit, future_profit]
        except Exception, e:
            print str(e)

    df_res.to_csv("/tmp/pe.csv")

def parse_middle(filepath="/tmp/pe.csv"):
    df= pd.read_csv(filepath, encoding="utf-8")
    df["score"] = df.incr_ratio/ df.pe
    print df[df.mcap<1000].sort_values(["future_profit"], ascending=False)
    print df.corr()["future_profit"]
    #print df.sort_values(["incr_ratio"])

if __name__ == "__main__":
    #generate_middle()
    parse_middle()
    PLOT = True
    if PLOT:
        df_lrb = get_lrb_data(sys.argv[1])
        get_quarter_profit(df_lrb)
        plt.plot(df_lrb.index[-16:], df_lrb.profit[-16:])
        #plt.axhline(y=0.0, c='r')
        plt.show()
