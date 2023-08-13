import re
import os
import sys
from multiprocessing import Pool
import numpy as np
import pandas as pd
from stock.globalvar import FINANCE_DIR
from stock.lib.finance import load_stock_basics


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


def get_growth(filename, qnum):
    stock_dir = FINANCE_DIR['stock']
    path = os.path.join(stock_dir, filename)
    exsymbol = get_exsymbol(filename)
    try:
        df = pd.read_csv(path, index_col="REPORT_DATE", parse_dates=True)
        netprofits = df.iloc[:qnum]["DEDUCT_PARENT_NETPROFIT_YOY"]
        incomes = df.iloc[:qnum]["TOTAL_OPERATE_INCOME_YOY"]
        return {
            "exsymbol": exsymbol,
            "netprofits": netprofits.tolist(),
            "incomes": incomes.tolist()
        }
    except Exception as e:
        return {"exsymbol": exsymbol,
            "netprofits": [],
            "incomes": []
        }


def gather_result(tasks):
    result = []
    for task in tasks:
        res = task.get()
        result.append(res)
    return result


def get_high_netprofit(today):
    stock_dir = FINANCE_DIR['stock']
    filenames = os.listdir(stock_dir)
    filenames = filter(lambda x: re.search(r'_lrb', x), filenames)
    p = Pool(10)
    tasks = []
    for filename in filenames:
        task = p.apply_async(get_growth, (filename, 4))
        tasks.append(task)
    result = gather_result(tasks)

    df_basics = load_stock_basics()
    for item in result:
        exsymbol = item["exsymbol"]
        netprofits = item["netprofits"]
        incomes = item["incomes"]
        if re.match(r'bj', exsymbol) or \
            len(netprofits) < 4 or \
            exsymbol not in df_basics.index:
            continue
        avg_netprofit = np.mean(netprofits)
        pe = df_basics.loc[exsymbol, "pe"]
        name = df_basics.loc[exsymbol, "name"]
        high_growth = all([netprofit > 20 for netprofit in netprofits]) and \
            all([income > 20 for income in incomes]) and \
            pe > 0 and pe < 30
        if high_growth:
            print(exsymbol, name, pe)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    today = None
    if len(sys.argv) == 1:
        today = pd.datetime.today()
    else:
        today = pd.datetime.strptime(sys.argv[1], "%Y-%m-%d")
    get_high_netprofit(today)
