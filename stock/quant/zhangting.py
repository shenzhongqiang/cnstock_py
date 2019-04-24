import re
import sys
import datetime
import numpy as np
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, get_tick_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts
import pandas as pd
from pandas.tseries.offsets import BDay

def get_zhangting_industry(today):
    date = today.strftime("%Y-%m-%d")
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

def get_potential(date):
    date_0 = date.strftime("%Y-%m-%d")
    date_1 = (date - BDay(1)).strftime("%Y-%m-%d")
    date_2 = (date - BDay(2)).strftime("%Y-%m-%d")
    date_3 = (date - BDay(3)).strftime("%Y-%m-%d")
    df_0 = get_tick_by_date(date_0)
    df_1 = get_tick_by_date(date_1)
    df_2 = get_tick_by_date(date_2)
    df_3 = get_tick_by_date(date_3)
    df_0.loc[:, "kaipan_0"] = df_0["kaipan_money"]
    df_1.loc[:, "kaipan_1"] = df_1["kaipan_money"]
    df_2.loc[:, "kaipan_2"] = df_2["kaipan_money"]
    df_3.loc[:, "kaipan_3"] = df_3["kaipan_money"]
    df_rt_0 = get_realtime_by_date(date_0)
    df_rt_1 = get_realtime_by_date(date_1)
    df_rt_2 = get_realtime_by_date(date_2)
    df_rt_3 = get_realtime_by_date(date_3)
    df_rt_0 = df_rt_0[(df_rt_0.lt_mcap<100) & (df_rt_0.chgperc<9)]
    df_rt_1 = df_rt_1[(df_rt_1.chgperc<9)]
    df_rt_2 = df_rt_2[(df_rt_2.chgperc<9)]
    df_rt_3 = df_rt_3[(df_rt_3.chgperc<9)]
    df_rt_0.loc[:, "opengap_0"] = df_rt_0.open / df_rt_0.yest_close - 1
    df_rt_1.loc[:, "opengap_1"] = df_rt_1.open / df_rt_1.yest_close - 1
    df_rt_2.loc[:, "opengap_2"] = df_rt_2.open / df_rt_2.yest_close - 1
    df_rt_3.loc[:, "opengap_3"] = df_rt_3.open / df_rt_3.yest_close - 1
    df_rt = df_rt_0.merge(df_rt_1, how="inner", left_index=True, right_index=True)
    df_rt = df_rt.merge(df_rt_2, how="inner", left_index=True, right_index=True)
    df_rt = df_rt.merge(df_rt_3, how="inner", left_index=True, right_index=True)
    df_rt = df_rt[(df_rt.opengap_0<0.02) & \
        (df_rt.opengap_1<0.02) & \
        (df_rt.opengap_2<0.02) & \
        (df_rt.opengap_3<0.02) & \
        (df_rt.opengap_0>-0.02) & \
        (df_rt.opengap_1>-0.02) & \
        (df_rt.opengap_2>-0.02) & \
        (df_rt.opengap_3>-0.02)]
    df_res = df_rt.merge(df_0, how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_1, how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_2, how="inner", left_index=True, right_index=True)
    df_res = df_res.merge(df_3, how="inner", left_index=True, right_index=True)
    df_res.loc[:, "calc"] = df_res["kaipan_0"] - (df_res["kaipan_1"]+df_res["kaipan_2"]+df_res["kaipan_3"])
    df_res = df_res[df_res.calc > 0]
    columns = ["kaipan_0", "kaipan_1", "kaipan_2", "kaipan_3", "calc"]
    df_plt = df_res[columns].sort_values("calc", ascending=True).tail(50)
    print(df_plt)

date = None
if len(sys.argv) == 1:
    today = pd.datetime.today()
else:
    today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
get_zhangting_industry(today)
#get_potential(today)
