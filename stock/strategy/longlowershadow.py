import sys
import copy
import numpy as np
import pandas as pd
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick
from matplotlib.dates import date2num, WeekdayLocator, DateFormatter, MONDAY, MonthLocator
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *


symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData("160105")
x = []
y = []
history = marketdata.get_archived_history_in_file("sh000001")
history.reverse()
dates = map(lambda x: x.date, history)
highs = map(lambda x: x.high, history)
lows = map(lambda x: x.low, history)
opens = map(lambda x: x.open, history)
closes = map(lambda x: x.close, history)
volumes = map(lambda x: x.volume, history)
df = pd.DataFrame({"high": highs,
    "low": lows,
    "open": opens,
    "close": closes,
    "volume": volumes}, index=dates)
df['lower'] = (df.loc[:, ["open", "close"]].min(axis=1) - df.low) / df.close.shift(1)
df['chg'] = df['close'].pct_change().shift(-1)
df.index = pd.to_datetime(df.index, format='%y%m%d')
df['ma20'] = pd.rolling_mean(df.close, 20).shift(1)

result_df = df['2011-01-01': '2015-12-30']
result_df = result_df[result_df.lower > 0.04]
#result_df = result_df[result_df.ma20 > result_df.ma20.shift(1)]
result_df[['lower', 'chg']].plot(kind='scatter', x='lower', y='chg')
plt.show()
