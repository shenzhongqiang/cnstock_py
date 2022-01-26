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

EXCLUDE_CONCEPTS = ["融资融券", "机构重仓", "富时罗素", "MSCI中国", "标准普尔", "沪股通", "HS300_", "上证180_", "上证50_",
                    "证金持股", "央视50_", "深证100R", "中证500", "ST股", "深成500", "上证380", "深股通", "创业成份",
                    "QFII重仓", "转债标的", "基金重仓", "创业板综", "昨日连板_含一字", "AH股", "GDR", "中字头", "茅指数",
                    "B股", "IPO受益", "举牌", "低价股", "养老金", "昨日涨停", "昨日涨停_含一字", "昨日触板", "昨日连板",
                    "贬值受益", "预亏预减", "高送转"]


def get_zt_price(yest_close, percent):
    return int(yest_close * (1 + percent) * 100 + 0.50001) / 100


def get_stock_zt_price(symbol, yest_close):
    if re.match(r"4", symbol) or re.match(r"8", symbol):
        zt_price = get_zt_price(yest_close, 0.3)
    elif re.match(r"688", symbol) or re.match(r"3", symbol):
        zt_price = get_zt_price(yest_close, 0.2)
    else:
        zt_price = get_zt_price(yest_close, 0.1)
    return zt_price


def get_stock_hist(symbol, start_date, end_date):
    stock_dir = HIST_DIR['stock']
    path = os.path.join(stock_dir, symbol)
    if not os.path.isfile(path):
        return None

    with open(path, "r") as f:
        df = pd.read_csv(f)
        index = pd.to_datetime(df.date, format="%Y-%m-%d")
        df.set_index(index, inplace=True)
    df = df.loc[start_date:end_date]
    return df


async def get_corr(df_x, symbol_y, start_date, end_date):
    df_related = get_stock_hist(symbol_y, start_date, end_date)
    if df_related is None:
        return {"symbol": symbol_y, "corr": np.nan}
    df = pd.merge(df_x, df_related, how="outer", left_index=True, right_index=True, suffixes=("_x", "_y"))
    corr = df["close_x"].corr(df["close_y"])
    if len(df_x) < 2 or len(df_related) < 2:
        drift = np.nan
    else:
        drift = df_x.iloc[-1]["close"] / df_x.iloc[-2]["close"] - df_related.iloc[-1]["close"] / df_related.iloc[-2][
            "close"]
    return {"symbol": symbol_y, "corr": corr, "drift": drift}


async def get_chg(symbol, start_date, end_date):
    df = get_stock_hist(symbol, start_date, end_date)
    if df is None or len(df) < 2 or end_date not in df.index:
        return {"symbol": symbol, "chg": np.nan}
    chg = df.iloc[-1]["close"] / df.iloc[-2]["close"] - 1
    return {"symbol": symbol, "chg": chg}


async def get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min):
    df_symbol = get_stock_hist(symbol, start_date, end_date)
    if df_symbol is None:
        return []
    tasks = [get_corr(df_symbol, related_symbol, start_date, end_date) for related_symbol in related_symbols]
    result = await asyncio.gather(*tasks)
    result = list(filter(lambda x: x is not None and x["corr"] >= corr_min, result))
    result.sort(key=lambda x: x["corr"], reverse=True)
    return result


async def get_similar_stocks_between_dates(symbol, start_date, end_date, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    df_industry = stock.utils.symbol_util.load_industry()
    concepts = df_concept[(df_concept["symbol"] == symbol)][~df_concept["concept_name"].isin(EXCLUDE_CONCEPTS)][
        ["concept_symbol", "concept_name"]].drop_duplicates().values
    industries = df_industry[df_industry["symbol"] == symbol][
        ["industry_symbol", "industry_name"]].drop_duplicates().values
    if len(concepts) == 0 and len(industries) == 0:
        return

    print("========== concept ===========")
    for concept in concepts:
        concept_symbol = concept[0]
        concept_name = concept[1]
        related_symbols = df_concept[df_concept["concept_symbol"] == concept_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min)
        print(concept_name)
        print("symbol,corr,drift")
        for item in high_corr_stocks:
            print("{},{:.2f},{:.3f}".format(item["symbol"], item["corr"], item["drift"]))

    print("========== industry ===========")
    for industry in industries:
        industry_symbol = industry[0]
        industry_name = industry[1]
        related_symbols = df_industry[df_industry["industry_symbol"] == industry_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min)
        print(industry_name)
        print("symbol,corr,drift")
        for item in high_corr_stocks:
            print("{},{:.2f},{:.3f}".format(item["symbol"], item["corr"], item["drift"]))


async def get_high_chg_stocks(symbol, related_symbols, date, chg_min):
    format = "%Y-%m-%d"
    end_dt = datetime.datetime.strptime(date, format)
    start_dt = end_dt - datetime.timedelta(days=1)
    start_date = start_dt.strftime(format)
    df_symbol = get_stock_hist(symbol, start_date, date)
    if df_symbol is None or date not in df_symbol.index:
        return []
    tasks = [get_chg(related_symbol, start_date, date) for related_symbol in related_symbols]
    result = await asyncio.gather(*tasks)
    result = list(filter(lambda x: x is not None and x["chg"] >= chg_min, result))
    result.sort(key=lambda x: x["chg"], reverse=True)
    return result


async def get_similar_stocks_on_date(symbol, date, chg_min):
    df_concept = stock.utils.symbol_util.load_concept()
    df_industry = stock.utils.symbol_util.load_industry()
    concepts = df_concept[(df_concept["symbol"] == symbol)][~df_concept["concept_name"].isin(EXCLUDE_CONCEPTS)][
        ["concept_symbol", "concept_name"]].drop_duplicates().values
    industries = df_industry[df_industry["symbol"] == symbol][
        ["industry_symbol", "industry_name"]].drop_duplicates().values
    if len(concepts) == 0 and len(industries) == 0:
        return

    print("========== concept ===========")
    for concept in concepts:
        concept_symbol = concept[0]
        concept_name = concept[1]
        related_symbols = df_concept[df_concept["concept_symbol"] == concept_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_chg_stocks = await get_high_chg_stocks(symbol, related_symbols, date, chg_min)
        print(concept_name)
        print("symbol,chg")
        for item in high_chg_stocks:
            print("{},{:.3f}".format(item["symbol"], item["chg"]))

    print("========== industry ===========")
    for industry in industries:
        industry_symbol = industry[0]
        industry_name = industry[1]
        related_symbols = df_industry[df_industry["industry_symbol"] == industry_symbol]["symbol"].values
        related_symbols = list(filter(lambda x: x != symbol, related_symbols))
        high_chg_stocks = await get_high_chg_stocks(symbol, related_symbols, date, chg_min)
        print(industry_name)
        print("symbol,chg")
        for item in high_chg_stocks:
            print("{},{:.3f}".format(item["symbol"], item["chg"]))


async def get_high_corr_concept_pairs(concept_name, start_date, end_date, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    stock_items = df_concept[df_concept["concept_name"] == concept_name][["symbol", "name"]].values
    if len(stock_items) == 0:
        print("no such concept: {}".format(concept_name))
    print("x,y,corr,drift")
    for i in range(len(stock_items)):
        stock_item = stock_items[i]
        symbol = stock_item[0]
        related_symbols = list(map(lambda x: x[0], stock_items[i + 1:]))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min)
        for item in high_corr_stocks:
            print("{},{},{:.2f},{:.3f}".format(symbol, item["symbol"], item["corr"], item["drift"]))


async def get_high_corr_industry_pairs(industry_name, start_date, end_date, corr_min):
    df_industry = stock.utils.symbol_util.load_industry()
    stock_items = df_industry[df_industry["industry_name"] == industry_name][["symbol", "name"]].values
    if len(stock_items) == 0:
        print("no such concept: {}".format(industry_name))
    print("x,y,corr,drift")
    for i in range(len(stock_items)):
        stock_item = stock_items[i]
        symbol = stock_item[0]
        related_symbols = list(map(lambda x: x[0], stock_items[i + 1:]))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min)
        for item in high_corr_stocks:
            print("{},{},{:.2f},{:.3f}".format(symbol, item["symbol"], item["corr"], item["drift"]))


def get_zhangting_stocks(date_str):
    df_date = stock.utils.symbol_util.get_realtime_by_date(date_str)
    df_date.set_index("symbol", inplace=True)
    df_date = df_date[~df_date.isnull().any(axis=1)]
    df_date["zt_price"] = df_date.apply(lambda x: get_stock_zt_price(x.name, x["yest_close"]), axis=1)
    df_date.loc[:, "is_zhangting"] = np.absolute(df_date["zt_price"] - df_date["close"]) < 1e-8
    df_zt = df_date[(df_date.is_zhangting == True) & (df_date.volume > 0)].copy()
    df_zt.loc[:, "open_zt"] = df_zt["open"] == df_zt["zt_price"]
    df_zt.loc[:, "fengdan"] = df_zt["b1_v"] * df_zt["b1_p"] / 1e6
    wbond_symbols = pd.read_csv(SYM['wbond'], dtype={"正股代码": np.str_})["正股代码"].values
    df_zt["wbond"] = df_zt.index.isin(wbond_symbols)
    columns = ["name", "fengdan", "wbond", "open_zt"]
    print(df_zt[columns].sort_values("fengdan", ascending=False))


async def get_all_pairs():
    format = "%Y-%m-%d"
    end_dt = datetime.datetime.today()
    start_dt = end_dt - datetime.timedelta(days=240)
    start_date = start_dt.strftime(format)
    end_date = end_dt.strftime(format)
    df_concept = stock.utils.symbol_util.load_concept()
    grouped = df_concept.groupby("concept_name")
    for concept_name, group in grouped:
        if len(group) <= 20:
            print(concept_name, len(group))
            await get_high_corr_concept_pairs(concept_name, start_date, end_date, corr_min=0.9)

    print("==========")
    df_industry = stock.utils.symbol_util.load_industry()
    grouped = df_industry.groupby("industry_name")
    for industry_name, group in grouped:
        if len(group) <= 30:
            print(industry_name, len(group))
            await get_high_corr_industry_pairs(industry_name, start_date, end_date, corr_min=0.9)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, default=None, help="e.g. 2021-01-04")
    parser.add_argument("--end", type=str, default=None, help="e.g. 2022-01-04")
    parser.add_argument("--date", type=str, default=None, help="e.g. 2022-01-04")
    parser.add_argument("--zhangting", action="store_true", default=False)
    parser.add_argument("--symbol", type=str, default=None, help="e.g. 600001")
    parser.add_argument("--concept", type=str, default=None, help="e.g. 元宇宙")
    parser.add_argument("--industry", type=str, default=None, help="e.g. 煤炭行业")
    parser.add_argument("--corr-min", type=float, default=0.9, help="e.g. 0.9")
    parser.add_argument("--chg-min", type=float, default=0.09, help="e.g. 0.09")
    parser.add_argument("--pairs", action="store_true", default=False, help="get all highly related stock pairs")

    args = parser.parse_args()
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    format = "%Y-%m-%d"
    end_date = args.end
    if end_date is None:
        end_date = datetime.datetime.today().strftime(format)
    start_date = args.start
    if start_date is None:
        end_dt = datetime.datetime.strptime(end_date, format)
        start_dt = end_dt - datetime.timedelta(days=240)
        start_date = start_dt.strftime(format)

    if args.zhangting:
        get_zhangting_stocks(end_date)
        sys.exit(0)
    if args.symbol and args.date is not None:
        asyncio.run(get_similar_stocks_on_date(args.symbol, args.date, args.chg_min))
        sys.exit(0)
    if args.symbol:
        asyncio.run(get_similar_stocks_between_dates(args.symbol, start_date, end_date, args.corr_min))
        sys.exit(0)
    if args.concept:
        asyncio.run(get_high_corr_concept_pairs(args.concept, start_date, end_date, args.corr_min))
        sys.exit(0)
    if args.industry:
        asyncio.run(get_high_corr_industry_pairs(args.industry, start_date, end_date, args.corr_min))
        sys.exit(0)
    if args.pairs:
        asyncio.run(get_all_pairs())
        sys.exit(0)
