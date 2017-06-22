import os
import cPickle as pickle
import redis
from stock.globalvar import HIST_DIR

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

def save(exsymbol, df):
    r = redis.Redis(connection_pool=POOL)
    df_string = pickle.dumps(df)
    r.set(exsymbol, df_string)

def get(exsymbol):
    r = redis.Redis(connection_pool=POOL)
    df_string = r.get(exsymbol)
    return pickle.loads(df_string)

def init():
    r = redis.Redis(connection_pool=POOL)
    r.flushall()

def get_exsymbols():
    r = redis.Redis(connection_pool=POOL)
    return r.keys()

def get_trading_dates():
    r = redis.Redis(connection_pool=POOL)
    history = get('id000001')
    return history.date.values

def save_into_file(exsymbol, df):
    stock_dir = HIST_DIR['stock']
    path = os.path.join(stock_dir, exsymbol)
    with open(path, "wb") as f:
        pickle.dump(df, f)

def get_from_file(exsymbol):
    stock_dir = HIST_DIR['stock']
    path = os.path.join(stock_dir, exsymbol)
    with open(path, "rb") as f:
        df = pickle.load(f)
        return df
