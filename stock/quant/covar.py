from stock.marketdata import *
import logging
import logging.config
from stock.globalvar import *
import numpy as np

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class CoVar:
    def __init__(self, marketdata):
        self.marketdata = marketdata

    def check(self, exsymbols):
        basket = []
        i = 0
        num = 50
        for i in xrange(len(exsymbols)):
            ex1 = exsymbols[i]
            bars1 = [0] * num
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bars1[0] = self.marketdata.get_data(ex1)
                history = self.marketdata.get_history_by_date(ex1)
                if len(history) < 100:
                    continue
                bars1[1:num] = history[0:num-1]
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_history_by_date(ex1)
                if len(history) < 100:
                    continue
                bars1[0:num] = history[0:num]

            for j in range(i+1, len(exsymbols)):
                ex2 = exsymbols[j]
                bars2 = [0] * num
                try:
                    if isinstance(self.marketdata, realtimedata.RealTimeData):
                        bar_today = self.marketdata.get_data(ex2)
                        history = self.marketdata.get_history_by_date(ex2)
                        if len(history) < 100:
                            continue
                        bars2[0:num] = history[0:num]
                    elif isinstance(self.marketdata, backtestdata.BackTestData):
                        history = self.marketdata.get_history_by_date(ex2)
                        bar_today = history[0]
                        if len(history) < 100:
                            continue
                        bars2[0:num] = history[1:num+1]

                    chg = bar_today.close / bars2[0].close
                    bars1_close = map(lambda x: x.close, bars1)
                    bars2_close = map(lambda x: x.close, bars2)
                    ts1 = np.array(bars1_close)
                    ts2 = np.array(bars2_close)
                    cc = np.corrcoef([ts1, ts2])
                    if cc[0, 1] > 0.8 and chg > 1.05:
                        print "%s <=> %s: %f" % (ex1, ex2, cc[0, 1])
                except IOError, e:
                    logger.error("cannot open: %s" % (e.filename))
                except Exception, e:
                    logger.error("%s: %s" % (type(e), e.message))
