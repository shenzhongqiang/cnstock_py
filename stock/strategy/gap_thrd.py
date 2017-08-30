import datetime
import numpy as np
import pandas as pd
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

class GapStrategy(Strategy):
    def __init__(self, start, end, initial=1e6, thrd=0.0005, pred_thrd=0.02, sl_thrd=0.01):
        super(GapStrategy, self).__init__(start=start, end=end, initial=initial)
        self.order.set_params({
            "thrd": thrd,
            "pred_thrd": pred_thrd,
            "sl_thrd": sl_thrd,
        })
        self.store = get_store(store_type)
        self.thrd = thrd
        self.pred_thrd = pred_thrd
        self.sl_thrd = sl_thrd
        self.exsymbol = 'id000001'

    def train(self, df_stock):
        df_stock["open_gap"] = df_stock.open / df_stock.close.shift(1) - 1
        df_stock["chg"] = df_stock.close.pct_change()
        df_stock["volume_yest"] = df_stock.volume.shift(1)# + df_stock.volume.shift(2) + df_stock.volume.shift(3)
        max_profits = []
        for i in xrange(len(df_stock) - 6):
            s = pd.Series(df_stock.iloc[i+1:i+6].high.max(), index=[df_stock.index[i]])
            max_profits.append(s)
        df_stock["max_profit"] = pd.concat(max_profits) / df_stock.open - 1

        min_profits = []
        for i in xrange(len(df_stock) - 6):
            s = pd.Series(df_stock.iloc[i+1:i+6].low.min(), index=[df_stock.index[i]])
            min_profits.append(s)
        df_stock["min_profit"] = pd.concat(min_profits) / df_stock.close - 1
        df_test = df_stock.dropna(how="any")
        df_test = df_test[df_test.open_gap > self.thrd]
        X = df_test[["volume_yest", "open_gap"]].copy()
        y = df_test[["max_profit", "min_profit"]].copy()
        clf = linear_model.LinearRegression()
        clf.fit(X, y)
        return clf

    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f thrd=%f pred_thrd=%f" %(
            self.start, self.end, self.initial, self.thrd, self.pred_thrd))
        df = self.store.get(self.exsymbol)
        df_test = df.loc[self.start:self.end]
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= self.start) & (dates <= self.end)]
        state = 0
        days = 0
        buy_price = 0.0
        sell_limit = 0.0
        stop_loss = 0.0
        for date in dates:
            start_id = df.index.get_loc(date)
            df_train = df.iloc[start_id-700:start_id]
            if date not in df_test.index:
                continue
            if state == 0:
                clf = self.train(df_train)
                today_bar = df.loc[date]
                today_id = df.index.get_loc(date)
                yest_bar = df.iloc[today_id-1]
                volume_yest = yest_bar.volume
                open_gap = today_bar.open / yest_bar.close - 1
                if open_gap < self.thrd:
                    continue
                X = np.array([[volume_yest, open_gap]])
                y = clf.predict(X)
                if y[0][0] < self.pred_thrd:
                    continue
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                balance = self.order.get_account_balance()
                amount = int(balance / today_bar.open / 100) * 100
                self.order.buy(self.exsymbol, today_bar.open, dt, amount)
                pos = self.order.get_positions()
                buy_price = today_bar.open
                sell_limit = (y[0][0] + 1) * today_bar.open
                stop_loss = (1-self.sl_thrd) * buy_price
                if y[0][1] >= 0:
                    stop_loss = (1-self.sl_thrd) * buy_price
                else:
                    ratio = max(y[0][1], -1.0 * self.sl_thrd)
                    stop_loss = (1+ratio) * buy_price
                print sell_limit, stop_loss
                state = 1
                days += 1
                continue

            if state == 1:
                pos = self.order.get_positions()[0]
                if not is_sellable(df_test, date):
                    state = -1
                    continue

                try:
                    today_bar = df.loc[date]
                    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                    if today_bar.low <= stop_loss:
                        self.order.sell(pos.exsymbol, stop_loss, dt, pos.amount)
                        state = 0
                        days = 0
                        continue

                    if today_bar.high > sell_limit:
                        self.order.sell(pos.exsymbol, sell_limit, dt, pos.amount)
                        state = 0
                        days = 0
                    else:
                        days += 1
                        if days == 6:
                            self.order.sell(pos.exsymbol, today_bar.close, dt, pos.amount)
                            state = 0
                            days = 0
                    continue
                except NoHistoryOnDate, e:
                    #print pos.exsymbol, date
                    pass

            if state == -1:
                if is_sellable(df_test, date):
                    pos = self.order.get_positions()[0]
                    today_bar = df.loc[date]
                    self.order.sell(pos.exsymbol, today_bar.open, dt, pos.amount)
                    state = 0
                    days = 0

        account_id = self.order.get_account_id()
        report = Report(account_id)
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
    strategy = GapStrategy(start='2016-07-01', end='2017-07-01')
    strategy.run()

