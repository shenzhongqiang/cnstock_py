import os
import cPickle as pickle
from stock.globalvar import HIST_DIR

class Store(object):
    @staticmethod
    def save(exsymbol, df):
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, exsymbol)
        with open(path, "wb") as f:
            pickle.dump(df, f)

    @staticmethod
    def get(exsymbol):
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, exsymbol)
        with open(path, "rb") as f:
            df = pickle.load(f)
            return df

    @staticmethod
    def flush():
        files = os.listdir(HIST_DIR)
        filepaths = map(lambda x: os.path.join(HIST_DIR, x), files)
        for path in filepaths:
            os.remove(path)

    @staticmethod
    def get_exsymbols():
        files = os.listdir(HIST_DIR)
        return files

    @staticmethod
    def get_trading_dates():
        history = Store.get('id000001')
        return history.date.values

