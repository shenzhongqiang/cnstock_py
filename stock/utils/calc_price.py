from stock.utils.symbol_util import symbol_to_exsymbol, is_symbol_kc, is_symbol_cy

def get_zt_price(symbol, price):
    exsymbol = symbol_to_exsymbol(symbol)
    if is_symbol_cy(exsymbol) or is_symbol_kc(exsymbol):
        zt_price = int(price * 1.2 * 100 + 0.50001) /100.0
    else:
        zt_price = int(price * 1.1 * 100 + 0.50001) /100.0
    return zt_price

def get_dt_price(symbol, price):
    exsymbol = symbol_to_exsymbol(symbol)
    if is_symbol_cy(exsymbol) or is_symbol_kc(exsymbol):
        dt_price = int(price * 0.8 * 100 + 0.50001) /100.0
    else:
        dt_price = int(price * 0.9 * 100 + 0.50001) /100.0
    return dt_price
