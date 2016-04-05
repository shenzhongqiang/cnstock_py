import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, WeekdayLocator, DateFormatter, MONDAY, MonthLocator, MO
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.trade.order import *
from stock.trade.report import *

marketdata = backtestdata.BackTestData("160304")
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
df['ma'] = pd.rolling_mean(df.close, 20)
df['prevma'] = df.ma.shift(1)
df['std'] = pd.rolling_std(df.close, 20)
df['prevclose'] = df.close.shift(1)

df['chg'] = df.close.pct_change()
df['profit'] = pd.rolling_sum(df.chg, 5).shift(-5)
x_series = pd.Series(np.arange(len(df.index)), index=df.index)
df['slope'] = pd.ols(y=df.close, x=x_series, window=20).beta['x']
df.index = pd.to_datetime(df.index, format='%y%m%d')
df = df['2015-01-01': '2016-03-04']

df['deviation'] = (df['close'] - df['ma']) / df['std']
x = []
y = []
seq = np.linspace(-2, 4, 100)
for i in seq:
    result_df = df[df.ma > df.prevma][df.deviation.shift(1) < i][df.deviation > i]
    x.append(i)
    y.append(result_df['profit'].sum())


upper_factor = df[df.slope > 1].deviation.quantile(0.95)
lower_factor = df[df.slope > 1].deviation.quantile(0.05)
print lower_factor, upper_factor
df['lowerb'] = df['ma'] + df['std'] * lower_factor
df['prevlowerb'] = df.lowerb.shift(1)
df['upperb'] = df['ma'] + df['std'] * upper_factor
df['prevupperb'] = df.upperb.shift(1)
print df[df.slope > 1][df.close < df.lowerb]

'''
state = 0
engine = create_engine('sqlite://')
Base.metadata.create_all(engine)
order = Order(engine)
order.add_account(initial=100000)
amount = 0
stop_loss = 0
for date, row in df.iterrows():
    date_str = date.strftime('%y%m%d')
    if state == 0:
        if row.slope > 1 and row.close < row.lowerb:
            balance = order.get_account_balance()
            amount = int(balance/row.close)
            order.buy("sh000001", row.close, date_str, amount)
            stop_loss = row.close * 0.9
            state = 1
            continue
    if state == 1:
        if row.low <= stop_loss:
            order.sell("sh000001", stop_loss, date_str, amount)
            state = 0
            continue
        if row.prevclose > row.prevupperb and \
            row.close < row.upperb:
            order.sell("sh000001", row.close, date_str, amount)
            state = 0
            continue

report = Report(engine)
report.print_report()

fig = plt.figure()
dates = df.index
ax = fig.add_subplot(1,1,1)
ax.plot(dates, df.close, dates, df.lowerb, dates, df.upperb)
ax.xaxis.set_major_locator(WeekdayLocator(byweekday=MO, interval=2))
ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
ax.xaxis_date()
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
ax.legend(['close', 'lower band', 'upper band'])
plt.show()
'''

fig = plt.figure()
dates = df.index
ax = fig.add_subplot(1,1,1)
ax.plot(x, y)
plt.show()
