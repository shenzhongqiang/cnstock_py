import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from config import store_type
import tushare as ts

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
    df_res = df_industry.groupby("exsymbol")["industry"].agg({"industry": lambda x: ",".join(x)})
    return df_res

def get_concept():
    df = stock.utils.symbol_util.load_concept()
    df_res = df.groupby("exsymbol")["concept"].agg({"concept": lambda x: ",".join(x)})
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

def get_zhangting(today):
    today_str = today.strftime("%Y-%m-%d")
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today["zt_price"] = np.round(df_today["yest_close"] * 1.1, 2)
    df_today["diff2zt"] = df_today["zt_price"] - df_today["close"]
    df_zt = df_today[(df_today.diff2zt<1e-3) & (df_today.lt_mcap>0) & (df_today.volume>0)].copy()
    df_zt.loc[:, "turnover"] = df_zt["volume"]/(df_zt["lt_mcap"]/df_zt["close"]*1e6)
    df_zt.loc[:, "fengdan"] = df_zt["b1_v"] * df_zt["b1_p"] *100 / df_zt["lt_mcap"] / 1e8
    df_zt.loc[:, "fengdan_money"] = df_zt["b1_v"]*df_zt["b1_p"]/1e6

    df_tick = stock.utils.symbol_util.get_tick_by_date(today_str)
    df_res = df_zt.merge(df_tick[["zhangting_sell", "zhangting_min"]], how="inner", left_index=True, right_index=True)

    df_industry = get_industry()
    df_concept = get_concept()
    df_res = df_res.merge(df_industry, how="left", left_index=True, right_index=True)
    columns = ["fengdan", "fengdan_money", "lt_mcap", "turnover", "zhangting_sell", "zhangting_min", "industry"]
    print("========================== zhangting ==========================")
    print(df_res[columns].sort_values("zhangting_sell", ascending=True))


def get_turnover(today):
    today_str = today.strftime("%Y-%m-%d")
    df_today = stock.utils.symbol_util.get_realtime_by_date(today_str)
    df_today.loc[:, "turnover"] = df_today["volume"]/(df_today["lt_mcap"]/df_today["close"]*1e6)
    columns = ["chgperc", "turnover", "mcap", "lt_mcap"]
    df_res = df_today[columns].sort_values("turnover", ascending=False).head(10)
    print("========================== high turnover ==========================")
    print(df_res)

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    get_zhangting(today)
    get_turnover(today)
