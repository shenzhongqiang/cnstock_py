import datetime
import re
import os.path
from stock.utils.request import *
from stock.utils.uniform import *
from stock.globalvar import *
from stock.marketdata.bar import *

class NoHistoryBeforeDate(Exception):
    pass

class TooFewHistoryBars(Exception):
    pass

class NoHistoryBar(Exception):
    pass

class BackTestData:
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

    def get_history_by_date(self, exsymbol):
        bars = self.get_history_in_file(exsymbol)
        history = []
        start = 0
        for bar in bars:
            if start == 0 and bar.dt <= self.dt:
                start = 1

            if start == 1:
                history.append(bar)

        if start == 0:
            raise NoHistoryBeforeDate("no history data for %s before %s" \
                % (exsymbol, self.date))

        return history

    # get all history bars in file
    def get_history_in_file(self, exsymbol):
        today_date = self.date
        file = ''
        if exsymbol in INDEX.values():
            file = os.path.join(HIST_DIR['index'], exsymbol)
        else:
            file = os.path.join(HIST_DIR['stock'], exsymbol)
        f = open(file, "r")
        contents = f.read()
        f.close()
        lines = contents.split('\\n\\\n')

        history = []
        start = 0
        i = len(lines) - 2
        while i >= 2:
            line = lines[i]
            (date, o, close, high, low, volume) = line.split(' ')
            dt = datetime.datetime.strptime(date, "%y%m%d")
            if dt <= self.dt:
                start = 1
            if start == 1:
                bar = Bar(exsymbol, date=date, dt=dt, open=o, \
                    close=close, high=high, low=low, volume=volume)
                history.append(bar)
            i = i - 1

        if start == 0:
            raise NoHistoryBeforeDate("no history data for %s before %s" \
                % (exsymbol, self.date))

        return history
