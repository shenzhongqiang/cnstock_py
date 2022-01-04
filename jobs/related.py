import argparse
import asyncio
import datetime
import os
import re
import sys

import numpy as np
import pandas as pd

import stock.utils.symbol_util
from stock.globalvar import HIST_DIR, SYM


def get_zt_price(yest_close, percent):
    return int(yest_close*(1+percent)*100+0.50001)/100

def get_stock_zt_price(symbol, yest_close):
    if re.match(r"4", symbol) or re.match(r"8", symbol):
        zt_price = get_zt_price(yest_close, 0.3)
    elif re.match(r"688", symbol) or re.match(r"3", symbol):
        zt_price = get_zt_price(yest_close, 0.2)
    else:
        zt_price = get_zt_price(yest_close, 0.1)
    return zt_price

def get_stock_hist(symbol, date_str):
    stock_dir = HIST_DIR['stock']
    path = os.path.join(stock_dir, symbol)
    if not os.path.isfile(path):
        return None

    with open(path, "r") as f:
        df = pd.read_csv(f)
        index = pd.to_datetime(df.date, format="%Y-%m-%d")
        df.set_index(index, inplace=True)
    df = df.loc[:date_str]
    df = df.iloc[-240:]
    return df

async def get_corr(df_x, symbol_y, date_str):
    df_related = get_stock_hist(symbol_y, date_str)
    if df_related is None or len(df_related) < 200:
        return {"symbol": symbol_y, "corr": np.nan}
    df = pd.merge(df_x, df_related, how="outer", left_index=True, right_index=True, suffixes=("_x", "_y"))
    corr = df["close_x"].corr(df["close_y"])
    drift = df_x.iloc[-1]["close"]/df_x.iloc[-2]["close"] - df_related.iloc[-1]["close"]/df_related.iloc[-2]["close"]
    return {"symbol": symbol_y, "corr": corr, "drift": drift}

async def get_high_corr_stocks(symbol, related_symbols, date_str, corr_min):
    df_symbol = get_stock_hist(symbol, date_str)
    if df_symbol is None or len(df_symbol) < 200:
        return []
    tasks = [get_corr(df_symbol, related_symbol, date_str) for related_symbol in related_symbols]
    result = await asyncio.gather(*tasks)
    result = list(filter(lambda x: x is not None and x["corr"] >= corr_min, result))
    result.sort(key=lambda x: x["corr"], reverse=True)
    return result

async def get_similar_stocks(symbol, date_str, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    df_industry = stock.utils.symbol_util.load_industry()
    concepts = df_concept[df_concept["symbol"] == symbol][["concept_symbol", "concept_name"]].drop_duplicates().values
    industries = df_industry[df_industry["symbol"] == symbol][["industry_symbol", "industry_name"]].drop_duplicates().values
    if len(concepts) == 0 and len(industries) == 0:
        return

    print("========== concept ===========")
    for concept in concepts:
        concept_symbol = concept[0]
        concept_name = concept[1]
        related_symbols = df_concept[df_concept["concept_symbol"]==concept_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, date_str, corr_min)
        print(concept_name)
        print("symbol,corr,drift")
        for item in high_corr_stocks:
            print("{},{:.2f},{:.3f}".format(item["symbol"], item["corr"], item["drift"]))

    print("========== industry ===========")
    for industry in industries:
        industry_symbol = industry[0]
        industry_name = industry[1]
        related_symbols = df_industry[df_industry["industry_symbol"]==industry_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, date_str, corr_min)
        print(industry_name)
        print("symbol,corr,drift")
        for item in high_corr_stocks:
            print("{},{:.2f},{:.3f}".format(item["symbol"], item["corr"], item["drift"]))

async def get_high_corr_concept_pairs(concept_name, date_str, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    stock_items = df_concept[df_concept["concept_name"] == concept_name][["symbol", "name"]].values
    if len(stock_items) == 0:
        print("no such concept: {}".format(concept_name))
    print("x,y,corr,drift")
    for i in range(len(stock_items)):
        stock_item = stock_items[i]
        symbol = stock_item[0]
        related_symbols = list(map(lambda x: x[0], stock_items[i+1:]))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, date_str, corr_min)
        for item in high_corr_stocks:
            print("{},{},{:.2f},{:.3f}".format(symbol, item["symbol"], item["corr"], item["drift"]))

async def get_high_corr_industry_pairs(industry_name, date_str, corr_min):
    df_industry = stock.utils.symbol_util.load_industry()
    stock_items = df_industry[df_industry["industry_name"] == industry_name][["symbol", "name"]].values
    if len(stock_items) == 0:
        print("no such concept: {}".format(industry_name))
    print("x,y,corr,drift")
    for i in range(len(stock_items)):
        stock_item = stock_items[i]
        symbol = stock_item[0]
        related_symbols = list(map(lambda x: x[0], stock_items[i+1:]))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, date_str, corr_min)
        for item in high_corr_stocks:
            print("{},{},{:.2f},{:.3f}".format(symbol, item["symbol"], item["corr"], item["drift"]))

def get_zhangting_stocks(date_str):
    df_date = stock.utils.symbol_util.get_realtime_by_date(date_str)
    df_date.set_index("symbol", inplace=True)
    df_date = df_date[~df_date.isnull().any(axis=1)]
    df_date["zt_price"] = df_date.apply(lambda x: get_stock_zt_price(x.name, x["yest_close"]), axis=1)
    df_date.loc[:, "is_zhangting"] = np.absolute(df_date["zt_price"]-df_date["close"])<1e-8
    df_zt = df_date[(df_date.is_zhangting==True) & (df_date.volume>0)].copy()
    df_zt.loc[:, "fengdan"] = df_zt["b1_v"]*df_zt["b1_p"]/1e6
    wbond_symbols = pd.read_csv(SYM['wbond'], dtype={"正股代码": np.str_}).values
    df_zt["wbond"] = df_zt.index.isin(wbond_symbols)
    columns = ["name", "fengdan", "wbond"]
    print(df_zt[columns].sort_values("fengdan", ascending=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default=None, help="e.g. 2022-01-01")
    parser.add_argument("--zhangting", action="store_true", default=False)
    parser.add_argument("--symbol", type=str, default=None, help="e.g. 600001")
    parser.add_argument("--concept", type=str, default=None, help="元宇宙")
    parser.add_argument("--industry", type=str, default=None, help="煤炭行业")
    parser.add_argument("--corr-min", type=float, default=0.9, help="煤炭行业")

    args = parser.parse_args()
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    date_str = args.date
    if date_str is None:
        date_str = datetime.datetime.today().strftime("%Y-%m-%d")

    if args.zhangting:
        get_zhangting_stocks(date_str)
        sys.exit(0)
    if args.symbol:
        asyncio.run(get_similar_stocks(args.symbol, date_str, args.corr_min))
        sys.exit(0)
    if args.concept:
        asyncio.run(get_high_corr_concept_pairs(args.concept, date_str, args.corr_min))
        sys.exit(0)
    if args.industry:
        asyncio.run(get_high_corr_industry_pairs(args.industry, date_str, args.corr_min))
        sys.exit(0)
