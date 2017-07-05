import numpy as np
import talib
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata import backtestdata
from stock.strategy.utils import get_exsymbol_history, get_history_by_date
from stock.strategy.base import Strategy
from stock.marketdata.storefactory import get_store
from config import store_type

class EmaStrategy(Strategy):
    def __init__(self, initial=80000, fast=5, slow=7):
        super(EmaStrategy, self).__init__(initial)
        self.store = get_store(store_type)
        self.fast = fast
        self.slow = slow
        self.exsymbols = self.store.get_stock_exsymbols()

    def rank_stock(self, date, exsymbols):
        scores = []
        for exsymbol in exsymbols:
            all_history = self.store.get(exsymbol)
            if len(all_history) == 0:
                continue
            history = get_history_by_date(all_history, date)
            s_chg = history.close.pct_change().values
            s_chg_slow = s_chg[-self.slow:]
            chg = reduce(lambda x, y: x * y,
                map(lambda x: 1 + x, s_chg_slow))
            std = np.std(s_chg_slow)
            scores.append({"exsymbol": exsymbol, "score": chg * std})
        if len(scores) > 0:
            scores.sort(key=lambda x: x["score"])
            return scores[0]["exsymbol"]
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
            ema_slow = talib.EMA(closes, timeperiod=self.slow)
            ema_fast = talib.EMA(closes, timeperiod=self.fast)
            length = len(ema_slow) - 1
            if ema_slow[length-2] > ema_fast[length-2] and \
                ema_slow[length-1] < ema_fast[length-1]:
                result.append(exsymbol)

        return result

    def run(self):
        marketdata = backtestdata.BackTestData('2017-06-15')
        dates = self.store.get_trading_dates()
        dates = dates[(dates >= '2016-06-01') & (dates <= '2017-06-01')]
        for date in dates:
            result = self.filter_stock(date)
            print self.rank_stock(date, result)
            print "=============================="

if __name__ == "__main__":
    strategy = EmaStrategy()
    strategy.run()
