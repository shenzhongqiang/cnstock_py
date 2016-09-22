import datetime
import sys
import copy
import numpy as np
import pandas as pd
from scipy.fftpack import rfft, irfft, fftfreq
from sklearn.svm import SVR
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, WeekdayLocator, DateFormatter, MONDAY, MonthLocator
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.filter.utils import *
import matplotlib
matplotlib.style.use('seaborn-paper')


symbols = get_stock_symbols('all')
marketdata = backtestdata.BackTestData("160105")
x = []
y = []
history = marketdata.get_archived_history_in_file("sh000001")
history.reverse()
dates = map(lambda x: x.date, history)
dates = map(lambda x: datetime.datetime.strptime(x, '%y%m%d'), dates)
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


W = fftfreq(df.close.size)
W_max = np.max(W)
fft_close = rfft(df.close.values)
fft_close[abs(W) > W_max * 0.10] = 0
new_close = irfft(fft_close)
plt.plot(dates, new_close)
plt.legend(['new'])
plt.show()
