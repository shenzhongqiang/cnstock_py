# -*- coding: UTF-8 -*-
import os
import numpy as np
import pandas as pd
from stock.globalvar import FINANCE_DIR, BASIC_DIR, LRB_CH2EN, XJLLB_CH2EN, ZCFZB_CH2EN
from stock.utils.symbol_util import symbol_to_exsymbol

def _set_quarter(df):
    for i in range(len(df)):
        dt = df.index[i]
        if dt.month == 3:
            df.loc[df.index[i], "quarter"] = "Q1"
        elif dt.month == 6:
            df.loc[df.index[i], "quarter"] = "Q2"
        elif dt.month == 9:
            df.loc[df.index[i], "quarter"] = "Q3"
        elif dt.month == 12:
            df.loc[df.index[i], "quarter"] = "Q4"

def _parse_cell(string, parser=None):
    string = string.strip()
    if string == "":
        return np.nan
    if string == "--":
        return np.nan
    if parser == None:
        return string
    return parser(string)

def get_lrb_data(exsymbol):
    filename = "%s_lrb" % exsymbol
    path = os.path.join(FINANCE_DIR["stock"], filename)
    if not os.path.isfile(path):
        msg = "%s has no lrb data" % exsymbol
        raise Exception(msg)
    content = None
    with open(path, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data = {}
    index = []
    for line in lines:
        if line.strip() == "":
            continue
        cells = line.split(",")
        col = cells[0].strip()
        if col == "报告日期":
            index = map(lambda x: _parse_cell(x, str), cells[1:])
        else:
            en = LRB_CH2EN.get(col)
            if en == "":
                raise Exception("en for %s not defined" % cells[0])
            array = data.setdefault(en, [])
            parsed = map(lambda x: _parse_cell(x, float), cells[1:])
            array.extend(parsed)

    df = pd.DataFrame(data=data, index=index).fillna(0.0)
    df = df[pd.notnull(df.index)]
    df.set_index(pd.to_datetime(df.index, format="%Y-%m-%d"), inplace=True)
    _set_quarter(df)
    return df.iloc[::-1]

def get_zcfzb_data(exsymbol):
    filename = "%s_zcfzb" % exsymbol
    path = os.path.join(FINANCE_DIR["stock"], filename)
    if not os.path.isfile(path):
        msg = "%s has no zcfzb data" % exsymbol
        raise Exception(msg)
    content = None
    with open(path, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data = {}
    index = []
    for line in lines:
        if line.strip() == "":
            continue
        cells = line.split(",")
        col = cells[0].strip()
        if col == "报告日期":
            index = map(lambda x: _parse_cell(x, str), cells[1:])
        else:
            en = ZCFZB_CH2EN.get(col)
            if not en:
                raise Exception("en for %s not defined" % cells[0])
            array = data.setdefault(en, [])
            parsed = map(lambda x: _parse_cell(x, float), cells[1:])
            array.extend(parsed)

    df = pd.DataFrame(data=data, index=index).fillna(0.0)
    df = df[pd.notnull(df.index)]
    df.set_index(pd.to_datetime(df.index, format="%Y-%m-%d"), inplace=True)
    _set_quarter(df)
    return df.iloc[::-1]

def get_xjllb_data(exsymbol):
    filename = "%s_xjllb" % exsymbol
    path = os.path.join(FINANCE_DIR["stock"], filename)
    if not os.path.isfile(path):
        msg = "%s has no xjllb data" % exsymbol
        raise Exception(msg)
    content = None
    with open(path, "r") as f:
        content = f.read()
    lines = content.splitlines()
    data = {}
    index = []
    for line in lines:
        if line.strip() == "":
            continue
        cells = line.split(",")
        col = cells[0].strip()
        if col == "报告日期":
            index = map(lambda x: _parse_cell(x, str), cells[1:])
        else:
            en = XJLLB_CH2EN.get(col.strip())
            if not en:
                raise Exception("en for %s not defined" % cells[0])
            array = data.setdefault(en, [])
            parsed = map(lambda x: _parse_cell(x, float), cells[1:])
            array.extend(parsed)

    df = pd.DataFrame(data=data, index=index).fillna(0.0)
    df = df[pd.notnull(df.index)]
    df.set_index(pd.to_datetime(df.index, format="%Y-%m-%d"), inplace=True)
    _set_quarter(df)
    return df.iloc[::-1]

def load_stock_basics():
    filepath = os.path.join(BASIC_DIR, "basics")
    df = pd.read_csv(filepath, encoding="utf-8", dtype={"code": str, "pe": np.float64})
    df["exsymbol"] = list(map(lambda x: symbol_to_exsymbol(x), df["code"]))
    df.set_index("exsymbol", inplace=True)
    return df
