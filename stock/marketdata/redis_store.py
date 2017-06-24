import os
import cPickle as pickle
import redis
from stock.globalvar import HIST_DIR

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

class Store(object):
    @staticmethod
    def save(exsymbol, df):
        r = redis.Redis(connection_pool=POOL)
        df_string = pickle.dumps(df)
        r.set(exsymbol, df_string)

    @staticmethod
    def get(exsymbol):
        r = redis.Redis(connection_pool=POOL)
        df_string = r.get(exsymbol)
        return pickle.loads(df_string)

    @staticmethod
    def flush():
        r = redis.Redis(connection_pool=POOL)
        r.flushall()

    @staticmethod
    def get_exsymbols():
        r = redis.Redis(connection_pool=POOL)
        return r.keys()

    @staticmethod
    def get_trading_dates():
        r = redis.Redis(connection_pool=POOL)
        history = Store.get('id000001')
        return history.date.values
