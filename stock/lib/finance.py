# -*- coding: UTF-8 -*-
import os
import numpy as np
import pandas as pd
from stock.globalvar import FINANCE_DIR, LRB_CH2EN, XJLLB_CH2EN, ZCFZB_CH2EN


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
    content = None
    with open(path, "rb") as f:
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
    return df.iloc[::-1]

def get_zcfzb_data(exsymbol):
    filename = "%s_zcfzb" % exsymbol
    path = os.path.join(FINANCE_DIR["stock"], filename)
    content = None
    with open(path, "rb") as f:
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
    return df.iloc[::-1]

def get_xjllb_data(exsymbol):
    filename = "%s_xjllb" % exsymbol
    path = os.path.join(FINANCE_DIR["stock"], filename)
    content = None
    with open(path, "rb") as f:
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
    return df.iloc[::-1]
