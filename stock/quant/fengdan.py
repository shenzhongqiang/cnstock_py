import datetime
import sys
import pandas as pd
from stock.utils.symbol_util import get_stock_symbols, get_realtime_by_date, NoRealtimeData, get_tick_by_date
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts
import numpy as np

def get_in_out(symbol, date):
    df = ts.get_tick_data(symbol, date=date, src='tt')
    thre = df.amount.quantile(0.99)
    thre = np.max([thre, 1e6])
    in_amount = df[(df.amount>thre)&(df.type=="买盘")].amount.sum()/1e8
    out_amount = df[(df.amount>thre)&(df.type=="卖盘")].amount.sum()/1e8
    return [in_amount, out_amount]

def get_zhangting_sell(symbol, date):
    df = ts.get_tick_data(symbol, date=date, src='tt')
    high = df.price.max()
    df_zt = df[(df.price==high) & (df.type=="卖盘")]
    thre = df_zt.amount.quantile(0.99)
    thre = np.max([thre, 1e6])
    inst_amount = df_zt[df_zt.amount >= thre].amount.sum() / 1e8
    total_amount = df_zt.amount.sum() / 1e8
    return [inst_amount, total_amount]

if len(sys.argv) < 2:
    print("Usage: %s <sz002750>" % sys.argv[0])
    sys.exit(1)

exsymbol = sys.argv[1]
store = get_store(store_type)
df = store.get(exsymbol)
df["chg"] = df.close / df.close.shift(1) - 1
print("date\tchg\tfengdan\tfengdan_money\tzhangting_min\tzhangting_force\tzhangting_sell\tkaipan_money\tin\tout\tinst_sell\ttotal_sell")
for date in df.index[-15:]:
    date_str = date.strftime("%Y-%m-%d")
    fengdan = 0
    fengdan_money = 0
    try:
        df_rt = get_realtime_by_date(date_str)
        row_rt = df_rt.loc[exsymbol]
        fengdan = row_rt["b1_v"] * row_rt["b1_p"]*100/row_rt["lt_mcap"]/1e8
        fengdan_money = row_rt["b1_v"] * row_rt["b1_p"]*100/1e8
    except Exception:
        pass

    chg = df.loc[date_str].chg
    df_tick = get_tick_by_date(date_str)
    row_tick = df_tick.loc[exsymbol]
    zhangting_min = row_tick["zhangting_min"]
    zhangting_force = row_tick["zhangting_force"]
    zhangting_sell = row_tick["zhangting_sell"]
    kaipan_money = row_tick["kaipan_money"]
    symbol = exsymbol[2:]
    [in_amt, out_amt] = get_in_out(symbol, date_str)
    [inst_amt, ttl_amt] = get_zhangting_sell(symbol, date_str)
    print("{}\t{:.3f}\t{:.5f}\t{:.5f}\t{:.5g}\t{:.5f}\t{:.5f}\t{:.0f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}".format(date_str, chg, fengdan, fengdan_money, zhangting_min, zhangting_force, zhangting_sell, kaipan_money, in_amt, out_amt, inst_amt, ttl_amt))
