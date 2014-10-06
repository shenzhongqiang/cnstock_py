from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class LongUpperShadow(Filter):
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
            zt_price = round(bar1.close * 1.1 * 100) / 100
            if vol == 0:
                return

            if zt_price == bar_today.close:
                return

            chgperc = (bar_today.close / bar1.close - 1) * 100
            chg_yest = bar1.close / bar2.close - 1
            is_high = bar_today.high > bar_today.open * 1.04
            small_body = abs(bar_today.close - bar_today.open) < \
                bar_today.open * 0.02
            if chg_yest > 0.06 and is_high and small_body:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bar_today.pe, cvalue=bar_today.cvalue, value=bar_today.value))
        except Exception, e:
            print e.message

