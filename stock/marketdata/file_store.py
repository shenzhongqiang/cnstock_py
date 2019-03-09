import re
import os
import pandas as pd
from stock.globalvar import HIST_DIR

class Store(object):
    @staticmethod
    def save(exsymbol, df):
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, exsymbol)
        with open(path, "w") as f:
            f.write(df.to_csv())

    @staticmethod
    def get(exsymbol):
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, exsymbol)
        df = None
        with open(path, "r") as f:
            df = pd.read_csv(f)
            index = pd.to_datetime(df.date, format="%Y-%m-%d")
            df.set_index(index, inplace=True)
        return df

    @staticmethod
    def flush():
        files = os.listdir(HIST_DIR["stock"])
        filepaths = list(map(lambda x: os.path.join(HIST_DIR["stock"], x), files))
        for path in filepaths:
            os.remove(path)

    @staticmethod
    def get_exsymbols():
        files = os.listdir(HIST_DIR["stock"])
        return files

    @staticmethod
    def get_stock_exsymbols():
        exsymbols = os.listdir(HIST_DIR["stock"])
        result = list(filter(lambda x: re.search(r'^(?!id)', x), exsymbols))
        return result

    @staticmethod
    def get_trading_dates():
        history = Store.get('id000001')
        return history.index.values

