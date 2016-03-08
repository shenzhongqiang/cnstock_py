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
from stock.trade.order import *
from stock.trade.report import *
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
df['ma20prev'] = df.ma20.shift(1)
result_df = df['2015-01-01': '2016-03-04']
state = 0
#engine = create_engine('sqlite:///' + DBFILE, echo=False)
engine = create_engine('sqlite://')
Base.metadata.create_all(engine)
order = Order(engine)
order.add_account(initial=100000)
amount = 0
for date, row in result_df.iterrows():
    date_str = date.strftime('%y%m%d')
    if state == 0:
        if row.ma20 > row.ma20prev and row.gapup > 0.002:
            balance = order.get_account_balance()
            amount = int(balance/row.open)
            order.buy("sh000001", row.open, date_str, amount)
            state = 1
            continue
    if state == 1:
        if row.ma20 > row.ma20prev and row.gapup > 0.002:
            continue
        order.sell("sh000001", row.open, date_str, amount)
        state = 0

report = Report(engine)
report.print_report()
#gapup_df = result_df[result_df.ma20 > result_df.ma20.shift(1)]
#gapup_df = gapup_df[gapup_df.gapup > 0.002]
#gapup_df['money_chg'] = gapup_df.chg
#
#gapdown_df = result_df[result_df.ma20 < result_df.ma20.shift(1)]
#gapdown_df = gapdown_df[gapdown_df.gapup < -0.003]
#gapdown_df['money_chg'] = gapdown_df.apply(lambda row: row['chg'] * -1.0, axis=1)
#
#final_df = pd.concat([gapup_df, gapdown_df])
#final_df = final_df.sort_index()
#pl = (final_df.money_chg + 1).cumprod()
#j = np.argmax(np.maximum.accumulate(pl) - pl)
#i = np.argmax(pl[:j])
#max_drawdown = pl[i] - pl[j]
#print len(pl), max_drawdown, pl[-1]
#
#fig = plt.figure()
#ax2 = fig.add_subplot(1,1,1)
#ax2.plot(pl)
#plt.show()
