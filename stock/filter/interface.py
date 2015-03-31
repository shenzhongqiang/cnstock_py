from abc import *
import stock.marketdata

class Filter:
    __metaclass__ = ABCMeta

    def __init__(self, marketdata, output, params=None):
        self.marketdata = marketdata
        self.output = output
        self.params = params

    @abstractmethod
    def check(self, exsymbol):
        pass

class CheckResult:
    def __init__(self, exsymbol, chgperc=None, cnname=None, \
        pe=None, cvalue=None, value=None, bar_today=None):
        self.exsymbol = exsymbol
        self.chgperc = chgperc
        self.symbol = exsymbol[2:]
        self.cnname = cnname
        self.pe = pe
        self.cvalue = cvalue
        self.value = value
        self.bar_today = bar_today
