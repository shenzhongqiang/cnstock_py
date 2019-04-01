import sys
import tushare as ts
from stock.utils.symbol_util import exsymbol_to_symbol
from stock.marketdata.storefactory import get_store
from config import store_type
import pandas as pd

def get_tick_history(exsymbol, days=10):
    store = get_store(store_type)
    dates = store.get('id000001').index
    symbol = exsymbol_to_symbol(exsymbol)
    df_res = pd.DataFrame(columns=["kaipan_vol", "kaipan_money", "shoupan_vol", "shoupan_money"])
    for i in range(days, 0, -1):
        date = dates[len(dates)-i].strftime("%Y-%m-%d")
        df = ts.get_tick_data(symbol, date=date, src="tt")
        if df is None or len(df) == 0:
            continue
        df["time"] = pd.to_datetime(df["time"], format='%H:%M:%S')
        kaipan_time = df.iloc[0].time
        kaipan_vol = 0
        kaipan_money = 0
        if kaipan_time.hour == 9 and kaipan_time.minute < 30:
            kaipan_vol = df.iloc[0].volume
            kaipan_money = df.iloc[0].amount
        shoupan_time = df.iloc[len(df)-1].time
        shoupan_vol = 0
        shoupan_money = 0
        if shoupan_time.hour >= 15 and shoupan_time.minute >= 0:
            shoupan_vol = df.iloc[len(df)-1].volume
            shoupan_money = df.iloc[len(df)-1].amount
        df_res.loc[date] = [kaipan_vol, kaipan_money, shoupan_vol, shoupan_money]
    return df_res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <exsymbol>" % sys.argv[0])
        sys.exit(1)

    exsymbol = sys.argv[1]
    df = get_tick_history(exsymbol, days=30)
    print(df)
