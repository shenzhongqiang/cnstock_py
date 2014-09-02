import datetime
from stock.utils.request import *
from stock.utils.uniform import *
from stock.globalvar import *


class BackTestData:
    def __init__(self, date):
        self.date = date
        self.dt = datetime.strptime(date, "%y%m%d")

    def get_stock_data(self, exsymbol):
        stock_file = os.path.join(HIST_DIR['stock'], exsymbol)
        fenhong_file = os.path.join(HIST_DIR['fenhong'], exsymbol)


    def get_index_data(self, exsymbol):
        pass
