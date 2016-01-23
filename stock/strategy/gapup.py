import sys
import copy
import numpy as np
import pandas as pd
from sklearn.svm import SVR
import matplotlib.pyplot as plt
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
df['gapup'] = pd.Series(df.open / df.close.shift(1) - 1)
df.index = pd.to_datetime(df.index, format='%y%m%d')
df['chg'] = df['open'].pct_change().shift(-1)
df['ma20'] = pd.rolling_mean(df.close, 20).shift(1)
result_df = df['2015-01-01': '2016-01-01']
result_df = result_df[result_df.ma20 > result_df.ma20.shift(1)]

gap_df = result_df[result_df.gapup > 0.002]
pl = (gap_df.chg + 1).cumprod()
plt.plot(pl)
plt.show()

''' tuning code
x = []
y = []
z = []
for gap in np.linspace(-0.02, 0.02, 100):
    gap_df = result_df[result_df.gapup > gap]
    if len(gap_df.values) < 30:
        continue
    pl = (gap_df.chg + 1).prod()
    x.append(gap)
    y.append(pl)
    z.append(gap_df['chg'].std())

fig, axes = plt.subplots(2, 1)
axes[0].scatter(x, y)
axes[1].scatter(x, z)
plt.show()
'''
