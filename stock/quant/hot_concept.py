import sys
from stock.marketdata.storefactory import get_store
from config import store_type
from stock.utils.symbol_util import load_concept, load_industry, get_realtime_by_date
import numpy as np
import pandas as pd

def get_stock_increase(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    df = pd.DataFrame(columns=["increase"])
    for exsymbol in exsymbols:
        try:
            df_stock = store.get(exsymbol)
            if len(df_stock) < 10:
                continue
            if date not in df_stock.index:
                continue
            idx = df_stock.index.get_loc(date)
            min10 = np.min(df_stock.iloc[idx-10:idx].close)
            increase = df_stock.iloc[idx].close/min10 - 1
            df.loc[exsymbol] = increase
        except Exception as e:
            continue
    return df

def get_best_stock(group):
    idx = group["increase"].idxmax()
    max_increase = group.loc[idx]["increase"]
    dragonhead = group.loc[idx]["exsymbol"]
    return [dragonhead, max_increase]

def get_concept_dragon_head(df, date):
    df_grp = df.groupby("concept")
    df_res = pd.DataFrame(columns=["dragonhead", "increase"])
    for concept, group in df_grp:
        exsymbols = group["exsymbol"]
        [dragonhead, max_increase] = get_best_stock(group)
        df_res.loc[concept] = [dragonhead, max_increase]
    return df_res

def get_industry_dragon_head(df, date):
    df_grp = df.groupby("industry")
    df_res = pd.DataFrame(columns=["dragonhead", "increase"])
    for industry, group in df_grp:
        exsymbols = group["exsymbol"]
        [dragonhead, max_increase] = get_best_stock(group)
        df_res.loc[industry] = [dragonhead, max_increase]
    return df_res

def get_stock_chg(date):
    df = get_realtime_by_date(date)
    df.loc[:, "chg"] = df["chgperc"]/100
    df.loc[:, "zt_price"] = df.yest_close.apply(lambda x: round(x*1.1+1e-8, 2))
    df.loc[:, "is_zhangting"] = (df["zt_price"]-df["close"])<1e-8
    return df

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today().strftime("%Y-%m-%d")
    else:
        today = sys.argv[1]

    df_stock = get_stock_chg(today)
    df_concept = load_concept()
    df_increase = get_stock_increase(today)
    df_res = df_concept.merge(df_stock, how="inner", left_on="exsymbol", right_index=True)
    df_res = df_res.merge(df_increase, how="inner", left_on="exsymbol", right_index=True)
    df_chg = df_res.groupby("concept")["chg"].agg(["mean", "count"]).rename(columns={"mean": "avg_chg", "count": "num_stock"}).sort_values("avg_chg")
    df_dragon = get_concept_dragon_head(df_res, today)
    df_chg = df_chg.merge(df_dragon, how="left", left_on="concept", right_index=True)
    print("======================= concept avg changes ========================")
    print(df_chg[df_chg.num_stock>5].tail(10))

    df_zt = df_res.groupby("concept")["is_zhangting"].agg(["sum"]).rename(columns={"sum": "num_zhangting"})
    df_hot = df_zt.merge(df_dragon, how="left", left_on="concept", right_index=True)
    df_hot = df_hot[df_hot.num_zhangting>=3]
    df_hot_stocks = df_res[df_res.concept.isin(df_hot.index) & df_res.is_zhangting==True]
    columns = ["concept", "exsymbol", "chg"]
    print("======================= concept zhangting num ========================")
    #print(df_hot_stocks[columns])
    print(df_hot.sort_values("num_zhangting"))

    df_industry = load_industry()
    df_res = df_industry.merge(df_stock, how="inner", left_on="exsymbol", right_index=True)
    df_res = df_res.merge(df_increase, how="inner", left_on="exsymbol", right_index=True)
    df_chg = df_res.groupby("industry")["chg"].agg(["mean", "count"]).rename(columns={"mean": "avg_chg", "count": "num_stock"}).sort_values("avg_chg")
    df_dragon = get_industry_dragon_head(df_res, today)
    df_chg = df_chg.merge(df_dragon, how="left", left_on="industry", right_index=True)
    print("======================= industry avg changes ========================")
    print(df_chg[df_chg.num_stock>5].tail(10))

    df_zt = df_res.groupby("industry")["is_zhangting"].agg(["sum"]).rename(columns={"sum": "num_zhangting"})
    df_hot = df_zt.merge(df_dragon, how="left", left_on="industry", right_index=True)
    df_hot = df_hot[df_hot.num_zhangting>=3]
    df_hot_stocks = df_res[df_res.industry.isin(df_hot.index) & df_res.is_zhangting==True]
    columns = ["industry", "exsymbol", "chg"]
    print("======================= industry zhangting num ========================")
    #print(df_hot_stocks[columns])
    print(df_hot.sort_values("num_zhangting"))
