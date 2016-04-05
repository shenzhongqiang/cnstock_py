import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, WeekdayLocator, DateFormatter, MONDAY, MonthLocator, MO
from stock.utils.symbol_util import *
from stock.globalvar import *
from stock.marketdata import *
from stock.trade.order import *
from stock.trade.report import *

def get_max_drawdown(profit_series):
    if len(profit_series) == 0:
        return 0.0
    j = np.argmax(np.maximum.accumulate(profit_series) - profit_series)
    i = np.argmax(profit_series[:j+1])
    max_drawdown = profit_series[i] - profit_series[j]
    return max_drawdown

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
df['chg'] = df.close.pct_change()
df['chg_std'] = pd.rolling_std(df.chg, 20)
df['range'] = (df.high - df.low) / df.close.shift(1)
df['range_std'] = pd.rolling_std(df.range, 20)
df.range_std.hist(bins=20)
df['profit'] = pd.rolling_sum(df.chg, 5).shift(-5)
x_series = pd.Series(np.arange(len(df.index)), index=df.index)
df['slope'] = pd.ols(y=df.close, x=x_series, window=10).beta['x']
df.index = pd.to_datetime(df.index, format='%y%m%d')
df['deviation'] = (df['close'] - df['ma']) / df['std']
df['prevdev'] = df.deviation.shift(1)
df['min10'] = pd.rolling_min(df['low'], 10).shift(-10)
df['max10'] = pd.rolling_max(df['high'], 10).shift(-10)
df['factor'] = pd.rolling_quantile(df.deviation, 250, 0.85)
df['upperb'] = 1.5 * df['std'] + df['ma']
df['drawdown'] = (df.close - df.min10) / df.close
df['drawup'] = (df.max10 - df.close) / df.close
df['max_drawdown'] = pd.rolling_apply(df.close, 10, get_max_drawdown).shift(-10) / df.close

df = df['2012-01-01': '2014-01-01']
fig = plt.figure()
dates = df.index
ax = fig.add_subplot(2,1,1)
ax.plot(dates, df.close)
ax.xaxis.set_major_locator(WeekdayLocator(byweekday=MO, interval=2))
ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
ax.xaxis_date()
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
ax2 = fig.add_subplot(2,1,2)
ax2.plot(dates, df.chg_std, dates, df.range_std)
ax2.xaxis.set_major_locator(WeekdayLocator(byweekday=MO, interval=2))
ax2.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
ax2.xaxis_date()
ax2.legend(['chg std', 'range std'])
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
plt.show()
sys.exit(1)

entries = []
exits = []
seq = np.linspace(0.1, 0.9, 100)
X = []
Y = []
Z = []
for tp in seq:
    df['tp_factor'] = pd.rolling_quantile(df[df.ma > df.prevma].drawup, 500, 0.7)
    df['sl_factor'] = pd.rolling_quantile(df[df.ma > df.prevma].drawdown, 500, 0.9)
    df = df['2006-01-01': '2016-01-01']

    # trade
    state = 0
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    order = Order(engine)
    order.add_account(initial=100000)
    amount = 0
    entry = 0.0
    exit = 0.0
    stop_loss = 0
    days = 0
    for date, row in df.iterrows():
        date_str = date.strftime('%y%m%d')
        if state == 0:
            if row.ma > row.prevma and \
                row.prevdev < 1.5 and \
                row.deviation > 1.5:
                balance = order.get_account_balance()
                amount = int(balance/row.close)
                order.buy("sh000001", row.close, date_str, amount)
                entry = row.close
                stop_loss = row.close * (1 - row.sl_factor)
                entries.append([date, row.close])
                state = 1
                continue
        if state == 1:
            if days == 10:
                order.sell("sh000001", row.close, date_str, amount)
                exits.append([date, row.close])
                state = 0
                days = 0
                continue
            if row.low <= stop_loss:
                order.sell("sh000001", stop_loss, date_str, amount)
                exits.append([date, stop_loss])
                state = 0
                days = 0
                continue
            if row.high > entry * (1 + row.tp_factor):
                exit = entry * (1 + row.tp_factor)
                order.sell("sh000001", exit, date_str, amount)
                exits.append([date, exit])
                state = 0
                days = 0
                continue
            days += 1

    report = Report(engine)
    summary = report.get_summary()
    X.append(tp)
    Y.append(summary['profit'])
    Z.append(summary['max_drawdown'])
    print tp, summary['profit'], summary['max_drawdown'], summary['num_of_trades'], summary['win_rate']

    #fig = plt.figure()
    #dates = df.index
    #ax = fig.add_subplot(1,1,1)
    #ax.plot(dates, df.close, dates, df.upperb)
    #ax.xaxis.set_major_locator(WeekdayLocator(byweekday=MO, interval=2))
    #ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
    #ax.xaxis_date()
    #for point in entries:
    #    text = (point[0], point[1] * 0.88)
    #    ax.annotate('buy', xy=point, xytext=text,
    #        arrowprops=dict(arrowstyle="->", color='red'))
    #for point in exits:
    #    text = (point[0], point[1] * 1.08)
    #    ax.annotate('sell', xy=point, xytext=text,
    #        arrowprops=dict(arrowstyle="->", color='black'))
    #plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
    #ax.legend(['close', 'upper band'])
    #plt.show()

plt.plot(X, Y, X, Z)
plt.show()
