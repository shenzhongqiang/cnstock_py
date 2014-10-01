from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class LongLowerShadow(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bar_today = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bar_yest = history[0]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bar_today = history[0]
                bar_yest = history[1]

            vol = bar_today.volume
            if vol == 0:
                return

            if bar_today.high == bar_today.low:
                return

            chgperc = (bar_today.close / bar_yest.close - 1) * 100
            is_deep = bar_today.low < bar_today.close * 0.95
            small_body = abs(bar_today.close - bar_today.open) < \
                bar_today.open * 0.02

            if is_deep and small_body and chgperc > -2:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bar_today.pe, cvalue=bar_today.cvalue, value=bar_today.value))
        except Exception, e:
            print e.message


