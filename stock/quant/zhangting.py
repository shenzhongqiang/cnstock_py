import re
import sys
import datetime
import numpy as np
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts
import pandas as pd

date = None
if len(sys.argv) == 1:
    date = datetime.date.today().strftime("%Y-%m-%d")
else:
    date = sys.argv[1]

store = get_store(store_type)
exsymbols = store.get_stock_exsymbols()
df_rt = get_realtime_by_date(date)
df_rt = df_rt[df_rt.chgperc>9.9]
df_basics = ts.get_stock_basics()
df_basics.loc[:, "code"] = df_basics.index
df_basics.loc[:, "exsymbol"] = df_basics.code.apply(lambda x: 'sh'+x if re.match(r'6', x) else 'sz'+x)
df_basics.set_index("exsymbol", inplace=True)
df_res = df_rt.merge(df_basics[["industry"]], how="inner", left_index=True, right_index=True)
print(df_res.industry.value_counts())
