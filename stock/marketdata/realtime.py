import datetime
import re
import os.path
from stock.utils.request import *
from stock.utils.uniform import *
from stock.globalvar import *
from stock.marketdata.bar import *
from stock.marketdata.interface import *

class CannotExtractExsymbol(Exception):
    pass

class RealTimeData(MarketData):
    def __init__(self, date=None):
        self.dt = datetime.datetime.today()
        self.date = self.dt.strftime("%y%m%d")

    def get_data(self, exsymbol):
        file = ''
        if exsymbol in INDEX.values():
            file = os.path.join(REAL_DIR['index'], exsymbol)
        else:
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
        bar = Bar(exsymbol, date=self.date, dt=self.dt, \
            cnname=data[1], close=float(data[3]), lclose=float(data[4]), \
            open=float(data[5]), volume=float(data[6]), chg=float(data[31]), \
            chgperc=float(data[32]), high=float(data[33]), low=float(data[34]), \
            amount=float(data[37]), pe=float(data[39]), ampl=float(data[43]), \
            cvalue=float(data[44]), value=float(data[45]))
        return bar
