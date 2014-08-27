import datetime
import re
from bs4 import BeautifulSoup
from stock.globalvar import *

class Uniform:
    def __init__(self, ts, plans):
        self.ts = ts
        self.plan = plan

    def uniform_history(self):
        for p in plan:
            self.uniform_ts(p)

    def uniform_ts(self, p):
        exe_found = 0 # if fuquan execution date is found
        for bar in ts:
            bar_date = ts['date']
            bar_dt = datetime.strptime(bar_date, "%y%m%d")
            exe_dt = p['exe_dt']
            if exe_found == 0 and bar_dt < exe_dt:
                exe_found = 1

            if exe_found == 1:
                self.uniform_bar(bar, p)

    def uniform_bar(self, bar, p):
        song = p['song']
        zhuan = p['zhuan']
        fenhong = p['fenhong']

        numerator = (song + zhuang) / 10 + 1
        bar['open'] = (bar['open'] - fenhong / 10) / numerator
        bar['high'] = (bar['high'] - fenhong / 10) / numerator
        bar['close'] = (bar['close'] - fenhong / 10) / numerator
        bar['low'] = (bar['low'] - fenhong / 10) / numerator
        bar['volume'] = bar['volume'] * numerator


# return plan array
def parse_fenhong_output(file):
    f = open(file, "r")
    str = f.read()
    f.close()
    soup = BeautifulSoup(str)
    tables = soup.select('table[width="744"]')
    size = len(tables[1].contents)
    print tables[1].tbody.find_all("tr")
#    print tables[1].contents
#    tr = children[2]
#    print tr.children[2].string
