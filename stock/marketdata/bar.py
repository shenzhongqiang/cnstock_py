import datetime

class Bar:
    def __init__(self, exsymbol, date, dt=None, cnname=None, \
        close=None, lclose=None, open=None, volume=None, \
        chg=None, chgperc=None, high=None, low=None, \
        amount=None, pe=None, ampl=None):
        self.cnname = cnname
        self.exsymbol = exsymbol
        self.symbol = exsymbol[2:]
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
        if dt == None:
            self.dt = datetime.datetime.strptime(date, "%y%m%d")
        else:
            self.dt =dt
