import argparse
import sys
from stock.marketdata.storefactory import get_store
from config import store_type
from stock.utils.symbol_util import load_concept, load_industry, get_realtime_by_date, get_stock_basics
import numpy as np
import pandas as pd

def get_stock_increase(date):
    store = get_store(store_type)
    exsymbols = store.get_stock_exsymbols()
    df = pd.DataFrame(columns=["increase", "turnover"])
    df_basics = get_stock_basics()
    for exsymbol in exsymbols:
        try:
            df_stock = store.get(exsymbol)
            if len(df_stock) < 10:
                continue
            if date not in df_stock.index:
                continue
            idx = df_stock.index.get_loc(date)
            min10 = np.min(df_stock.iloc[idx-1:idx].close)
            increase = df_stock.iloc[idx].close/min10 - 1
            outstanding = df_basics.loc[exsymbol]["outstanding"]
            turnover = df_stock.iloc[idx].volume/outstanding/1e6
            df.loc[exsymbol] = [increase, turnover]
        except Exception as e:
            continue
    return df

def get_best_stock(group):
    idx = group["increase"].idxmax()
    if np.isnan(idx):
        return [np.nan, np.nan, np.nan, np.nan]
    max_increase = group.loc[idx]["increase"]
    dragon_increase = group.loc[idx]["exsymbol"]
    idx = group["turnover"].idxmax()
    max_turnover = group.loc[idx]["turnover"]
    dragon_turnover = group.loc[idx]["exsymbol"]
    return [dragon_increase, max_increase, dragon_turnover, max_turnover]

def get_concept_dragon_head(df, date):
    df_grp = df.groupby("concept")
    df_res = pd.DataFrame(columns=["dragon_incr", "increase", "dragon_tnov", "turnover"])
    for concept, group in df_grp:
        exsymbols = group["exsymbol"]
        df_res.loc[concept] = get_best_stock(group)
    return df_res

def get_industry_dragon_head(df, date):
    df_grp = df.groupby("industry")
    df_res = pd.DataFrame(columns=["dragon_incr", "increase", "dragon_tnov", "turnover"])
    for industry, group in df_grp:
        exsymbols = group["exsymbol"]
        df_res.loc[industry] = get_best_stock(group)
    return df_res

def get_stock_chg(date):
    df = get_realtime_by_date(date)
    df.loc[:, "chg"] = df["chgperc"]/100
    df.loc[:, "zt_price"] = df.yest_close.apply(lambda x: round(x*1.1+1e-8, 2))
    df.loc[:, "is_zhangting"] = (df["zt_price"]-df["close"])<1e-8
    return df

def get_lianban(date):
    df = get_realtime_by_date(date)
    df.loc[:, "zt_price"] = df.yest_close.apply(lambda x: round(x*1.1+1e-8, 2))
    df.loc[:, "is_zhangting"] = (df["zt_price"]-df["close"])<1e-8
    df_zt = df[df.is_zhangting==True]

    store = get_store(store_type)
    for exsymbol in df_zt.index.tolist():
        try:
            df_stock = store.get(exsymbol)
            idx = df_stock.index.get_loc(date)
            df_stock = df_stock.iloc[:idx+1]
            df_stock.loc[:, "zt_price"] = df_stock.close.shift(1).apply(lambda x: round(x*1.1+1e-8, 2))
            df_stock.loc[:, "is_zhangting"] = np.absolute(df_stock["zt_price"]-df_stock["close"])<1e-8
            df_nozt = df_stock[df_stock.is_zhangting==False]
            lianban = 0
            if len(df_nozt) == 0:
                lianban = len(df_stock)
            else:
                idx_start = df_stock.index.get_loc(df_nozt.index[-1])
                idx_end = df_stock.index.get_loc(df_stock.index[-1])
                lianban = idx_end - idx_start
            df_zt.loc[exsymbol, "lianban"] = lianban
            df_zt.loc[exsymbol, "xingu"] = lianban == len(df_stock)-1
        except:
            continue

    columns = ["lianban", "xingu"]
    return df_zt[df_zt.xingu==False][columns].sort_values("lianban")

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    parser = argparse.ArgumentParser()
    parser.add_argument('date', nargs='?', help='date')
    parser.add_argument('--stock', dest='stock', action='store_true', help='list stocks')
    opt = parser.parse_args()
    today = None
    if opt.date is None:
        today = pd.datetime.today().strftime("%Y-%m-%d")
    else:
        today = opt.date

    df_stock = get_stock_chg(today)
    df_concept = load_concept()
    df_increase = get_stock_increase(today)
    df_res = df_concept.merge(df_stock, how="inner", left_on="exsymbol", right_index=True)
    df_res = df_res.merge(df_increase, how="inner", left_on="exsymbol", right_index=True)
    df_dragon = get_concept_dragon_head(df_res, today)
    df_concept_grp = df_res.groupby("concept")["chg"].agg(["mean", "count"]).rename(columns={"mean": "avg_chg", "count": "num_stock"}).sort_values("avg_chg")
    df_concept_grp = df_concept_grp.merge(df_dragon, how="left", left_on="concept", right_index=True)
    print("======================= concept avg changes ========================")
    print(df_concept_grp[df_concept_grp.num_stock>5].tail(10))

    df_zt = df_res.groupby("concept")["is_zhangting"].agg(["sum"]).rename(columns={"sum": "num_zhangting"})
    df_concept_hot = df_zt[df_zt.num_zhangting>=1]
    df_concept_hot = df_concept_hot.merge(df_dragon, how="left", left_on="concept", right_index=True).sort_values("num_zhangting")
    print("======================= concept zhangting num ========================")
    print(df_concept_hot)

    df_concept_hot_stocks = None
    if opt.stock:
        print("======================= concept zhangting stocks ========================")
        df_concept_hot_stocks = df_res[df_res.is_zhangting==True].merge(df_concept_hot[["num_zhangting"]], left_on="concept", right_index=True)
        df_concept_hot_stocks = df_concept_hot_stocks.sort_values(["num_zhangting", "concept"])
        columns = ["exsymbol", "chg", "increase", "turnover", "concept"]
        df_concept_hot_stocks = df_concept_hot_stocks[columns]
        print(df_concept_hot_stocks)

    df_industry = load_industry()
    df_res = df_industry.merge(df_stock, how="inner", left_on="exsymbol", right_index=True)
    df_res = df_res.merge(df_increase, how="inner", left_on="exsymbol", right_index=True)
    df_dragon = get_industry_dragon_head(df_res, today)
    df_industry_grp = df_res.groupby("industry")["chg"].agg(["mean", "count"]).rename(columns={"mean": "avg_chg", "count": "num_stock"}).sort_values("avg_chg")
    df_industry_grp = df_industry_grp.merge(df_dragon, how="left", left_on="industry", right_index=True)
    print("======================= industry avg changes ========================")
    print(df_industry_grp[df_industry_grp.num_stock>5].tail(10))

    df_zt = df_res.groupby("industry")["is_zhangting"].agg(["sum"]).rename(columns={"sum": "num_zhangting"})
    df_industry_hot = df_zt[df_zt.num_zhangting>=1]
    df_industry_hot = df_industry_hot.merge(df_dragon, how="left", left_on="industry", right_index=True).sort_values("num_zhangting")
    print("======================= industry zhangting num ========================")
    print(df_industry_hot)

    df_industry_hot_stocks = None
    if opt.stock:
        print("======================= industry zhangting stocks ========================")
        df_industry_hot_stocks = df_res[df_res.is_zhangting==True].merge(df_industry_hot[["num_zhangting"]], left_on="industry", right_index=True)
        df_industry_hot_stocks = df_industry_hot_stocks.sort_values(["num_zhangting", "industry"])
        columns = ["exsymbol", "chg", "increase", "turnover", "industry"]
        df_industry_hot_stocks = df_industry_hot_stocks[columns]
        print(df_industry_hot_stocks)

    df_lianban = get_lianban(today)
    print("======================= lianban ========================")
    print(df_lianban)
    print("zt_num:", len(df_lianban))

    with open("/var/www/stock/index.html", "w", encoding="gbk") as f:
        print("======================= concept avg changes ========================")
        f.write(df_concept_grp[df_concept_grp.num_stock>5].tail(10).to_html())
        f.write("<br/><br/>")
        print("======================= concept zhangting num ========================")
        f.write(df_concept_hot.to_html())
        f.write("<br/><br/>")
        print("======================= industry avg changes ========================")
        f.write(df_industry_grp[df_industry_grp.num_stock>5].tail(10).to_html())
        f.write("<br/><br/>")
        print("======================= industry zhangting num ========================")
        f.write(df_industry_hot.to_html())
        f.write("<br/><br/>")
        print("======================= lianban ========================")
        f.write(df_lianban.to_html())
        if opt.stock:
            f.write("<br/><br/>")
            print("======================= concept zhangting stocks ========================")
            f.write(df_concept_hot_stocks.to_html())
            f.write("<br/><br/>")
            print("======================= industry zhangting stocks ========================")
            f.write(df_industry_hot_stocks.to_html())
