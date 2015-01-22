from stock.filter.interface import Filter, CheckResult
from stock.filter.utils import *
from stock.globalvar import *
from stock.marketdata import *
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class LongUpperShadow(Filter):
    def __init__(self, queue, marketdata, output, \
        params={"high": 1.04, "body": 0.02, "chg": 0.06}):
        super(LongUpperShadow, self).__init__(queue, marketdata, output, params)

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
            zt_price = get_zt_price(bar1.close)
            if vol == 0:
                return

            if len(history) < 100:
                return

            if zt_price == bar_today.close:
                return

            chgperc = (bar_today.close / bar1.close - 1) * 100
            chg_yest = bar1.close / bar2.close - 1
            params = self.params
            is_high = bar_today.high > bar_today.open * params["high"]
            small_body = abs(bar_today.close - bar_today.open) < \
                bar_today.open * params["body"]
            if chg_yest > params["chg"] and is_high and small_body:
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
