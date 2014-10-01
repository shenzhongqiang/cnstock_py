from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class CrossStar(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bar_today = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bar1 = history[0]
                bar2 = history[1]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bar_today = history[0]
                bar1 = history[1]
                bar2 = history[2]

            vol = bar_today.volume
            if vol == 0:
                return

            if bar_today.high == bar_today.low:
                return

            chgperc = bar1.close / bar2.close - 1
            crossed = abs(bar_today.close - bar_today.open) / bar_today.close < 0.05
            if crossed and chgperc > 0.08:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bar_today.pe, cvalue=bar_today.cvalue, value=bar_today.value))
        except Exception, e:
            print e.message
