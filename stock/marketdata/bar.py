import datetime

class Bar:
    def __init__(self, exsymbol, symbol, date, cnname=None, \
        close=None, lclose=None, open=None, volume=None, \
        chg=None, chgperc=None, high=None, low=None, \
        amount=None, pe=None, ampl=None):
        self.cnname = cnname
        self.exsymbol = exsymbol
        self.symbol = symbol
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
        self.date = date
        self.dt = datetime.strptime(date, "%y%m%d")
