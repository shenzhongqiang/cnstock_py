from stock.filter.interface import Filter, CheckResult
from stock.filter.utils import *
from stock.globalvar import *
from stock.marketdata import *
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class LianZhang(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            bars = [0] * 6
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bars[0] = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[1:6] = history[0:5]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(exsymbol)
                bars[0:6] = history[0:6]

            wuliang = True
            for i in range(5):
                zt_price = get_zt_price(bars[i+1].close)
                today_close = bars[i].close
                if zt_price != today_close:
                    wuliang = False

            chgperc = (bars[0].close / bars[1].close - 1) * 100
            if wuliang:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))
        except IOError, e:
            logger.error("cannot open: %s" % (e.filename))
        except Exception, e:
            logger.error("%s: %s" % (type(e), e.message))
