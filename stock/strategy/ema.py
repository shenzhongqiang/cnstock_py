import numpy as np
import talib
from stock.utils.symbol_util import get_stock_symbols, get_archived_trading_dates
from stock.marketdata import backtestdata
from stock.strategy.utils import get_exsymbol_history
from stock.strategy.base import Strategy

class EmaStrategy(Strategy):
    def __init(self, initial=80000, fast=5, slow=7):
        super(EmaStrategy, self).__init__(initial)
        self.fast = fast
        self.slow = slow

    def filter_stock(self, exsymbol_history, date):
        result = []
        for exsymbol in exsymbol_history.keys():
            history = []
            try:
                history = get_history_by_date(exsymbol_history[exsymbol], date)
            except Exception, e:
                print str(e)
                continue
            closes = map(lambda x: x.close, history)
            ema_slow = talib.EMA(closes, timeperiod=slow)
            print ema_slow
            import time
            time.sleep(5)
            ema_fast = talib.EMA(closes, timeperiod=fast)
            ema_slow_prev = talib.EMA(closes[:-1], timeperiod=slow)
            ema_fast_prev = talib.EMA(closes[:-1], timeperiod=fast)
            if ema_slow_prev > ema_fast_prev and \
                ema_slow < ema_fast:
                result.append({"exsymbol": exsymbol, "history": history})

        return result

    def run(self):
        symbols = get_stock_symbols()
        marketdata = backtestdata.BackTestData('2017-06-15')
        exsymbol_history = get_exsymbol_history()
        dates = get_archived_trading_dates('2016-06-01', '2017-06-15')
        for date in dates:
            result = self.filter_stock(exsymbol_history, date)
            print result

if __name__ == "__main__":
    strategy = EmaStrategy()
    strategy.run()
