from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class ZhangTing(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            bars = [0] * 3
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bars[0] = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[1:3] = history[0:2]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[0:3] = history[0:3]

            vol = bars[0].volume
            zt_price = round(bars[1].close * 1.1 * 100) / 100
            if vol == 0:
                return

            if zt_price == bars[0].close:
                return

            chgperc = (bars[0].close / bars[1].close - 1) * 100
            yest_zt_price = round(bars[2].close * 1.1 * 100) / 100
            if yest_zt_price == bars[1].close:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))
        except Exception, e:
            print e.message
