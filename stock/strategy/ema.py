import datetime
import numpy as np
import talib
import logging
import logging.config
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

class EmaStrategy(Strategy):
    def __init__(self, start, end, initial=80000, fast=5, slow=7, target=1.1):
        super(EmaStrategy, self).__init__(start=start, end=end, initial=initial)
        self.store = get_store(store_type)
        self.fast = fast
        self.slow = slow
        self.target = target
        self.exsymbols = self.store.get_stock_exsymbols()

    def rank_stock(self, date, exsymbols):
        scores = []
        for exsymbol in exsymbols:
            all_history = self.store.get(exsymbol)
            if len(all_history) == 0:
                continue
            history = get_history_by_date(all_history, date)
            low = history[-self.slow:].low.min()
            close = history.iloc[-1].close
            chg = close / low
            s_chg = history.close.pct_change().values
            s_chg_slow = s_chg[-self.slow:]
            std = np.std(s_chg_slow)
            scores.append({
                "exsymbol": exsymbol,
                "score": chg * std,
                "close": history.iloc[-1].close,
                "date": history.iloc[-1].date})
        if len(scores) > 0:
            scores.sort(key=lambda x: x["score"])
            return scores[0]
        return None

    def filter_stock(self, date):
        result = []
        for exsymbol in self.exsymbols:
            history = []
            try:
                all_history = self.store.get(exsymbol)
                if len(all_history) == 0:
                    continue
                history = get_history_by_date(all_history, date)
            except Exception, e:
                print "history error: %s %s" % (exsymbol, str(e))
                continue
            closes = history.close.values
            if len(closes) < self.slow:
                continue
            low = history[-self.slow:].low.min()
            close = history.iloc[-1].close
            chg = close / low
            if chg < 1.0:
                continue
            ema_slow = talib.EMA(closes, timeperiod=self.slow)
            ema_fast = talib.EMA(closes, timeperiod=self.fast)
            length = len(ema_slow) - 1
            if ema_slow[length-2] > ema_fast[length-2] and \
                ema_slow[length-1] < ema_fast[length-1]:
                result.append(exsymbol)

        return result

    def run(self):
        logger.info("Running strategy with start=%s end=%s initial=%f fast=%d slow=%d target=%f" %(
            self.start, self.end, self.initial, self.fast, self.slow, self.target))
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= self.start) & (dates <= self.end)]
        state = 0
        days = 0
        buy_price = 0.0
        sell_limit = 0.0
        for date in dates:
            if state == 0:
                exsymbols = self.filter_stock(date)
                result = self.rank_stock(date, exsymbols)
                if result == None:
                    continue
                exsymbol = result["exsymbol"]
                date = result["date"]
                close = result["close"]
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                balance = self.order.get_account_balance()
                amount = int(balance / close / 100) * 100
                self.order.buy(exsymbol, close, dt, amount)
                buy_price = close
                sell_limit = buy_price * self.target
                state = 1
                days += 1
                continue

            if state == 1:
                pos = self.order.get_positions()[0]
                all_history = self.store.get(exsymbol)
                if not is_sellable(all_history, date):
                    state = -1
                    continue

                try:
                    row = get_history_on_date(all_history, date)
                    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                    if row.close > sell_limit:
                        self.order.sell(pos.exsymbol, sell_limit, dt, pos.amount)
                        state = 0
                        days = 0
                    else:
                        days += 1
                        if days == 5:
                            self.order.sell(pos.exsymbol, row.close, dt, pos.amount)
                            state = 0
                            days = 0
                    continue
                except NoHistoryOnDate, e:
                    #print pos.exsymbol, date
                    pass

            if state == -1:
                if is_sellable(all_history, date):
                    pos = self.order.get_positions()[0]
                    all_history = self.store.get(exsymbol)
                    row = get_history_on_date(all_history, date)
                    self.order.sell(pos.exsymbol, row.open, dt, pos.amount)
                    state = 0
                    days = 0

        report = Report()
        result = report.get_summary()
        logger.info("profit=%f, max_drawdown=%f, num_of_trades=%d, win_rate=%f, comm_total=%f" % (
            result.profit,
            result.max_drawdown,
            result.num_of_trades,
            result.win_rate,
            result.comm_total))

if __name__ == "__main__":
    logging.config.fileConfig(LOGCONF)
    strategy = EmaStrategy(start='2017-01-01', end='2017-03-09')
    strategy.run()
