from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from stock.trade.order import Order
from stock.globalvar import DBFILE
from stock.trade.models import Base
from stock.strategy.base import Strategy, NotImplemented
from stock.marketdata.storefactory import get_store
from config import store_type

class StockSimpleStrategy(Strategy):
    def __init__(self, start, end, initial=10000):
        super(StockSimpleStrategy, self).__init__(start=start, end=end, initial=initial)
        store = get_store(store_type)
        self.exsymbols = store.get_stock_exsymbols()
        dates = store.get_trading_dates()
        self.trading_dates = dates[(dates >= self.start) & (dates <= self.end)]
        self.history = {}
        for exsymbol in self.exsymbols:
            df = store.get(exsymbol)[:end]
            self.history[exsymbol] = df

    def get_exsymbol_history(self, exsymbol):
        return self.history[exsymbol]

    def set_exsymbol_history(self, exsymbol, df):
        self.history[exsymbol] = df
