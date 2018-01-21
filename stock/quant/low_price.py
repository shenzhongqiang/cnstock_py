import sys
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
from stock.lib.finance import load_stock_basics
from stock.lib.candlestick import plot_price_volume_inday


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
result = pd.DataFrame(columns=["exsybmol", "close", "mcap"])
df_basics = load_stock_basics()
for exsymbol in exsymbols:
    if exsymbol not in df_basics.index:
        continue
    total_shares = df_basics.loc[exsymbol, "totals"]
    df = store.get(exsymbol)
    close = df.iloc[-1].close
    mcap = total_shares * close
    if close > 3 or mcap < 100:
        continue
    result.loc[len(result)] = [exsymbol, close, mcap]
print result
