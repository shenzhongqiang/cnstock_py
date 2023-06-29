import datetime
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


EXCLUDE_CONCEPTS = ["融资融券", "机构重仓", "富时罗素", "MSCI中国", "标准普尔", "沪股通", "HS300_", "上证180_", "上证50_",
                "证金持股", "央视50_", "深证100R", "中证500", "ST股", "深成500", "上证380", "深股通", "创业成份",
                "QFII重仓", "转债标的", "基金重仓", "创业板综", "昨日连板_含一字", "AH股", "GDR", "中字头", "茅指数",
                "B股", "IPO受益", "举牌", "低价股", "养老金", "昨日涨停", "昨日涨停_含一字", "昨日触板", "昨日连板",
                "贬值受益", "预盈预增", "预亏预减", "高送转", "百元股", "社保重仓", "参股新三板", "内贸流通", "股权激励",
                "AB股", "独角兽", "壳资源", "分拆预期", "债转股", "送转预期", "科创板做市股"]


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


def get_snapshot_from_history(date):
    store = get_store(store_type)
    rows = []
    symbols = stock.utils.symbol_util.get_stock_symbols()
    for symbol in symbols:
        if not store.has(symbol):
            continue

        df_stock = store.get(symbol)
        df_past = df_stock.loc[:date].copy()
        if len(df_past) < 2:
            continue
        if df_past.iloc[-1].date != date:
            continue
        row = {"symbol": symbol,
            "open": df_past.iloc[-1]["open"],
            "close": df_past.iloc[-1]["close"],
            "high": df_past.iloc[-1]["high"],
            "low": df_past.iloc[-1]["low"],
            "volume": df_past.iloc[-1]["volume"],
            "yest_close": df_past.iloc[-2]["close"],
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.set_index("symbol", inplace=True)
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
    yest = stock.utils.symbol_util.get_last_trading_date(today)
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


def get_chuban(today):
    today_str = today.strftime("%Y-%m-%d")
    df = get_snapshot_from_history(today_str)
    df["zt_price"] = df.apply(lambda x: get_zt_price(x.name[2:], x["yest_close"]), axis=1)
    df.loc[:, "is_chuban"] = np.absolute(df["zt_price"]-df["high"])<1e-8
    df.loc[:, "chg"] = df["close"]/df["yest_close"] - 1
    df_res = df[(df.is_chuban==True) & (df.close < df.high) & (df.close > 2)]
    columns = ["close", "yest_close", "zt_price"]
    print("========================== chuban ==========================")
    print(df_res[columns])

    df.loc[:, "hi_chg"] = df["high"]/df["yest_close"] - 1
    df_rise = df[(df.hi_chg > 0.05) & (df.close > df.open) & (df.close < df.zt_price)]
    columns = ["close", "yest_close", "hi_chg"]
    print("========================== rise ==========================")
    print(df_rise[columns])


def get_group_snapshot_from_history(date):
    df_concept = stock.utils.symbol_util.load_concept()
    df_concept = df_concept[~df_concept["concept_name"].isin(EXCLUDE_CONCEPTS)]
    df_industry = stock.utils.symbol_util.load_industry()
    symbols = df_concept["concept_symbol"].unique().tolist() + \
        df_industry["industry_symbol"].unique().tolist()
    symbols = list(set(symbols))

    rows = []
    for symbol in symbols:
        filepath = os.path.join(HIST_DIR["group"], symbol)
        df_group = pd.read_csv(filepath)
        index = pd.to_datetime(df_group.date, format="%Y-%m-%d")
        df_group.set_index(index, inplace=True)
        df_past = df_group.loc[:date].copy()
        if len(df_past) < 5:
            continue
        row = {"symbol": symbol,
            "day1_vol": df_past.iloc[-5].volume,
            "day2_vol": df_past.iloc[-4].volume,
            "day3_vol": df_past.iloc[-3].volume,
            "day4_vol": df_past.iloc[-2].volume,
            "day5_vol": df_past.iloc[-1].volume,
            "5day_low": df_past.iloc[-5:].low.min(),
            "open": df_past.iloc[-1].open,
            "close": df_past.iloc[-1].close,
        }

        rows.append(row)
    df = pd.DataFrame(rows)
    df.set_index("symbol", inplace=True)
    return df


def get_group(today):
    today_str = today.strftime("%Y-%m-%d")
    df = get_group_snapshot_from_history(today_str)
    df["avg_vol"] = (df["day1_vol"]+df["day2_vol"]+df["day3_vol"]+df["day4_vol"]) / 4
    df["vol_incr"] = df["day5_vol"]/df["avg_vol"] - 1
    df["dvol"] = df["day5_vol"]/df["day4_vol"] - 1
    df["yest_dvol"] = df["day4_vol"]/df["day3_vol"] - 1
    df["price_incr"] = df["close"]/df["5day_low"] - 1
    df["d2vol"] = df["dvol"] - df["yest_dvol"]
    df_res = df[(df["vol_incr"] > 0.3) & (df["d2vol"] > 0.2) & (df["price_incr"] < 0.07) & (df["close"] > df["open"])]

    df_concept = stock.utils.symbol_util.load_concept()[["concept_symbol", "concept_name"]].drop_duplicates()
    df_concept.rename(columns={"concept_symbol": "symbol", "concept_name": "name"}, inplace=True)
    df_industry = stock.utils.symbol_util.load_industry()[["industry_symbol", "industry_name"]].drop_duplicates()
    df_industry.rename(columns={"industry_symbol": "symbol", "industry_name": "name"}, inplace=True)
    df_group = pd.concat([df_concept, df_industry]).set_index("symbol")
    df_res = df_res.merge(df_group, left_index=True, right_index=True)
    columns = ["vol_incr", "d2vol", "price_incr", "name"]
    print(df_res[columns].sort_values("vol_incr", ascending=False))


def get_top_bottom_stocks_group(today):
    today_str = today.strftime("%Y-%m-%d")
    df = get_snapshot_from_history(today_str)
    df["chg"] = df["close"]/df["yest_close"] - 1
    df_top = df[df["chg"] > 0.08]
    df_bottom = df[df["chg"] < -0.08]
    df_concept = stock.utils.symbol_util.load_concept()
    df_concept = df_concept[~df_concept["concept_name"].isin(EXCLUDE_CONCEPTS)]
    df_industry = stock.utils.symbol_util.load_industry()
    df_top_concept = df_top.merge(df_concept, left_index=True, right_on="symbol")[["concept_name", "symbol"]].groupby("concept_name").count().sort_values("symbol", ascending=False)
    df_top_industry = df_top.merge(df_industry, left_index=True, right_on="symbol")[["industry_name", "symbol"]].groupby("industry_name").count().sort_values("symbol", ascending=False)
    df_bottom_concept = df_bottom.merge(df_concept, left_index=True, right_on="symbol")[["concept_name", "symbol"]].groupby("concept_name").count().sort_values("symbol", ascending=False)
    df_bottom_industry = df_bottom.merge(df_industry, left_index=True, right_on="symbol")[["industry_name", "symbol"]].groupby("industry_name").count().sort_values("symbol", ascending=False)

    print("========================== top concept ==========================")
    print(df_top_concept[df_top_concept["symbol"]>1])
    print("========================== top industry ==========================")
    print(df_top_industry[df_top_industry["symbol"]>1])
    print("========================== bottom concept ==========================")
    print(df_bottom_concept[df_bottom_concept["symbol"]>1])
    print("========================== bottom industry ==========================")
    print(df_bottom_industry[df_bottom_industry["symbol"]>1])


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")

    get_top_bottom_stocks_group(today)
    get_group(today)
    #get_chuban(today)
    #get_zhangting(today)
    #get_duanban(today)

