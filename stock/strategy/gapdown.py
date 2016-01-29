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
df['gapup'] = pd.Series(df.open / df.close.shift(1) - 1)
df.index = pd.to_datetime(df.index, format='%y%m%d')
df['chg'] = df['open'].pct_change().shift(-1)
#df['chg'] = df['close'] / df['open'] - 1
df['ma20'] = pd.rolling_mean(df.close, 20).shift(1)
result_df = df['2011-01-01': '2015-12-30']

result_df = result_df[result_df.ma20 < result_df.ma20.shift(1)]
gap_df = result_df[result_df.gapup < -0.003]
gap_df['negchg'] = gap_df.apply(lambda row: row['chg'] * -1.0, axis=1)
pl = (gap_df.negchg + 1).cumprod()
j = np.argmax(np.maximum.accumulate(pl) - pl)
i = np.argmax(pl[:j])
max_drawdown = pl[i] - pl[j]
print len(pl), max_drawdown, pl[-1]
fig = plt.figure()
ax2 = fig.add_subplot(1,1,1)
ax2.plot(pl)
plt.show()

#''' tuning code
x = []
y = []
z = []
d = []
for gap in np.linspace(-0.02, 0.02, 1000):
    gap_df = result_df[result_df.gapup < gap]
    if len(gap_df.values) < 30:
        continue
    #print gap
    gap_df['negchg'] = gap_df.apply(lambda row: row['chg'] * -1.0, axis=1)
    pl = (gap_df.negchg + 1).cumprod()
    j = np.argmax(np.maximum.accumulate(pl) - pl)
    i = np.argmax(pl[:j])
    max_drawdown = pl[i] - pl[j]
    x.append(gap)
    y.append(pl[-1])
    z.append(max_drawdown)
    d.append(gap_df.negchg.std())

fig, axes = plt.subplots(3, 1)
axes[0].plot(x, y)
axes[1].plot(x, z)
axes[2].plot(x, d)
plt.show()
#'''
