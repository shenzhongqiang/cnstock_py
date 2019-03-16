import datetime
import os
import os.path
import asyncio
import aiohttp
from stock.utils import request
import stock.utils.symbol_util
from stock.marketdata.storefactory import get_store
from config import store_type
from stock.globalvar import *
from tqdm import tqdm, trange

def init():
    # check if directory exists, if not create directory
    for k,v in REAL_DIR.items():
        if not os.path.isdir(v):
            os.makedirs(v)
    files = os.listdir(REAL_DIR["stock"])
    for filename in files:
        filepath = os.path.join(REAL_DIR["stock"], filename)
        os.remove(filepath)

async def download_realtime(exsymbol, session):
        url = "http://qt.gtimg.cn/q=" + exsymbol
        filepath = os.path.join(REAL_DIR['stock'], exsymbol)
        async with session.get(url) as response:
            resp = await response.text()
            with open(filepath, "w") as f:
                f.write(resp)

async def run():
    symbols = stock.utils.symbol_util.get_stock_symbols()
    index_symbols = stock.utils.symbol_util.get_index_symbols()
    symbols.extend(index_symbols)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            exsymbol = stock.utils.symbol_util.symbol_to_exsymbol(symbol)
            task = asyncio.create_task(download_realtime(exsymbol, session))
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    init()
    print("init complete")
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)
    print("download complete")

    df = stock.utils.symbol_util.get_today_all()
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    filename = "%s.csv" % today
    filepath = os.path.join(REAL_DIR["daily"], filename)
    df.to_csv(filepath)
    print("save complete")
