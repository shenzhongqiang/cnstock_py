import sys
from stock.utils.symbol_util import exsymbol_to_symbol, get_stock_symbols, get_kaipan, get_realtime_by_date
from stock.marketdata.storefactory import get_store
from stock.lib.finance import load_stock_basics
from config import store_type
import pandas as pd


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <date>" % sys.argv[0])
        sys.exit(1)

    date = sys.argv[1]
    store = get_store(store_type)
    dates = store.get('id000001').index
    idx = dates.get_loc(date)
    exsymbols = store.get_stock_exsymbols()
    df_res = pd.DataFrame(columns=["kaipan_vol", "opengap", "vol_ratio", "lt_mcap", "kaipan_money"])
    df_basics = load_stock_basics()
    df_basics = df_basics.loc[df_basics.outstanding>0]
    date_yest = dates[idx-1].strftime("%Y-%m-%d")
    df_realtime = get_realtime_by_date(date_yest)
    for exsymbol in exsymbols:
        if exsymbol not in df_realtime.index:
            continue
        exsymbol_row = df_realtime.loc[exsymbol]
        chgperc = exsymbol_row.chgperc
        if chgperc <= 9.5:
            continue
        try:
            outstanding = df_basics.loc[exsymbol, "outstanding"]
            if outstanding == 0:
                continue
            s = get_kaipan(exsymbol)
            opengap = s.price/exsymbol_row.close-1
            lt_mcap = outstanding*s.price
            ratio = s.volume / outstanding / 1e6
            df_res.loc[exsymbol] = [s.volume, opengap, ratio, lt_mcap, s.amount]
        except Exception as e:
            continue
    print(df_res.sort_values("kaipan_money", ascending=True))
