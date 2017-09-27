import json
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import talib
import logging
import logging.config
from sklearn import linear_model
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.strategy.utils import get_exsymbol_history, get_history_by_date, get_history_on_date, is_sellable
from stock.strategy.base import Strategy
from stock.marketdata.storefactory import get_store
from stock.trade.order import Order
from stock.trade.report import Report
from stock.exceptions import NoHistoryOnDate
from stock.globalvar import LOGCONF
from config import store_type

logger = logging.getLogger(__name__)

class IndexStrategy(Strategy):
    def __init__(self, start, end, initial=1e6, params={
            "upper": 0.00,
            "lower": -0.01}):
        super(IndexStrategy, self).__init__(start=start, end=end, initial=initial)
        self.order.set_params(params)
        self.store = get_store(store_type)
        self.params = params
        self.exsymbol = 'id000001'


    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f %s" %(
            self.start, self.end, self.initial, json.dumps(self.params)))
        df = self.store.get(self.exsymbol)
        df["ma"] = df.close.rolling(window=20).mean()
        df["bias"] = (df.close - df.ma)/df.ma
        df["diff_min"] = df.close / df.close.rolling(window=90).min() - 1
        df["std_close"] = df.close.rolling(window=10).std() / df.close
        df_test = df.loc[self.start:self.end]
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= self.start) & (dates <= self.end)]
        state = 0
        days = 0
        buy_price = 0.0
        sell_limit = 0.0
        stop_loss = 0.0
        open_env = pd.DataFrame(columns=["open_date", "diff_min", "std_close"])
        for date in dates:
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            if date not in df_test.index:
                continue
            if state == 0:
                today_bar = df.loc[date]
                if today_bar.bias > self.params["upper"]:# and today_bar.diff_min < 0.20 and today_bar.std_close > 0.01:
                    open_env.loc[len(open_env)] = [dt, today_bar.diff_min, today_bar.std_close]
                    balance = self.order.get_account_balance()
                    amount = int(balance / today_bar.close / 100) * 100
                    self.order.buy(self.exsymbol, today_bar.close, dt, amount)
                    pos = self.order.get_positions()
                    state = 1
                    days += 1
                    continue

            if state == 1:
                pos = self.order.get_positions()[0]
                if not is_sellable(df_test, date):
                    state = -1
                    continue

                today_bar = df.loc[date]
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                if today_bar.bias < self.params["lower"]:
                    self.order.sell(pos.exsymbol, today_bar.close, dt, pos.amount)
                    state = 0
                    days = 0
                    continue

            if state == -1:
                if is_sellable(df_test, date):
                    pos = self.order.get_positions()[0]
                    today_bar = df.loc[date]
                    self.order.sell(pos.exsymbol, today_bar.open, dt, pos.amount)
                    state = 0
                    days = 0

        account_id = self.order.get_account_id()
        report = Report(account_id)
        df_rep = report.get_closed_tranx_df()
        df_result = pd.merge(open_env, df_rep, on="open_date")
        pd.set_option('display.max_rows', None)
        diff_thrd = df_result.diff_min.quantile(0.95)
        std_thrd = df_result.std_close.quantile(0.1)
        print diff_thrd, std_thrd
        print df_result.groupby(pd.cut(df_result['diff_min'], np.linspace(np.min(df_result.diff_min), np.max(df_result.diff_min), 10))).mean()
        #fig = plt.figure()
        #ax1 = fig.add_subplot(411)
        #ax2 = fig.add_subplot(412)
        #ax3 = fig.add_subplot(413)
        #ax4 = fig.add_subplot(414)
        #ax1.scatter(df_result.diff_min, df_result.pl, c='b')
        #ax1.set_title("diff_min")
        #ax2.scatter(df_result.std_close, df_result.pl, c='b')
        #ax2.set_title("std_close")
        #ax3.hist(df_result.diff_min, bins=8)
        #ax3.set_title("diff_min")
        #ax4.hist(df_result.std_close, bins=8)
        #ax4.set_title("std_close")
        #plt.show()
        report.print_report()
        result = report.get_summary()
        logger.info("profit=%f, max_drawdown=%f, num_of_trades=%d, win_rate=%f, comm_total=%f, params=%s" % (
            result.profit,
            result.max_drawdown,
            result.num_of_trades,
            result.win_rate,
            result.comm_total,
            result.params))
        return result

if __name__ == "__main__":
    logging.config.fileConfig(LOGCONF)
    strategy = IndexStrategy(start='2010-01-01', end='2017-07-01')
    strategy.run()


