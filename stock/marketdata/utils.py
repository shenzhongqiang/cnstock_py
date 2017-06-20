import os.path
import pandas as pd
from stock.globalvar import HIST_DIR

def load_csv(symbol):
    path = os.path.join(HIST_DIR["stock"], symbol)
    df = pd.read_csv(path, index_col=0, engine='c', dtype=str)
    return df
