# float number 0.5 is represented as 0.4999999999998 in python
def get_zt_price(price):
    zt_price = int(price * 1.1 * 100 + 0.50001) /100.0
    return zt_price

def get_dt_price(price):
    zt_price = int(price * 0.9 * 100 + 0.50001) /100.0
    return zt_price
