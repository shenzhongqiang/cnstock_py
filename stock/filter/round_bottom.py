from stock.filter.interface import Filter, CheckResult
from stock.globalvar import *
from stock.marketdata import *
from stock.utils.fuquan import *
import logging
import logging.config
import traceback
import numpy as np
from sklearn.linear_model import LinearRegression

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

def get_first_order_diff(timeseries):
    result = []
    i = 0
    while i < len(timeseries):
        if i == 0:
            result.append({"time": timeseries[i]["time"], "value": 0})
        else:
            diff = timeseries[i]["value"] - timeseries[i-1]["value"]
            result.append({"time": timeseries[i]["time"], "value": diff})
        i+=1
    return result

def norm_series(timeseries):
    values = map(lambda x: x["value"], timeseries)
    lowest = values[0]
    for i in range(len(timeseries)):
        timeseries[i]["value"] = timeseries[i]["value"] / lowest

class RoundBottom(Filter):
    def check(self, exsymbol):
        #print exsymbol
        n = 20
        bars = []
        try:
            if isinstance(self.marketdata, realtimedata.RealTimeData):
                bar_today = self.marketdata.get_data(exsymbol)
                history = self.marketdata.get_archived_history_in_file(exsymbol)
                Fuquan.fuquan_history(history)
                bars.append(bar_today)
                for i in range(20):
                    bars.append(history[i])
            elif isinstance(self.marketdata, backtestdata.BackTestData):
                history = self.marketdata.get_archived_history_in_file(exsymbol)
                Fuquan.fuquan_history(history)
                for i in range(21):
                    bars.append(history[i])

            vol = bars[0].volume
            if vol == 0:
                return

            if bars[0].high == bars[0].low:
                return

            bars.reverse()
            lm = LinearRegression()
            seq = range(n)
            X = np.array([seq]).T
            lowseries = map(lambda x: {"time": x.date, "value": x.low}, bars)
            norm_series(lowseries)
            first_order_diff = get_first_order_diff(lowseries)
            data = map(lambda x: x["value"], first_order_diff[1:21])
            Y = np.array(data) * 1e3
            avg = np.mean(Y)
            lm.fit(X,Y)
            mse = np.mean((Y - lm.predict(X)) ** 2)

            chgperc = (bars[0].close / bars[1].close - 1) * 100
            if lm.coef_[0] > 0.5 and mse < 150:
                print exsymbol, lm.coef_[0], mse
                self.output.append(CheckResult(exsymbol, chgperc=chgperc, \
                    pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))
        except IOError, e:
            traceback.print_exc()
            logger.error("cannot open: %s" % (e.filename))
        except Exception, e:
            traceback.print_exc()
            logger.error("%s: %s" % (type(e), e.message))

