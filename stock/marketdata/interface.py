import os.path
import datetime
from stock.marketdata.bar import Bar
from stock.globalvar import *
from stock.utils.dt import *
from stock.utils.symbol_util import *
from abc import *
import tushare as ts

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
        symbol = exsymbol_to_symbol(exsymbol)
        df = ts.get_k_data(symbol)
        print df
        history = []
        start = 0
        for index, row in df.iloc[::-1].iterrows():
            dt = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
            if start == 0 and dt <= self.dt:
                start = 1

            if start == 1:
                bar = Bar(row.code, date=row.date, dt=dt, open=row.open,
                    close=row.close, high=row.high, low=row.low,
                    volume=row.volume)
                history.append(bar)

        if start == 0:
            raise NoHistoryBeforeDate("no history data for %s before %s" \
                % (exsymbol, self.date))

        if len(history) < 10:
            raise TooFewBarsBeforeDate("too few bars for %s before %s" \
                % (exsymbol, self.date))
        return history

