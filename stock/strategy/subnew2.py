import json
import datetime
import numpy as np
import pandas as pd
import talib
import logging
import logging.config
from sklearn import linear_model
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.strategy.utils import get_exsymbol_history, get_history_by_date, get_history_on_date, is_open_buyable, is_sellable, is_zhangting
from stock.strategy.base import Strategy
from stock.marketdata.storefactory import get_store
from stock.trade.order import Order
from stock.trade.report import Report
from stock.exceptions import NoHistoryOnDate
from stock.globalvar import LOGCONF
from config import store_type

logger = logging.getLogger(__name__)

class SubnewStrategy(Strategy):
    def __init__(self, start, end, initial=1e6, params={
            "sl_ratio": 0.049,
            "tp_ratio": 0.10,
            "open_gap": 0.02,
        }):
        super(SubnewStrategy, self).__init__(start=start, end=end, initial=initial)
        self.order.set_params(params)
        self.store = get_store(store_type)
        self.params = params
        self.exsymbols = self.store.get_stock_exsymbols()

    def filter_stock(self, date):
        result = []
        for exsymbol in self.exsymbols:
            df = self.store.get(exsymbol)[:date]
            if date not in df.index:
                continue

            if len(df) >= 250 or len(df) < 22:
                continue

            df["chg"] = df.close.pct_change()
            df["max_vol"] = df.volume.shift(1).rolling(window=20).max()
            df["open_gap"] = df.open / df.close.shift(1) -1
            df["body"] = df.close - df.open
            decrease = False
            i = 1
            for i in range(1, len(df.index)):
                row = df.ix[i]
                row_yest = df.ix[i-1]
                if row.high < row_yest.high:
                    decrease = True
                    break

            if decrease == False:
                continue

            idx = df.index.get_loc(date)
            row = df.iloc[idx]
            yest_row = df.iloc[idx-1]
            prev_chg = yest_row.chg
            chg = row.chg
            if yest_row.volume > yest_row.max_vol and yest_row.body > 0 and \
                yest_row.chg > 0.095 and row.open_gap < self.params["open_gap"]:
                result.append(exsymbol)
        return result

    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f %s" %(
            self.start, self.end, self.initial, json.dumps(self.params)))
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= self.start) & (dates <= self.end)]
        state = 0
        days = 0
        buy_price = 0.0
        stop_price = 0.0
        record_high = 0.0
        for date in dates:
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            if state == 0:
                exsymbols = self.filter_stock(date)
                print exsymbols
                if len(exsymbols) == 0:
                    continue
                idx = np.random.randint(len(exsymbols))
                exsymbol = exsymbols[idx]
                df = self.store.get(exsymbol)[:date]
                if not is_open_buyable(df, date):
                    continue
                price = df.loc[date].open
                high = df.loc[date].high
                balance = self.order.get_account_balance()
                amount = int(balance / price / 100) * 100
                self.order.buy(exsymbol, price, dt, amount)
                buy_price = price
                record_high = buy_price
                stop_price = (1-self.params["sl_ratio"]) * price
                state = 1
                days += 1
                continue

            if state == 1:
                pos = self.order.get_positions()[0]
                df = self.store.get(pos.exsymbol)
                if not is_sellable(df, date):
                    state = -1
                    continue

                idx = df.index.get_loc(date)
                yest_bar = df.iloc[idx-1]
                today_bar = df.iloc[idx]
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                if today_bar.low <= stop_price:
                    self.order.sell(pos.exsymbol, stop_price, dt, pos.amount)
                    state = 0
                    days = 0
                    continue

                if days == 10:
                    self.order.sell(pos.exsymbol, today_bar.close, dt, pos.amount)
                    state = 0
                    days = 0
                    continue

                if today_bar.close > record_high:
                    stop_price = (1-self.params["sl_ratio"]) * today_bar.close
                    record_high = today_bar.close
                days += 1

            if state == 2:
                pos = self.order.get_positions()[0]
                df = self.store.get(pos.exsymbol)
                if not is_sellable(df, date):
                    state = -1
                    continue

                idx = df.index.get_loc(date)
                yest_bar = df.iloc[idx-1]
                today_bar = df.iloc[idx]
                if not is_zhangting(yest_bar.close, today_bar.close):
                    self.order.sell(pos.exsymbol, today_bar.close, dt, pos.amount)
                    state = 0
                    days = 0
                    continue

            if state == -1:
                df = self.store.get(pos.exsymbol)
                if is_sellable(df, date):
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
    strategy = SubnewStrategy(start='2017-09-01', end='2017-09-19')
    strategy.run()


