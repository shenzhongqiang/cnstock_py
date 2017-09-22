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

def get_quarter_profit(df):
    for i in range(len(df)):
        date = df.index[i]
        if i == 0:
            df.loc[date, "profit"] = np.nan

        dt = date.to_datetime()
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

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_res = pd.DataFrame(columns=["exsymbol", "h2_incr", "h1_incr"])
for exsymbol in exsymbols:
    df_lrb = get_lrb_data(exsymbol)
    if len(df_lrb) < 6:
        continue
    get_quarter_profit(df_lrb)
    df_res.loc[len(df_res)] = [exsymbol, df_lrb.iloc[-1].profit / df_lrb.iloc[-5].profit, df_lrb.iloc[-2].profit / df_lrb.iloc[-6].profit]
    #plt.plot(df_lrb.index, df_lrb["profit"])
    #plt.axhline(y=0.0, c='r')
    #plt.show()

print df_res.sort_values(["h2_incr"]).tail(10)
