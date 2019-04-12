import datetime
import os
import os.path
import re
import json
from stock.utils import request
from stock.globalvar import *
from stock.marketdata.utils import load_csv
import tushare as ts
import pandas as pd

class InvalidType(Exception):
    pass

class NoRealtimeData(Exception):
    pass

class NoTickData(Exception):
    pass

def get_stock_symbols():
    df = pd.read_csv(SYM["all"], dtype=str)
    return df.code.tolist()

def get_index_symbols():
    df = pd.read_csv(SYM["id"], dtype=str)
    return df.code.tolist()

def get_index_symbol(type):
    return INDEX[type]

def get_archived_trading_dates(start, end):
    index_path = os.path.join(HIST_DIR["index"], "000001")
    df = load_csv(index_path)
    dates = df.date.tolist()
    dts = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), dates)
    result = []
    start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    for dt in dts:
        if dt >= start_dt and dt <= end_dt:
            result.append(dt)

    return map(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d"), result)

def get_st(exsymbols):
    exsymbol_str = ",".join(exsymbols)
    url = "http://push2.gtimg.cn/q=%s" % (exsymbol_str)
    result = request.send_request(url)
    lines = result.split("\n")
    st = {}
    for line in lines:
        if line == "":
            continue
        cnname = line.split('~')[1]
        exsymbol = line.split('=')[0][2:]
        match = re.search(r"ST", cnname)
        if match:
            st[exsymbol] = True
        else:
            st[exsymbol] = False
    return st

def download_symbols():
    df = ts.get_stock_basics()
    df.to_csv(SYM["all"])
    index_df = ts.get_index()
    index_df.to_csv(SYM["id"])

def is_symbol_cy(symbol):
    patt = re.compile('^sz3')
    if patt.search(symbol) and symbol != INDEX['cy']:
        return True
    else:
        return False

def is_symbol_sh(symbol):
    patt = re.compile('^sh')
    if patt.search(symbol) and symbol != INDEX['sh']:
        return True
    else:
        return False

def is_symbol_sz(symbol):
    patt = re.compile('^sz0')
    if patt.search(symbol) and symbol != INDEX['sz']:
        return True
    else:
        return False

def symbol_to_exsymbol(symbol, index=False):
    exsymbol = ''
    if index == False:
        if re.search(r'^6', symbol):
            exsymbol = 'sh' + symbol
        elif re.search(r'^3', symbol):
            exsymbol = 'sz' + symbol
        elif re.search(r'^0', symbol):
            exsymbol = 'sz' + symbol
    else:
        exsymbol = 'id' + symbol
    return exsymbol

def exsymbol_to_symbol(exsymbol):
    return exsymbol[2:]

def get_today_all():
    folder = REAL_DIR["stock"]
    files = os.listdir(folder)
    symbols = get_stock_symbols()
    exsymbols = list(map(lambda x: symbol_to_exsymbol(x), symbols))
    df = pd.DataFrame(columns=["close", "open", "high", "low", "volume",
        "chgperc", "yest_close", "amount",
        "b1_v", "b1_p", "a1_v", "a1_p",
        "pe", "pb", "lt_mcap", "mcap"], index=exsymbols)
    for filename in files:
        exsymbol = filename
        filepath = os.path.join(folder, filename)
        with open(filepath, "r") as f:
            content = f.read()
            m = re.match(r"v_(.*?)=", content)
            if m == None:
                raise Exception("cannot extract exsymbol from %s" \
                    % (content))
            result = re.sub("^v_.*?=\"|\";$", "", content)
            data = result.split("~")
            if len(data) < 47:
                continue
            df.at[exsymbol, "pe"] = 0 if data[39] == '' else float(data[39])
            df.at[exsymbol, "pb"] = 0 if data[46] == '' else float(data[46])
            df.at[exsymbol, "close"] = float(data[3])
            df.at[exsymbol, "yest_close"] = float(data[4])
            df.at[exsymbol, "open"] = float(data[5])
            df.at[exsymbol, "volume"] = float(data[6])
            chg = float(data[31])
            df.at[exsymbol, "chgperc"] = float(data[32])
            df.at[exsymbol, "high"] = float(data[33])
            df.at[exsymbol, "low"] = float(data[34])
            df.at[exsymbol, "amount"] = float(data[37])
            df.at[exsymbol, "b1_v"] = float(data[10])
            df.at[exsymbol, "b1_p"] = float(data[11])
            df.at[exsymbol, "a1_p"] = float(data[19])
            df.at[exsymbol, "a1_v"] = float(data[20])
            df.at[exsymbol, "lt_mcap"] = 0 if data[44] == '' else float(data[44])
            df.at[exsymbol, "mcap"] = 0 if data[45] == '' else float(data[45])
    return df[df.lt_mcap > 0]

def get_realtime_date():
    folder = REAL_DIR["stock"]
    filepath = os.path.join(folder, "sz399001")
    with open(filepath, "r") as f:
        content = f.read()
        m = re.match(r"v_(.*?)=", content)
        result = re.sub("^v_.*?=\"|\";$", "", content)
        data = result.split("~")
        datetime_str = data[30]
        dt = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
        date_str = dt.strftime("%Y-%m-%d")
        return date_str

def get_realtime_by_date(date_str):
    folder = REAL_DIR["daily"]
    filepath = os.path.join(folder, date_str + ".csv")
    if not os.path.isfile(filepath):
        raise NoRealtimeData("no such file: %s" % filepath)
    df = pd.read_csv(filepath, index_col=0)
    return df

def get_zhangting_minutes(df_tick):
    high = df_tick.price.max()
    df_tick.loc[:, "last_price"] = df_tick.price.shift(1)
    df_tick.loc[:, "last_time"] = df_tick["time"].shift(1)
    time_diff = df_tick.time.values - df_tick.last_time.values
    df_tick.loc[:, "time_diff"] = time_diff
    zhangting_time = df_tick[(df_tick.price==high) & (df_tick.last_price==high)].time_diff.sum()
    zhangting_min = zhangting_time / datetime.timedelta(minutes=1)
    return zhangting_min

def get_kaipan(exsymbol, s_rt):
    folder = TICK_DIR["stock"]
    filepath = os.path.join(folder, exsymbol)
    if not os.path.isfile(filepath):
        raise NoTickData("no such file: %s" % filepath)
    df = pd.read_csv(filepath, sep='\t', header=0, names=['time', 'price', 'change', 'volume', 'amount', 'type'])
    df.loc[:, "time"] = pd.to_datetime(df["time"])
    df.index = df["time"]
    s_null = pd.Series(data={'price': 0, 'change': 0, 'volume': 0, 'amount': 0, 'type': None, 'sell_amount': 0, 'zhangting_min': 0}, name=None)
    if len(df) == 0:
        return (exsymbol, s_null)

    s = df.iloc[0]
    s_kaipan = None
    if s_rt["chgperc"] < 9.9:
        s_kaipan = pd.Series(data={'price': s.price, 'change': s.change, 'volume': s.volume, 'amount': s.amount, 'type': s.type, 'sell_amount': 0, 'zhangting_min': 0}, name=s.name)
    else:
        high = df.price.max()
        sell_amount = df[df.price==high].volume.sum() * high / 1e6
        df_tick1 = df[df.time<="11:30:00"].copy()
        df_tick2 = df[df.time>="13:00:00"].copy()
        zhangting1_min = get_zhangting_minutes(df_tick1)
        zhangting2_min = get_zhangting_minutes(df_tick2)
        zhangting_min = zhangting1_min + zhangting2_min
        s_kaipan = pd.Series(data={'price': s.price, 'change': s.change, 'volume': s.volume, 'amount': s.amount, 'type': s.type, 'sell_amount': sell_amount, 'zhangting_min': zhangting_min}, name=s.name)
    return (exsymbol, s_kaipan)

def get_tick_by_date(date_str):
    folder = TICK_DIR["daily"]
    filepath = os.path.join(folder, date_str + ".csv")
    if not os.path.isfile(filepath):
        raise NoTickData("no such file: %s" % filepath)
    df = pd.read_csv(filepath, index_col=0)
    return df
