from stock.utils.fuquan import *
from stock.filter.interface import Filter, CheckResult
from stock.globalvar import *
from stock.marketdata import *
import logging
import logging.config
import numpy as np
import pandas as pd
import scipy.stats

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class VolUp(Filter):
    def check(self, exsymbol):
        #print exsymbol
        try:
            bars = [0] * 8
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bars[0] = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_archived_history_in_file(exsymbol)
                bars[1:8] = history[0:7]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_archived_history_in_file(exsymbol)
                bars[0:8] = history[0:8]

            vol = bars[0].volume
            if vol == 0:
                return

            if bars[0].high == bars[0].low:
                return

            fuquan_history(history)
            history.reverse()
            dates = map(lambda x: x.date, history)
            highs = map(lambda x: x.high, history)
            lows = map(lambda x: x.low, history)
            opens = map(lambda x: x.open, history)
            closes = map(lambda x: x.close, history)
            volumes = map(lambda x: x.volume, history)
            df = pd.DataFrame({"high": highs,
                "low": lows,
                "open": opens,
                "close": closes,
                "volume": volumes}, index=dates)

            is_big = bars[0].volume > df.volume[len(df.volume)-250:].quantile(0.95)
            chgperc = (bars[0].close / bars[1].close - 1) * 100
            if is_big:
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))
        except IOError, e:
            logger.error("cannot open: %s" % (e.filename))
        except Exception, e:
            logger.error("%s: %s" % (type(e), e.message))
