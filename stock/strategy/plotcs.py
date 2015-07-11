import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
from matplotlib.finance import candlestick
from stock.strategy.utils import *

history = get_complete_history("sh000001")[0:20]
quotes = []
for bar in history:
    quotes.append([date2num(bar.dt),
        bar.open,
        bar.close,
        bar.high,
        bar.low])

fig = plt.figure()
ax = fig.add_subplot(111)
candlestick(ax, quotes, width=0.6)
ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
delta = datetime.timedelta(days=10)
ax.set_xlim(history[19].dt - delta, history[0].dt + delta)
ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')

plt.show()
