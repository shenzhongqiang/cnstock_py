import re
import os
import sys
import pandas as pd
from stock.globalvar import FINANCE_DIR


def get_exsymbol(filename):
    m = re.search(r'(.*)_lrb', filename)
    if m:
        return m.group(1)
    m = re.search(r'(.*)_xjllb', filename)
    if m:
        return m.group(1)
    m = re.search(r'(.*)_zcfzb', filename)
    if m:
        return m.group(1)
    raise Exception("cannot get symbol from filename ", filename)

def get_high_netprofit(today):
    stock_dir = FINANCE_DIR['stock']
    filenames = os.listdir(stock_dir)
    filenames = filter(lambda x: re.search(r'_lrb', x), filenames)
    for filename in filenames:
        exsymbol = get_exsymbol(filename)
        path = os.path.join(stock_dir, filename)
        df = pd.read_csv(path, index_col="REPORT_DATE", parse_dates=True)
        df["report_q"] = df.index.quarter
        if len(df) < 4:
            continue
        is_growing = df.iloc[3]["DEDUCT_PARENT_NETPROFIT_YOY"] > 20 and df.iloc[2]["DEDUCT_PARENT_NETPROFIT_YOY"] > 20 and \
            df.iloc[1]["DEDUCT_PARENT_NETPROFIT_YOY"] > 20 and df.iloc[0]["DEDUCT_PARENT_NETPROFIT_YOY"] > 20
        if is_growing:
            print(exsymbol)

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")
    get_high_netprofit(today)