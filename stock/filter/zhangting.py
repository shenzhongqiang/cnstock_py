from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class ZhangTing(Filter):
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
                self.output.append(CheckResult(exsymbol, False))

            zt_price = round(bar_yest.close * 1.1 * 100) / 100
            result = zt_price == bar_today.close
            self.output.append(CheckResult(exsymbol, result))
        except Exception, e:
            print e.message
            self.output.append(CheckResult(exsymbol, False))
