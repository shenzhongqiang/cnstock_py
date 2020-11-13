import time
import sys
import datetime
import shutil
import os
import py7zr
from ftplib import FTP
import numpy as np
import pandas as pd
from stock.globalvar import *
from stock.utils.symbol_util import symbol_to_exsymbol, is_symbol_kc

pd.set_option('max_columns', None)

def get_filepath(today):
    today_str = today.strftime("%Y%m%d")
    filename = "{}.7z".format(today_str)
    filepath = "/tmp/{}".format(filename)
    return filepath

def download_kaipan(today):
    ftp = FTP('218.244.131.134')
    result = ftp.login(user='szq_stkauction_tick', passwd='jinshuyuan.net78zxfi9')
    print(result)
    today_str = today.strftime("%Y%m%d")
    filename = "{}.7z".format(today_str)
    filepath = get_filepath(today)
    f = open(filepath, 'wb')
    cmd = 'RETR {}'.format(filename)
    ftp.retrbinary(cmd, f.write)
    ftp.quit()
    print("downloaded", filename)

def extract_archive(today):
    filepath = get_filepath(today)
    with py7zr.SevenZipFile(filepath, mode='r') as z:
        z.extractall(path='/tmp')
    today_str = today.strftime("%Y%m%d")
    source_dir = '/tmp/{}'.format(today_str)
    target_dir = KAIPAN_DIR['stock']
    for filename in os.listdir(target_dir):
        filepath = os.path.join(target_dir, filename)
        os.remove(filepath)

    filenames = os.listdir(source_dir)
    for filename in filenames:
        source_file = os.path.join(source_dir, filename)
        target_file = os.path.join(target_dir, filename)
        if os.path.isfile(target_file):
            continue
        shutil.move(source_file, target_dir)
    print("extracted all")

def filter_stocks(today):
    filenames = os.listdir(KAIPAN_DIR['stock'])
    critical_time = datetime.datetime(year=today.year, month=today.month, day=today.day,
        hour=9, minute=20, second=0)
    for filename in filenames:
        filepath = os.path.join(KAIPAN_DIR['stock'], filename)
        df = pd.read_csv(filepath, engine='c', dtype={
            'Stkcd': str,
            'TradingDay': str,
            'TimeStamp': str,
            'PreClosePrice': np.float64,
            'Volume': np.int64,
            'Amount': np.float64,
            'BidPrice1': np.float64,
            'BidQty1': np.int64,
            'BidQty2': np.int64,
            'AskPrice1': np.float64,
            'AskQty1': np.int64,
            'AskQty2': np.int64
        })
        df['incrperc'] = (df['BidPrice1'] / df['PreClosePrice'] - 1)
        df['time'] = df['TradingDay'] + ' ' + df['TimeStamp'].apply(lambda x: "{:0>6}".format(x))
        df['time'] = pd.to_datetime(df['time'], format='%Y%m%d %H%M%S')
        symbol = df.iloc[0]['Stkcd']
        exsymbol = symbol_to_exsymbol(symbol)
        if is_symbol_kc(exsymbol):
            continue
        df1 = df[df['time'] < critical_time]
        df2 = df[df['time'] >= critical_time]
        if df1.size == 0 or df2.size == 0:
            continue
        if df1['incrperc'].max() < 0.19:
            continue
        matched_qty1 = df1.iloc[-1]['BidQty1']
        matched_amount1 = int(df1.iloc[-1]['BidQty1'] * df1.iloc[-1]['BidPrice1'] * 100)
        unmatched_qty = df1.iloc[-1]['BidQty2'] - df1.iloc[-1]['AskQty2']
        matched_qty2 = df2.iloc[-1].Volume
        matched_amount2 = int(df2.iloc[-1].Amount)
        max_bid_id = df['BidQty1'].idxmax()
        max_bid_amount = int(df.iloc[max_bid_id]['BidQty1'] * df.iloc[max_bid_id]['BidPrice1'] * 100)
        print(symbol, max_bid_amount, matched_qty1, unmatched_qty, matched_amount1, matched_qty2, matched_amount2)

if __name__ == "__main__":
    today = None
    if len(sys.argv) == 1:
        today = datetime.date.today()
    else:
        today = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d")
    filepath = get_filepath(today)
    download_kaipan(today)
    extract_archive(today)
    filter_stocks(today)
