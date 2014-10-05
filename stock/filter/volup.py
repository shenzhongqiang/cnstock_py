from stock.filter.interface import Filter, CheckResult
from stock.marketdata import *

class VolUp(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            bars = [0] * 8
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bars[0] = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[1:8] = history[0:7]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[0:8] = history[0:8]

            vol = bars[0].volume
            if vol == 0:
                return

            if bars[0].high == bars[0].low:
                return

            vols = [ x.volume for x in bars[3:8] ]
            max_vol = max(vols)
            volup = bars[0].volume > max_vol * 2 and \
                bars[1].volume > max_vol * 2 and \
                bars[2].volume > max_vol * 2
            up_bar = bars[0].close > bars[0].open

            chgperc = (bars[0].close / bars[1].close - 1) * 100
            if volup and up_bar:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))
        except Exception, e:
            print e.message

