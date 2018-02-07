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
from stock.marketdata.storefactory import get_store
from stock.filter.utils import *
import matplotlib
from config import store_type
matplotlib.style.use('seaborn-paper')


x = []
y = []
store = get_store(store_type)
history = store.get('id000001')['2017-01-01':]
print history
dates = history.date
dates = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), dates)
highs = history.high
lows = history.low
opens = history.open
closes = history.close
volumes = history.volume


W = fftfreq(len(history.close))
W_max = np.max(W)
fft_close = rfft(history.close.values)
# set high frequency waves' magnitude to zero
#fft_close[abs(W) > W_max * 0.10] = 0
# select high magnitude waves only
index_toset = np.abs(fft_close).argsort()[:-6]
fft_close[index_toset] = 0
new_close = irfft(fft_close)
plt.plot(dates, new_close)
plt.plot(dates, closes)
plt.legend(['new'])
plt.show()
