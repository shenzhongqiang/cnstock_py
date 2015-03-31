from stock.utils.dt import *

class Bar:
    def __init__(self, exsymbol, date, dt=None, cnname=None, \
        close=None, lclose=None, open=None, volume=None, \
        chg=None, chgperc=None, high=None, low=None, \
        amount=None, pe=None, ampl=None, cvalue=None, \
        value=None):
        self.exsymbol = exsymbol
        self.symbol = exsymbol[2:]
        self.date = date
        if dt == None:
            self.dt = parse_datetime(date)
        else:
            self.dt =dt
        self.cnname = cnname
        self.close = close
        self.lclose = lclose
        self.open = open
        self.volume = volume
        self.chg = chg
        self.chgperc = chgperc
        self.high = high
        self.low = low
        self.amount = amount
        self.pe = pe
        self.ampl = ampl
        self.cvalue = cvalue
        self.value = value

    def __repr__(self):
        return "<stock.marketdata.bar.Bar: %s %f>" % (self.date, self.close)
