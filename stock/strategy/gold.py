import datetime
import pandas as pd
import scipy.stats
import scipy.misc
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, HourLocator, DayLocator, WeekdayLocator, DateFormatter, MONDAY, MonthLocator, MO
from stock.trade.order import *
from stock.trade.report import *

df = pd.read_csv(
    "../exp/src/main/java/history/XAUUSDm5",
    header=None,
    names=[
        "time", "bo", "bc", "bh", "bl", "ao", "ac", "ah", "al", "vol"],
    index_col=0,
    parse_dates=True)[::-1]

df["spread"] = df["ac"] - df["bc"]
df["ind_h"] = pd.rolling_max(df.ah, window=50).shift(1)
df["ind_h_prev"] = df.ind_h.shift(1)
df["ah_prev"] = df.ah.shift(1)
df["drawdown"] = 1 - pd.rolling_min(df.al, 20).shift(-20) / df.ac
df.drawdown = df.drawdown.shift(20)
df["sl_ratio"] = pd.rolling_quantile(df["drawdown"], 250, 0.9)
df["drawup"] = pd.rolling_max(df.ah, 20).shift(-20) / df.ac - 1
df = df["2016-03-01": "2016-03-02"]
#fig = plt.figure()
#dates = df.index
#ax = fig.add_subplot(1,1,1)
#ax.plot(dates, df.ac, dates, df.ind_h)
#ax.xaxis.set_major_locator(HourLocator(byhour=range(24), interval=4))
#ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d %H"))
#ax.xaxis_date()
#plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
#ax.legend(['close', 'high'])
#plt.show()

df['tp_ratio'] = pd.rolling_quantile(df.drawup, 250, 0.7)

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
entries = []
exits = []
for date, row in df.iterrows():
    if state == 0:
        if row.ind_h <= row.ah and \
            row.ind_h_prev > row.ah_prev:
            balance = order.get_account_balance()
            amount = int(balance/row.ind_h)
            order.buy("XAUUSD", row.ind_h, date, amount)
            entry = row.ind_h
            stop_loss = row.ind_h * (1 - row.sl_ratio)
            entries.append([date, row.ind_h])
            state = 1
            continue
    if state == 1:
        if days == 20:
            order.sell("XAUUSD", row.ac, date, amount)
            exits.append([date, row.ac])
            state = 0
            days = 0
            continue
        if row.al <= stop_loss:
            order.sell("XAUUSD", stop_loss, date, amount)
            exits.append([date, stop_loss])
            state = 0
            days = 0
            continue
        if row.al > entry * (1 + row.tp_ratio):
            exit = entry * (1 + row.tp_ratio)
            order.sell("XAUUSD", exit, date, amount)
            exits.append([date, exit])
            state = 0
            days = 0
            continue
        days += 1

report = Report(engine)
summary = report.get_summary()
report.print_report()

fig = plt.figure()
dates = df.index
ax = fig.add_subplot(1,1,1)
ax.plot(dates, df.ah, dates, df.ind_h)
ax.xaxis.set_major_locator(HourLocator(byhour=range(24), interval=4))
ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d-%H"))
ax.xaxis_date()
for point in entries:
    text = (point[0], point[1] * 0.995)
    ax.annotate('buy', xy=point, xytext=text,
        arrowprops=dict(arrowstyle="->", color='red'))
for point in exits:
    text = (point[0], point[1] * 1.005)
    ax.annotate('sell', xy=point, xytext=text,
        arrowprops=dict(arrowstyle="->", color='black'))
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
ax.legend(['close', 'high'])
plt.show()
