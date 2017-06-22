import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from stock.trade.order import Order
from stock.globalvar import DBFILE
from stock.trade.models import Base

class NotImplemented(Exception):
    pass

class Strategy(object):
    def __init__(self, initial=10000, **kwargs):
        self.result = None
        engine = create_engine('sqlite:///' + DBFILE, echo=False, \
            connect_args={'check_same_thread':False})
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        order = Order(engine)
        order.add_account(initial)

    def run(self):
        raise NotImplemented("subclass must implement this method")

    def get_result(self):
        return self.result
