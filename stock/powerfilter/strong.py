from stock.filter.interface import Filter, CheckResult
from stock.filter.utils import *
from stock.globalvar import *
from stock.marketdata import *
from stock.utils.symbol_util import *
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class Strong:
    def __init__(self, marketdata):
        self.marketdata = marketdata

    def get_stock_data(self, exsymbol):
        bars = [0] * 10
        if isinstance(self.marketdata, realtimedata.RealTimeData):
            bars[0] = self.marketdata.get_data(exsymbol)
            history = self.marketdata.get_history_by_date(exsymbol)
            bars[1:10] = history[0:9]
        elif isinstance(self.marketdata, backtestdata.BackTestData):
            history = self.marketdata.get_history_by_date(exsymbol)
            bars[0:10] = history[0:10]
        return bars

    def check(self, exsymbols):
        output = []
        chg = {}
        chg['sh'] = self.get_stock_data('sh000001')[0].close / self.get_stock_data('sh000001')[1].close - 1
        chg['sz'] = self.get_stock_data('sz399001')[0].close / self.get_stock_data('sz399001')[1].close - 1
        chg['cy'] = self.get_stock_data('sz399006')[0].close / self.get_stock_data('sz399006')[1].close - 1

        for exsymbol in exsymbols:
            try:
                bars = self.get_stock_data(exsymbol)
                vol = bars[0].volume
                if vol == 0 or bars[0].low == bars[0].high:
                    continue

                zt = False
                for i in range(9):
                    if bars[i].close / bars[i+1].close > 1.09:
                        zt = True

                if zt == False:
                    continue

                bar_change = bars[0].close / bars[1].close - 1
                if is_symbol_cy(exsymbol):
                    if chg['cy'] <= -0.01 and bar_change >= 0.01:
                        output.append(CheckResult(exsymbol, chgperc=bar_change*100,
                            pe=bars[0].pe, cvalue=bars[0].cvalue,
                            value=bars[0].value))
                elif is_symbol_sh(exsymbol):
                    if chg['sh'] <= -0.01 and bar_change >= 0.01:
                        output.append(CheckResult(exsymbol, chgperc=bar_change*100,
                            pe=bars[0].pe, cvalue=bars[0].cvalue,
                            value=bars[0].value))
                elif is_symbol_sz(exsymbol):
                    if chg['sz'] <= -0.01 and bar_change >= 0.01:
                        output.append(CheckResult(exsymbol, chgperc=bar_change*100,
                            pe=bars[0].pe, cvalue=bars[0].cvalue,
                            value=bars[0].value))
            except IOError, e:
                logger.error("cannot open: %s" % (e.filename))
            except Exception, e:
                logger.error("%s: %s" % (type(e), e.message))

        output.sort(key=lambda x: x.chgperc)
        return output
