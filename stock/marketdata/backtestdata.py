import datetime
import re
import os.path
from stock.utils.request import *
from stock.utils.uniform import *
from stock.globalvar import *
from stock.marketdata.bar import *
from stock.marketdata.interface import *

class TooFewHistoryBars(Exception):
    pass

class NoHistoryBar(Exception):
    pass

class BackTestData(MarketData):
    def __init__(self, date):
        self.date = date
        self.dt = datetime.datetime.strptime(date, "%y%m%d")

    def get_data(self, exsymbol):
        history_by_today = self.get_history_by_date(exsymbol)

        if len(history_by_today) < 2:
            raise TooFewHistoryBars("%s has fewer than 2 history bars" \
                % (exsymbol))

        bar_today = history_by_today[0]
        if bar_today.dt < self.dt:
            raise NoHistoryBar("no history bar for %s on %s" \
                % (exsymbol, self.date))

        return bar_today
