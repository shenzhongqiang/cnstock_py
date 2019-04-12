import sys
import datetime
import re
import os.path
import asyncio
import aiohttp
import stock.utils.symbol_util
from stock.globalvar import TICK_DIR, REAL_DIR
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd
import concurrent.futures

def init():
    for k, v in TICK_DIR.items():
        if not os.path.isdir(v):
            os.makedirs(v)
    files = os.listdir(TICK_DIR["stock"])
    for filename in files:
        filepath = os.path.join(TICK_DIR["stock"], filename)
        os.remove(filepath)

async def download_tick(exsymbol, date, session):
    if re.match(r"\d{4}-\d{2}-\d{2}", date):
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        date = dt.strftime("%Y%m%d")
    url = "http://stock.gtimg.cn/data/index.php?appn=detail&action=download&c={}&d={}".format(exsymbol, date)
    filepath = os.path.join(TICK_DIR['stock'], exsymbol)
    async with session.get(url) as response:
        resp = await response.text(encoding="GBK")
        with open(filepath, "w") as f:
            f.write(resp)

async def run(date):
    symbols = stock.utils.symbol_util.get_stock_symbols()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
            task = asyncio.create_task(download_tick(exsymbol, date, session))
            tasks.append(task)

        await asyncio.gather(*tasks)

def save_kaipan_from_realtime():
    df = stock.utils.symbol_util.get_today_all()
    df.loc[:, "b1_money"] = df.close * df.b1_v * 100
    df.loc[:, "kaipan_money"] = df.apply(lambda x: x.amount*1e4 if x.amount > 0 else x.b1_money, axis=1)
    df_res = pd.DataFrame(data={"kaipan_price": df.close, "kaipan_money": df.kaipan_money})
    return df_res

async def save_kaipan_from_tick(loop, date):
    folder = TICK_DIR["stock"]
    files = os.listdir(folder)
    df = pd.DataFrame(columns=["kaipan_price", "kaipan_money", "sell_amount", "zhangting_min"])
    tasks = []
    df_rt = stock.utils.symbol_util.get_realtime_by_date(date)
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as pool:
        for filename in files:
            exsymbol = filename
            if exsymbol not in df_rt.index:
                continue
            s_rt = df_rt.loc[exsymbol]
            task = loop.run_in_executor(pool, stock.utils.symbol_util.get_kaipan, exsymbol, s_rt)
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        for (exsymbol, s) in result:
            df.at[exsymbol] = [s.price, s.amount, s.sell_amount, s.zhangting_min]
    outfile = "%s.csv" % date
    outpath = os.path.join(TICK_DIR["daily"], outfile)
    df.to_csv(outpath)


def main(date):
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    # if date is not today, download tick data and get kaipan from tick
    if today == date and now.hour <= 9 and now.minute < 30:
        # if date is today and before 9:30, get kaipan from realtime
        df = save_kaipan_from_realtime()
        filename = "%s.csv" % today
        filepath = os.path.join(TICK_DIR["daily"], filename)
        df.to_csv(filepath)
        print("tick: agg complete")
    else:
        init()
        print("tick: init complete")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(run(date))
        loop.run_until_complete(future)
        print("tick: download complete")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(save_kaipan_from_tick(loop, date))
        loop.run_until_complete(future)
        print("tick: agg complete")

if __name__ == "__main__":
    date = None
    if len(sys.argv) < 2:
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
    else:
        date = sys.argv[1]
    main(date)
