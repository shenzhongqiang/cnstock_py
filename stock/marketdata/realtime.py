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
        url = "http://qt.gtimg.cn/q=" + exsymbol
        request = Request()
        resp = request.send_request(url)
        # get exsymbol
        m = re.match(r"v_(.*?)=", resp)
        if m == None:
            raise CannotExtractExsymbol("cannot extract exsymbol from %s" \
                % (resp))
        exsymbol = m.group(1)

        result = re.sub("^v_.*?=\"|\";$", "", resp)
        data = result.split("~")
        bar = Bar(exsymbol, date=self.date, dt=self.dt, \
            cnname=data[1], close=data[3], lclose=data[4], open=data[5], \
            volume=data[6], chg=data[31], chgperc=data[32], \
            high=data[33], low=data[34], amount=data[37], \
            pe=data[39], ampl=data[43], cvalue=data[44], \
            value=data[45])
        return bar
