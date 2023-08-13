import re
import os
import sys
import asyncio
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


async def get_growth(filename, qnum):
    stock_dir = FINANCE_DIR['stock']
    path = os.path.join(stock_dir, filename)
    df = pd.read_csv(path, index_col="REPORT_DATE", parse_dates=True)

    chgs = df.iloc[:qnum]["DEDUCT_PARENT_NETPROFIT_YOY"]

    exsymbol = get_exsymbol(filename)
    return [exsymbol, chgs.tolist()]


async def get_high_netprofit(today):
    stock_dir = FINANCE_DIR['stock']
    filenames = os.listdir(stock_dir)
    filenames = filter(lambda x: re.search(r'_lrb', x), filenames)
    tasks = [get_growth(filename, 4) for filename in filenames]
    result = await asyncio.gather(*tasks)
    print(result)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")
    asyncio.run(get_high_netprofit(today))
