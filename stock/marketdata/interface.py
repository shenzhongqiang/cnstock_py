import os.path
from stock.marketdata.bar import Bar
from stock.globalvar import *
from stock.utils.dt import *
from abc import *

class NoHistoryBeforeDate(Exception):
    pass

class TooFewBarsBeforeDate(Exception):
    pass

class MarketData:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, exsymbol):
        pass

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

        if len(history) < 10:
            raise TooFewBarsBeforeDate("too few bars for %s before %s" \
                % (exsymbol, self.date))
        return history

    # get all history bars in file
    def get_history_in_file(self, exsymbol):
        today_date = self.date

        file = os.path.join(HIST_DIR['stock'], "latest", exsymbol)
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
            dt = parse_datetime(date)
            if dt <= self.dt:
                start = 1
            if start == 1:
                bar = Bar(exsymbol, date=date, dt=dt, open=float(o), \
                    close=float(close), high=float(high), low=float(low), \
                    volume=float(volume))
                history.append(bar)
            i = i - 1

        if start == 0:
            raise NoHistoryBeforeDate("no history data for %s before %s" \
                % (exsymbol, self.date))

        return history

    def get_archived_history_in_file(self, exsymbol):
        today_date = self.date

        history = []
        start = 0
        for year in ARCHIVED_YEARS:
            filepath = os.path.join(HIST_DIR['stock'], year, exsymbol)
            if not os.path.isfile(filepath):
                continue

            f = open(filepath, "r")
            contents = f.read()
            f.close()

            lines = contents.split('\\n\\\n')
            i = len(lines) - 2
            while i >= 1:
                line = lines[i]
                (date, o, close, high, low, volume) = line.split(' ')
                dt = parse_datetime(date)
                if dt <= self.dt:
                    start = 1
                if start == 1:
                    bar = Bar(exsymbol, date=date, dt=dt, open=float(o), \
                        close=float(close), high=float(high), low=float(low), \
                        volume=float(volume))
                    history.append(bar)
                i = i - 1

        if start == 0:
            raise NoHistoryBeforeDate("no history data for %s before %s" \
                % (exsymbol, self.date))

        return history
