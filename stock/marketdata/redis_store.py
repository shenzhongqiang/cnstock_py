import re
import os
from cStringIO import StringIO
import redis
import pandas as pd
from stock.globalvar import HIST_DIR

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

class Store(object):
    @staticmethod
    def save(exsymbol, df):
        r = redis.Redis(connection_pool=POOL)
        df_string = df.to_csv()
        r.set(exsymbol, df_string)

    @staticmethod
    def get(exsymbol):
        r = redis.Redis(connection_pool=POOL)
        df_string = r.get(exsymbol)
        io = StringIO(df_string)
        df = pd.read_csv(io)
        index = pd.to_datetime(df.date, format="%Y-%m-%d")
        df.set_index(index, inplace=True)
        return df

    @staticmethod
    def flush():
        r = redis.Redis(connection_pool=POOL)
        r.flushall()

    @staticmethod
    def get_exsymbols():
        r = redis.Redis(connection_pool=POOL)
        return r.keys()

    @staticmethod
    def get_stock_exsymbols():
        r = redis.Redis(connection_pool=POOL)
        exsymbols = r.keys()
        result = filter(lambda x: re.search(r'^(?!id)', x), exsymbols)
        return result

    @staticmethod
    def get_trading_dates():
        r = redis.Redis(connection_pool=POOL)
        history = Store.get('id000001')
        return history.date.values
