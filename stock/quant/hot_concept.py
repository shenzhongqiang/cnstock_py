import sys
from stock.marketdata.storefactory import get_store
from stock.utils.symbol_util import load_concept, get_realtime_by_date
import numpy as np
import pandas as pd

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
    df_res = df_concept.merge(df_stock, how="left", left_on="exsymbol", right_index=True)
    df_chg = df_res.groupby("concept")["chg"].agg(["mean", "count"]).rename(columns={"mean": "avg_chg", "count": "num_stock"}).sort_values("avg_chg")
    print(df_chg[df_chg.num_stock>5].tail(10))

    df_zt = df_res.groupby("concept")["is_zhangting"].agg(["sum"]).rename(columns={"sum": "num_zhangting"})
    df_hot = df_zt[df_zt.num_zhangting>=3]
    df_hot_stocks = df_res[df_res.concept.isin(df_hot.index) & df_res.is_zhangting==True]
    columns = ["concept", "exsymbol", "chg"]
    print(df_hot_stocks[columns])
