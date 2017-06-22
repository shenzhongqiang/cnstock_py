import re
import os.path
from stock.utils.request import *
from stock.utils.fuquan import *
from stock.utils.dt import *
from stock.globalvar import *
from stock.marketdata.interface import MarketData

class TooFewHistoryBars(Exception):
    pass

class NoHistoryBar(Exception):
    pass

class BackTestData(MarketData):
    def __init__(self, date):
        MarketData.__init__(self)
        self.date = date

    def get_data(self, exsymbol):
        history_by_today = self.get_history_by_date(exsymbol)

        if len(history_by_today.index) == 0:
            raise NoHistoryBar("no history bar for %s on %s" \
                % (exsymbol, self.date))

        return history_by_today[len(history_by_today)-1]
