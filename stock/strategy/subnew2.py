import timeit
from functools import partial
import multiprocessing
import traceback
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
from stock.strategy.stock_simple_base import StockSimpleStrategy
from stock.trade.order import Order
from stock.trade.report import Report
from stock.exceptions import NoHistoryOnDate
from stock.globalvar import LOGCONF
from stock.lib.finance import load_stock_basics

logger = logging.getLogger(__name__)

def pre_calc(exsymbol, df):
    df["chg"] = df.close.pct_change()
    df["prev_chg"] = df.chg.shift(1)
    df["pprev_chg"] = df.chg.shift(2)
    df["ppprev_chg"] = df.chg.shift(3)
    df["vol_incr"] = df.volume.shift(1) / df.volume.shift(2).rolling(window=20).mean()
    df["opengap"] = df.open / df.close.shift(1) -1
    df["close_std"] = df.close.shift(2).rolling(window=20).std() / df.close.shift(2)
    df["recent_up_ratio"] = df.close.shift(1) /  df.close.shift(2).rolling(window=20).min() -1
    return (exsymbol, df)

class SubnewStrategy(StockSimpleStrategy):
    def __init__(self, start, end, initial=1e6, params={
            "sl_ratio": 0.05,
            "open_gap": 0.05,
            "max_pos": 5,
        }):

        super(SubnewStrategy, self).__init__(start=start, end=end, initial=initial)
        self.order.set_params(params)
        self.params = params
        self.stock_data = pd.DataFrame(columns=["break_idx"])
        pool = multiprocessing.Pool(10)
        async_res = []
        for exsymbol, df in self.history.iteritems():
            res = pool.apply_async(pre_calc, (exsymbol, df,))
            async_res.append(res)
        for res in async_res:
            [exsymbol, df] = res.get()
            self.set_exsymbol_history(exsymbol, df)
        pool.terminate()

        for exsymbol, df in self.history.iteritems():
            break_idx = np.nan
            for i in range(1, len(df.index)):
                row = df.ix[i]
                row_yest = df.ix[i-1]
                if row.high < row_yest.high:
                    break_idx = i
                    break
            self.stock_data.loc[exsymbol] = break_idx

    def filter_stock(self, date):
        result = []
        i = 0
        while i < len(self.exsymbols):
           exsymbol = self.exsymbols[i]
           df = self.get_exsymbol_history(exsymbol)[:date]
           if date not in df.index:
               continue

           if len(df) >= 250 or len(df) < 22:
               continue

           # break_idx = self.stock_data.loc[exsymbol].break_idx
           # if break_idx == np.nan:
           #     continue
           # idx = df.index.get_loc(date)
           # if break_idx >= idx:
           #     continue
           # row = df.iloc[idx]
           # if row.prev_chg > 0.099 and \
           #     row.opengap < self.params["open_gap"] and \
           #     row.pprev_chg < -0.03 and \
           #     row.ppprev_chg < -0.03 and \
           #     row.vol_incr < 1:
           #     result.append([exsymbol, row])
           i += 1
        result.sort(key=lambda x: x[1].close_std, reverse=True)
        max_pos = self.params["max_pos"]
        result = map(lambda x: x[0], result)[:max_pos]
        return result

    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f %s" %(
            self.start, self.end, self.initial, json.dumps(self.params)))
        state = 0
        days = 0
        buy_price = 0.0
        stop_price = 0.0
        record_high = 0.0
        positions = []
        closed_exsymbols = []
        max_pos = self.params["max_pos"]
        for date in self.trading_dates:
            print date, len(positions)
            print positions
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            for i in range(len(positions)):
                pos = positions[i]
                pos_row = self.order.get_position(pos["exsymbol"])
                if pos["state"] == 1:
                    df = self.get_exsymbol_history(pos_row.exsymbol)
                    if not is_sellable(df, date):
                        pos["state"] = -1
                        continue
                    idx = df.index.get_loc(date)
                    yest_bar = df.iloc[idx-1]
                    today_bar = df.iloc[idx]
                    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                    pos["days"] += 1
                    if today_bar.open <= pos["sl_price"]:
                        self.order.sell(pos_row.exsymbol, today_bar.open, dt, pos_row.amount)
                        closed_exsymbols.append(pos["exsymbol"])
                    elif today_bar.low <= pos["sl_price"]:
                        self.order.sell(pos_row.exsymbol, pos["sl_price"], dt, pos_row.amount)
                        closed_exsymbols.append(pos["exsymbol"])
                    elif days == 22:
                        self.order.sell(pos_row.exsymbol, today_bar.close, dt, pos_row.amount)
                        closed_exsymbols.append(pos["exsymbol"])
                    elif today_bar.close > pos["record_high"]:
                        pos["record_high"] = today_bar.close
                        pos["sl_price"] = (1-self.params["sl_ratio"]) * pos["record_high"]
                elif pos["state"] == -1:
                    if is_sellable(df, date):
                        self.order.sell(pos_row.exsymbol, today_bar.open, dt, pos_row.amount)
                        closed_exsymbols.append(pos["exsymbol"])

            positions = filter(lambda x: x["exsymbol"] not in closed_exsymbols, positions)
            if len(positions) < max_pos:
                print timeit.Timer(partial(self.filter_stock, date)).repeat(1, 1)
                import sys
                sys.exit(1)
                exsymbols = self.filter_stock(date)
                if len(exsymbols) == 0:
                    continue
                num_to_buy = min(max_pos - len(positions), len(exsymbols))
                for i in range(num_to_buy):
                    exsymbol = exsymbols[i]
                    df = self.get_exsymbol_history(exsymbol)[:date]
                    if not is_open_buyable(df, date):
                        continue
                    price = df.loc[date].open
                    high = df.loc[date].high
                    balance = self.order.get_account_balance()
                    amount = int(balance / max_pos / price / 100) * 100
                    self.order.buy(exsymbol, price, dt, amount)
                    buy_price = price
                    record_high = buy_price
                    stop_price = (1-self.params["sl_ratio"]) * price
                    state = 1
                    days += 1
                    positions.append({
                        "exsymbol": exsymbol,
                        "sl_price": stop_price,
                        "record_high": record_high,
                        "days": days,
                        "state": state
                    })
                    continue

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
    strategy = SubnewStrategy(start='2011-09-30', end='2017-09-30')
    strategy.run()


