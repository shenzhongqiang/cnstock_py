import sys
import numpy as np
import pandas as pd
import stock.utils.symbol_util
from stock.globalvar import *
from stock.marketdata.storefactory import get_store
from config import store_type
from pandas.tseries.offsets import BDay
import tushare as ts
from stock.utils.calc_price import get_zt_price

def get_last_trading_date(today):
    yest = today - BDay(1)
    folder = TICK_DIR["daily"]
    while True:
        yest_str = yest.strftime("%Y-%m-%d")
        filepath = os.path.join(folder, yest_str + ".csv")
        if os.path.isfile(filepath):
            break
        yest = yest - BDay(1)
    return yest

def get_industry():
    df_industry = stock.utils.symbol_util.load_industry()
    df_res = df_industry.groupby("exsymbol")["industry"].agg(industry=lambda x: ",".join(x))
    return df_res

def get_concept():
    df = stock.utils.symbol_util.load_concept()
    df_res = df.groupby("exsymbol")["concept"].agg(concept=lambda x: ",".join(x))
    return df_res

def filter_by_history(date, exsymbols):
    store = get_store(store_type)
    result = []
    df = pd.DataFrame(columns=["increase60", "increase5", "future"])
    for exsymbol in exsymbols:
        if not store.has(exsymbol):
            continue
        df_stock = store.get(exsymbol)
        df_past = df_stock.loc[:date].copy()
        if len(df_past) == 0:
            continue
        close_min60 = np.min(df_past.iloc[-60:].close)
        close_min5 = np.min(df_past.iloc[-5:].close)
        increase60 = df_past.iloc[-1].close/close_min60-1
        increase5 = df_past.iloc[-1].close/close_min5-1
        future = df_stock.iloc[-1].close/df_past.iloc[-1].close-1
        df.loc[exsymbol] = [increase60, increase5, future]
    return df

def get_lianban(exsymbol, date):
    store = get_store(store_type)
    lianban = -1
    xingu = None
    try:
        df_stock = store.get(exsymbol)
        idx = df_stock.index.get_loc(date)
        df_stock = df_stock.iloc[:idx+1]
        df_stock.loc[:, "zt_price"] = df_stock.close.shift(1).apply(lambda x: get_zt_price(exsymbol[2:], x))
        df_stock.loc[:, "is_zhangting"] = np.absolute(df_stock["zt_price"]-df_stock["close"])<1e-8
        df_nozt = df_stock[df_stock.is_zhangting==False]
        lianban = 0
        if len(df_nozt) == 0:
            lianban = len(df_stock)
        else:
            idx_start = df_stock.index.get_loc(df_nozt.index[-1])
            idx_end = df_stock.index.get_loc(df_stock.index[-1])
            lianban = idx_end - idx_start
        xingu = lianban == len(df_stock)-1
    except Exception as e:
        print(str(e))
        pass

    return (lianban, xingu)

def get_zhangting(today):
    today_str = today.strftime("%Y-%m-%d")
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today["zt_price"] = df_today.apply(lambda x: get_zt_price(x.name[2:], x["yest_close"]), axis=1)
    df_today.loc[:, "is_zhangting"] = np.absolute(df_today["zt_price"]-df_today["close"])<1e-8
    df_zt = df_today[(df_today.is_zhangting==True) & (df_today.lt_mcap>0) & (df_today.volume>0)].copy()
    df_zt.loc[:, "turnover"] = df_zt["volume"]/(df_zt["lt_mcap"]/df_zt["close"]*1e6)
    df_zt.loc[:, "fengdan"] = df_zt["b1_v"] * df_zt["b1_p"] *100 / df_zt["lt_mcap"] / 1e8
    df_zt.loc[:, "fengdan_money"] = df_zt["b1_v"]*df_zt["b1_p"]/1e6
    for exsymbol in df_zt.index.tolist():
        (lianban, xingu) = get_lianban(exsymbol, today_str)
        df_zt.loc[exsymbol, "lianban"] = lianban
        df_zt.loc[exsymbol, "xingu"] = xingu

    df_zt = df_zt[df_zt.xingu==False]
    df_tick = stock.utils.symbol_util.get_tick_by_date(today_str)
    df_res = df_zt.merge(df_tick[["zhangting_sell", "zhangting_min", "cost"]], how="inner", left_index=True, right_index=True)
    df_res["costoverflow"] = df_res["cost"] / df_res["close"]
    df_industry = get_industry()
    df_concept = get_concept()
    df_res = df_res.merge(df_industry, how="left", left_index=True, right_index=True)
    columns = ["fengdan", "fengdan_money", "lt_mcap", "zhangting_sell", "lianban", "industry"]
    print("========================== zhangting ==========================")
    print(df_res[columns].sort_values(["lianban"], ascending=False))


def get_duanban(today):
    today_str = today.strftime("%Y-%m-%d")
    yest = get_last_trading_date(today)
    yest_str = yest.strftime("%Y-%m-%d")
    df_yest = stock.utils.symbol_util.get_realtime_by_date(yest_str)
    df_yest["zt_price"] = df_yest.apply(lambda x: get_zt_price(x.name[2:], x["yest_close"]), axis=1)
    df_yest.loc[:, "is_zhangting"] = np.absolute(df_yest["zt_price"]-df_yest["close"])<1e-8
    df_yest_zt = df_yest[(df_yest.is_zhangting==True) & (df_yest.lt_mcap>0) & (df_yest.volume>0)].copy()
    for exsymbol in df_yest_zt.index.tolist():
        (lianban, xingu) = get_lianban(exsymbol, yest_str)
        df_yest_zt.loc[exsymbol, "lianban"] = lianban
        df_yest_zt.loc[exsymbol, "xingu"] = xingu

    df_yest_zt = df_yest_zt[df_yest_zt.xingu==False]
    df_yest_zt.loc[:, "fengdan"] = df_yest_zt["b1_v"] * df_yest_zt["b1_p"] *100 / df_yest_zt["lt_mcap"] / 1e8
    df_yest_zt.loc[:, "fengdan_money"] = df_yest_zt["b1_v"]*df_yest_zt["b1_p"]/1e6

    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today["zt_price"] = df_today.apply(lambda x: get_zt_price(x.name[2:], x["yest_close"]), axis=1)
    df_today.loc[:, "is_zhangting"] = np.absolute(df_today["zt_price"]-df_today["close"])<1e-8
    df_today_nozt = df_today[(df_today.is_zhangting==False) & (df_today.lt_mcap>0) & (df_today.volume>0)].copy()

    df_res = df_yest_zt.merge(df_today_nozt[["chgperc"]], how="inner", left_index=True, right_index=True)

    df_industry = get_industry()
    df_res = df_res.merge(df_industry, how="left", left_index=True, right_index=True)
    columns = ["fengdan", "fengdan_money", "chgperc_y", "lt_mcap", "lianban", "industry"]
    print("========================== duanban ==========================")
    print(df_res[columns].sort_values(["lianban"], ascending=False))

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    get_zhangting(today)
    get_duanban(today)
