import datetime
import re
import os.path
from stock.utils.request import *
from stock.utils.fuquan import *
from stock.globalvar import *
from stock.marketdata.bar import Bar
from stock.marketdata.interface import MarketData

class CannotExtractExsymbol(Exception):
    pass

class RealTimeData(MarketData):
    def __init__(self, date=None):
        MarketData.__init__(self)
        self.date = self.dt.strftime("%y%m%d")

    def get_data(self, exsymbol):
        file = os.path.join(REAL_DIR['stock'], exsymbol)
        f = open(file, "r")
        contents = f.read()
        f.close()

        # get exsymbol
        m = re.match(r"v_(.*?)=", contents)
        if m == None:
            raise CannotExtractExsymbol("cannot extract exsymbol from %s" \
                % (contents))
        exsymbol = m.group(1)

        result = re.sub("^v_.*?=\"|\";$", "", contents)
        data = result.split("~")
        pe = 0 if data[39] == '' else float(data[39])
        data[44] = '0' if data[44] == '' else data[44]
        data[45] = '0' if data[45] == '' else data[45]
        bar = Bar(exsymbol, date=self.date, dt=self.dt, \
            cnname=data[1], close=float(data[3]), lclose=float(data[4]), \
            open=float(data[5]), volume=float(data[6]), chg=float(data[31]), \
            chgperc=float(data[32]), high=float(data[33]), low=float(data[34]), \
            amount=float(data[37]), pe=pe, ampl=float(data[43]), \
            cvalue=float(data[44]), value=float(data[45]))
        return bar
