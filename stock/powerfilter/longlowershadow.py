from stock.filter.interface import Filter, CheckResult
from stock.filter.utils import *
from stock.globalvar import *
from stock.marketdata import *
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class LongLowerShadow:
    def __init__(self, marketdata):
        self.marketdata = marketdata

    def check(self, exsymbols):
        basket = []
        for exsymbol in exsymbols:
            try:
                bars = [0] * 5
                if isinstance(self.marketdata, realtimedata.RealTimeData):
                    bars[0] = self.marketdata.get_data(exsymbol)
                    history = self.marketdata.get_history_by_date(exsymbol)
                    bars[1:5] = history[0:4]
                elif isinstance(self.marketdata, backtestdata.BackTestData):
                    history = self.marketdata.get_history_by_date(exsymbol)
                    bars[0:5] = history[0:5]

                vol = bars[0].volume
                zt_price = get_zt_price(bars[1].close)
                if vol == 0:
                    continue

                if zt_price == bars[0].close:
                    continue

                chgperc = (bars[0].close / bars[1].close - 1) * 100
                lower_low = (bars[0].low < bars[1].low) and \
                    (bars[1].low < bars[2].low)
                small_body = abs(bars[0].close - bars[0].open) \
                    < (bars[0].high - bars[0].low) * 0.2
                small_range = (bars[0].high - bars[0].low) \
                    < bars[0].close * 0.03
                if lower_low and small_body and not small_range:
                    basket.append({'exsymbol': exsymbol, 'bars': bars})

            except IOError, e:
                logger.error("cannot open: %s" % (e.filename))
            except Exception, e:
                logger.error("%s: %s" % (type(e), e.message))

        if len(basket) > 30:
            basket = filter(lambda x: \
                x['bars'][0].close > x['bars'][0].open, basket)

            if len(basket) > 30:
                basket = filter(lambda x: \
                    abs(x['bars'][0].close - x['bars'][0].open) \
                    < (x['bars'][0].high - x['bars'][0].low) * 0.1, basket)

        output = []
        for stock in basket:
            exsymbol = stock['exsymbol']
            bars = stock['bars']
            chgperc = (bars[0].close / bars[1].close - 1) * 100
            output.append(CheckResult(exsymbol, chgperc=chgperc, \
                pe=bars[0].pe, cvalue=bars[0].cvalue, value=bars[0].value))

        return output

