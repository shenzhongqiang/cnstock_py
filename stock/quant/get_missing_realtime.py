import os
import sys
import datetime
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import numpy as np
import pandas as pd

date = None
if len(sys.argv) == 1:
    date = datetime.date.today().strftime("%Y-%m-%d")
else:
    date = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_index = store.get('sz000001')
if not date in df_index.index:
    print("not a valid trading date")
    sys.exit(1)
date_idx = df_index.index.get_loc(date)
yest_date = df_index.index[date_idx-1].strftime("%Y-%m-%d")

df_res = pd.DataFrame(columns=["body", "tmr_chg", "yest_one", "opengap", "today_chg", "yest_chg", "upper", "lower", "vol_ratio", "highperc", "increase10", "increase60", "closeup"])
data = {}
i = 0
for exsymbol in exsymbols:
    df = store.get(exsymbol)
    data[exsymbol] = df

for i in range(date_idx, len(df_index), 1):
    df_res= pd.DataFrame(columns=["close","open","high","low","volume","chgperc","yest_close","amount","b1_v","b1_p","a1_v","a1_p","pe","pb","lt_mcap","mcap"])
    date = df_index.index[i]
    filename = date.strftime("%Y-%m-%d") + ".csv"
    filepath = os.path.join(os.path.dirname(__file__), "..", "..", "data/realtime/daily", filename)
    if os.path.isfile(filepath):
        print(filepath)
        continue
    for exsymbol, df in data.items():
        df["chgperc"] = (df.close/df.close.shift(1)-1) * 100
        df["yest_close"] = df.close.shift(1)
        if date not in df.index:
            continue
        s = df.loc[date]
        df_res.loc[exsymbol] = [s.close,s.open,s.high,s.low,s.volume,s.chgperc,s.yest_close,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
    df_res.to_csv(filepath)
