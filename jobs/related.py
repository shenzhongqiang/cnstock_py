import argparse
import asyncio
import datetime
import os
import re
import sys

import numpy as np
import pandas as pd

import stock.utils.symbol_util
from stock.globalvar import HIST_DIR, SYM, BASIC_DIR

EXCLUDE_CONCEPTS = ["融资融券", "机构重仓", "富时罗素", "MSCI中国", "标准普尔", "沪股通", "HS300_", "上证180_", "上证50_",
                    "证金持股", "央视50_", "深证100R", "中证500", "ST股", "深成500", "上证380", "深股通", "创业成份",
                    "QFII重仓", "转债标的", "基金重仓", "创业板综", "昨日连板_含一字", "AH股", "GDR", "中字头", "茅指数",
                    "B股", "IPO受益", "举牌", "低价股", "养老金", "昨日涨停", "昨日涨停_含一字", "昨日触板", "昨日连板",
                    "贬值受益", "预盈预增", "预亏预减", "高送转", "百元股", "社保重仓", "参股新三板", "内贸流通", "股权激励",
                    "AB股", "独角兽", "壳资源", "分拆预期", "债转股", "送转预期", ]


GROUP_TYPE_CONCEPT = "concept"
GROUP_TYPE_INDUSTRY = "industry"

class CorrResult(object):
    def __init__(self, symbol_x, symbol_y, corr):
        self.symbol_x = symbol_x
        self.symbol_y = symbol_y
        self.corr = corr

    def __repr__(self):
        return '<CorrResult symbol_x="{}" symbol_y="{}" corr="{}">'.format(self.symbol_x, self.symbol_y, self.corr)


class GroupCorrResult(object):
    def __init__(self, group_name, corr_results, group_type):
        self.group_name = group_name
        self.corr_results = sorted(corr_results, key=lambda x: x.corr, reverse=True)
        self.group_type = group_type

    def print(self):
        print("{}: {}", self.group_type, self.group_name)
        for corr_result in self.corr_results:
            print("{},{},{:.3f}".format(corr_result.symbol_x, corr_result.symbol_y, corr_result.corr))


class HistoryStore(object):
    def __init__(self, symbols):
        self.store = {}
        for symbol in symbols:
            df = self.__class__.load_history(symbol)
            self.store[symbol] = df

    @classmethod
    def load_history(cls, symbol):
        stock_dir = HIST_DIR['stock']
        path = os.path.join(stock_dir, symbol)
        if not os.path.isfile(path):
            return None

        with open(path, "r") as f:
            df = pd.read_csv(f)
            index = pd.to_datetime(df.date, format="%Y-%m-%d")
            df.set_index(index, inplace=True)
        return df

    def get_history(self, symbol, start_date, end_date):
        if symbol in self.store:
            df = self.store[symbol]
            if df is not None:
                return df.loc[start_date:end_date]
        return None


def remove_b(symbols):
    result = list(filter(lambda x: not re.match(r'900', x), symbols))
    return result


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


async def get_corr(symbol_x, symbol_y, start_date, end_date, store):
    df_x = store.get_history(symbol_x, start_date, end_date)
    df_y = store.get_history(symbol_y, start_date, end_date)
    if df_x is None or df_y is None:
        return CorrResult(symbol_x, symbol_y, np.nan)
    df = pd.merge(df_x, df_y, how="outer", left_index=True, right_index=True, suffixes=("_x", "_y"))
    corr = df["close_x"].corr(df["close_y"])
    return CorrResult(symbol_x, symbol_y, corr)


async def get_chg(symbol, start_date, end_date, store):
    df = store.get_history(symbol, start_date, end_date)
    if df is None or len(df) < 2 or end_date not in df.index:
        return {"symbol": symbol, "chg": np.nan}
    chg = df.iloc[-1]["close"] / df.iloc[-2]["close"] - 1
    return {"symbol": symbol, "chg": chg}


async def get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min, store):
    tasks = [get_corr(symbol, related_symbol, start_date, end_date, store) for related_symbol in related_symbols]
    result = await asyncio.gather(*tasks)
    result = list(filter(lambda x: x is not None and x.corr >= corr_min, result))
    result.sort(key=lambda x: x.corr, reverse=True)
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

    result = []
    for concept in concepts:
        concept_symbol = concept[0]
        concept_name = concept[1]
        concept_symbols = df_concept[df_concept["concept_symbol"] == concept_symbol]["symbol"].values
        store = HistoryStore(concept_symbols, start_date, end_date)
        related_symbols = list(filter(lambda x: x != symbol, concept_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min, store)
        group_result = GroupCorrResult(concept_name, high_corr_stocks, GROUP_TYPE_CONCEPT)
        result.append(group_result)

    for industry in industries:
        industry_symbol = industry[0]
        industry_name = industry[1]
        industry_symbols = df_industry[df_industry["industry_symbol"] == industry_symbol]["symbol"].values
        store = HistoryStore(industry_symbols, start_date, end_date)
        related_symbols = list(filter(lambda x: x != symbol, industry_symbols))
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min, store)
        group_result = GroupCorrResult(industry_name, high_corr_stocks, GROUP_TYPE_INDUSTRY)
        result.append(group_result)
    return result


async def get_high_chg_stocks(symbol, related_symbols, date, chg_min, store):
    format = "%Y-%m-%d"
    end_dt = datetime.datetime.strptime(date, format)
    start_dt = end_dt - datetime.timedelta(days=1)
    start_date = start_dt.strftime(format)
    df_symbol = store.get_history(symbol, start_date, date)
    if df_symbol is None or date not in df_symbol.index:
        return []
    tasks = [get_chg(related_symbol, start_date, date, store) for related_symbol in related_symbols]
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
        concept_symbols = df_concept[df_concept["concept_symbol"] == concept_symbol]["symbol"].values
        store = HistoryStore(concept_symbols)
        related_symbols = list(filter(lambda x: x != symbol, concept_symbols))
        high_chg_stocks = await get_high_chg_stocks(symbol, related_symbols, date, chg_min, store)
        print(concept_name)
        print("symbol,chg")
        for item in high_chg_stocks:
            print("{},{:.3f}".format(item["symbol"], item["chg"]))

    print("========== industry ===========")
    for industry in industries:
        industry_symbol = industry[0]
        industry_name = industry[1]
        industry_symbols = df_industry[df_industry["industry_symbol"] == industry_symbol]["symbol"].values
        store = HistoryStore(industry_symbols)
        related_symbols = list(filter(lambda x: x != symbol, industry_symbols))
        high_chg_stocks = await get_high_chg_stocks(symbol, related_symbols, date, chg_min, store)
        print(industry_name)
        print("symbol,chg")
        for item in high_chg_stocks:
            print("{},{:.3f}".format(item["symbol"], item["chg"]))


async def get_high_corr_concept_pairs(concept_name, start_date, end_date, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    symbols = df_concept[df_concept["concept_name"] == concept_name]["symbol"].tolist()
    symbols = remove_b(symbols)
    if len(symbols) == 0:
        print("no such concept: {}".format(concept_name))
    store = HistoryStore(symbols)
    result = []
    for i in range(len(symbols)):
        symbol = symbols[i]
        related_symbols = symbols[i + 1:]
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min, store)
        for item in high_corr_stocks:
            result.append(CorrResult(symbol, item.symbol_y, item.corr))
    return GroupCorrResult(concept_name, result, GROUP_TYPE_CONCEPT)


async def get_high_corr_industry_pairs(industry_name, start_date, end_date, corr_min):
    df_industry = stock.utils.symbol_util.load_industry()
    symbols = df_industry[df_industry["industry_name"] == industry_name]["symbol"].tolist()
    symbols = remove_b(symbols)
    if len(symbols) == 0:
        print("no such concept: {}".format(industry_name))
    store = HistoryStore(symbols)
    result = []
    for i in range(len(symbols)):
        symbol = symbols[i]
        related_symbols = symbols[i + 1:]
        high_corr_stocks = await get_high_corr_stocks(symbol, related_symbols, start_date, end_date, corr_min, store)
        for item in high_corr_stocks:
            result.append(CorrResult(symbol, item.symbol_y, item.corr))
    return GroupCorrResult(industry_name, result, GROUP_TYPE_INDUSTRY)


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


async def get_pairs(start_date, end_date, corr_min):
    df_concept = stock.utils.symbol_util.load_concept()
    df_concept = df_concept[~df_concept["concept_name"].isin(EXCLUDE_CONCEPTS)]
    grouped = df_concept.groupby("concept_name")
    print("===== concept =====")
    tasks = []
    for concept_name, group in grouped:
        if len(group) > 25:
            continue
        task = asyncio.create_task(get_high_corr_concept_pairs(concept_name, start_date, end_date, corr_min=corr_min))
        tasks.append(task)
    concept_results = await asyncio.gather(*tasks)
    df = pd.DataFrame(columns=["group", "symbol_x", "symbol_y", "corr"])
    for concept_result in concept_results:
        concept_name = concept_result.group_name
        corr_results = concept_result.corr_results
        for corr_res in corr_results:
            df = pd.concat([df, pd.DataFrame({
                "group": concept_name,
                "symbol_x": corr_res.symbol_x,
                "symbol_y": corr_res.symbol_y,
                "corr": corr_res.corr}, index=[len(df)])])

    df_industry = stock.utils.symbol_util.load_industry()
    grouped = df_industry.groupby("industry_name")
    print("===== industry =====")
    tasks = []
    for industry_name, group in grouped:
        if len(group) > 35:
            continue
        task = asyncio.create_task(get_high_corr_industry_pairs(industry_name, start_date, end_date, corr_min=corr_min))
        tasks.append(task)
    industry_results = await asyncio.gather(*tasks)
    for industry_result in industry_results:
        industry_name = industry_result.group_name
        corr_results = industry_result.corr_results
        for corr_res in corr_results:
            df = pd.concat([df, pd.DataFrame({
                "group": industry_name,
                "symbol_x": corr_res.symbol_x,
                "symbol_y": corr_res.symbol_y,
                "corr": corr_res.corr}, index=[len(df)])])

    # symbols = list(set(df["symbol_x"].tolist() + df["symbol_y"].tolist()))
    # store = HistoryStore(symbols)
    # format = "%Y-%m-%d"
    # end_dt = datetime.datetime.strptime(end_date, format)
    # start_dt = end_dt - datetime.timedelta(days=22)
    # start_date = start_dt.strftime(format)
    # tasks = [get_corr(row["symbol_x"], row["symbol_y"], start_date, end_date, store) for index, row in df.iterrows()]
    # concept_results = await asyncio.gather(*tasks)
    # df["corr_22"] = list(map(lambda x: x.corr, concept_results))
    # df = df[df["corr_22"] > corr_min]
    filepath = os.path.join(BASIC_DIR, "pairs")
    df.to_csv(filepath, index=False)


async def get_pairs_drift(end_date):
    filepath = os.path.join(BASIC_DIR, "pairs")
    df_pair = pd.read_csv(filepath, dtype={"symbol_x": np.string_, "symbol_y": np.string_})
    symbols = list(set(df_pair["symbol_x"].tolist() + df_pair["symbol_y"].tolist()))
    store = HistoryStore(symbols)
    format = "%Y-%m-%d"
    end_dt = datetime.datetime.strptime(end_date, format)
    start_dt = end_dt - datetime.timedelta(days=240)
    start_date = start_dt.strftime(format)
    print("group,symbol_x,symbol_y,corr,x-y,x-y2,x-y3,x-y mean,x-y std")
    for index, row in df_pair.iterrows():
        group = row["group"]
        symbol_x = row["symbol_x"]
        symbol_y = row["symbol_y"]
        corr = row["corr"]
        df_x = store.get_history(symbol_x, start_date, end_date)
        df_y = store.get_history(symbol_y, start_date, end_date)
        if end_date not in df_x.index or end_date not in df_y.index:
            continue
        result = pd.merge(df_x, df_y, how="outer", left_index=True, right_index=True, suffixes=("_x", "_y"))
        result["close_x"].fillna(method="ffill", inplace=True)
        result["close_y"].fillna(method="ffill", inplace=True)
        result["chg_x"] = result["close_x"]/result["close_x"].shift(1) - 1
        result["chg_x2"] = result["close_x"]/result["close_x"].shift(2) - 1
        result["chg_x3"] = result["close_x"]/result["close_x"].shift(3) - 1
        result["chg_y"] = result["close_y"]/result["close_y"].shift(1) - 1
        result["chg_y2"] = result["close_y"]/result["close_y"].shift(2) - 1
        result["chg_y3"] = result["close_y"]/result["close_y"].shift(3) - 1
        result["x-y"] = result["chg_x"] - result["chg_y"]
        result["x-y2"] = result["chg_x2"] - result["chg_y2"]
        result["x-y3"] = result["chg_x3"] - result["chg_y3"]
        mean = result["x-y"].mean()
        std = result["x-y"].std()
        std2 = result["x-y2"].std()
        std3 = result["x-y3"].std()
        s = result.loc[end_date]
        if (s["chg_x"] > 0.05 and (s["x-y"] > 3*std or s["x-y2"] > 3*std2 or s["x-y3"] > 3*std3)) or \
                (s["chg_y"] > 0.05 and (s["x-y"] < -3*std or s["x-y2"] < -3*std2 or s["x-y3"] < -3*std3)):
            print("{},{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.5f},{:.3f}".format(
                group, symbol_x, symbol_y, corr, s["x-y"], s["x-y2"], s["x-y3"], mean, std))



async def main():
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
    parser.add_argument("--pairs-drift", action="store_true", default=False, help="get pairs with drift")

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
        await get_similar_stocks_on_date(args.symbol, args.date, args.chg_min)
        sys.exit(0)
    if args.symbol:
        result = await get_similar_stocks_between_dates(args.symbol, start_date, end_date, args.corr_min)
        for group_result in result:
            group_result.print()
        sys.exit(0)
    if args.concept:
        group_result = await get_high_corr_concept_pairs(args.concept, start_date, end_date, args.corr_min)
        group_result.print()
        sys.exit(0)
    if args.industry:
        group_result = await get_high_corr_industry_pairs(args.industry, start_date, end_date, args.corr_min)
        group_result.print()
        sys.exit(0)
    if args.pairs:
        await get_pairs(start_date, end_date, args.corr_min)
        sys.exit(0)
    if args.pairs_drift:
        await get_pairs(start_date, end_date, args.corr_min)
        await get_pairs_drift(end_date)
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
