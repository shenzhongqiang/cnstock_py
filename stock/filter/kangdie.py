from stock.filter.interface import Filter, CheckResult
from stock.filter.utils import *
from stock.globalvar import *
from stock.marketdata import *
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class Kangdie(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bar_today = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bar1 = history[0]
                bar2 = history[1]
                bar3 = history[2]
                bar4 = history[3]
                bar5 = history[4]
                bar6 = history[5]
                bar7 = history[6]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bar_today = history[0]
                bar1 = history[1]
                bar2 = history[2]
                bar3 = history[3]
                bar4 = history[4]
                bar5 = history[5]
                bar6 = history[6]
                bar7 = history[7]

            vol = bar_today.volume
            zt_price = get_zt_price(bar1.close)
            if vol == 0:
                return

            if zt_price == bar_today.close:
                return

            chgperc = (bar_today.close / bar1.close - 1) * 100
            chg0 = bar_today.close / bar1.close - 1
            chg1 = bar1.close / bar2.close - 1
            chg2 = bar2.close / bar3.close - 1
            chg3 = bar3.close / bar4.close - 1
            chg4 = bar4.close / bar5.close - 1
            chg5 = bar5.close / bar6.close - 1
            chg6 = bar6.close / bar7.close - 1
            if chg0 > 0:
                self.output.append(CheckResult(
                    exsymbol, \
                    chgperc=chgperc, \
                    pe=bar_today.pe, \
                    cvalue=bar_today.cvalue, \
                    value=bar_today.value, \
                    bar_today=bar_today))
        except IOError, e:
            logger.error("cannot open: %s" % (e.filename))
        except Exception, e:
            logger.error("%s: %s" % (type(e), e.message))


