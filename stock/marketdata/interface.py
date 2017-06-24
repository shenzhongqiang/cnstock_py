import redis
import os.path
import datetime
from stock.marketdata.bar import Bar
from stock.utils.symbol_util import exsymbol_to_symbol
from abc import ABCMeta, abstractmethod
from stock.marketdata.utils import load_csv
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd
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
        store = get_store(store_type)
        df = store.get(exsymbol)
        return df[df.date <= self.date]
