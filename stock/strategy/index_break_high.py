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
from stock.strategy.utils import get_exsymbol_history, get_history_by_date, get_history_on_date, is_sellable, is_buyable
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
            "high_days": 10,
            "low_days": 10}):
        super(IndexStrategy, self).__init__(start=start, end=end, initial=initial)
        self.order.set_params(params)
        self.store = get_store(store_type)
        self.params = params
        self.exsymbol = 'sh600208'


    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f %s" %(
            self.start, self.end, self.initial, json.dumps(self.params)))
        df = self.store.get(self.exsymbol)
        df["high10"] = df.high.rolling(window=self.params["high_days"]).max().shift(1)
        df["low10"] = df.low.rolling(window=self.params["low_days"]).min().shift(1)
        df_test = df.loc[self.start:self.end]
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= self.start) & (dates <= self.end)]
        state = 0
        days = 0
        buy_price = 0.0
        sell_limit = 0.0
        stop_loss = 0.0
        for date in dates:
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            if date not in df_test.index:
                continue
            if state == 0:
                today_bar = df_test.loc[date]
                if len(df_test.loc[:date]) < 2:
                    continue
                if not is_buyable(df_test, date):
                    continue

                if today_bar.close > today_bar.high10:
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
                if today_bar.close < today_bar.low10:
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
        #report.print_report()
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


