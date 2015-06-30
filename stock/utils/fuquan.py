import os.path
import datetime
import re
from stock.globalvar import *

class Fuquan:
    @classmethod
    def fuquan_history(cls, history):
        exsymbol = history[0].exsymbol
        fq_hist = cls.parse_fuquan_data(exsymbol)
        for item in fq_hist:
            exe_found = 0 # if fuquan execution date is found
            for bar in history:
                if bar.dt < item['dt']:
                    bar.open = bar.open * item['ratio']
                    bar.close = bar.close * item['ratio']
                    bar.high = bar.high * item['ratio']
                    bar.low = bar.low * item['ratio']
                    bar.volume = bar.volume / item['ratio']

    def fuquan_bar(self, bar, p):
        song = p['song']
        zhuan = p['zhuan']
        fuquan = p['fuquan']

        numerator = (song + zhuang) / 10 + 1
        bar['open'] = (bar['open'] - fuquan / 10) / numerator
        bar['high'] = (bar['high'] - fuquan / 10) / numerator
        bar['close'] = (bar['close'] - fuquan / 10) / numerator
        bar['low'] = (bar['low'] - fuquan / 10) / numerator
        bar['volume'] = bar['volume'] * numerator

    # return fuquan history as list
    @classmethod
    def parse_fuquan_data(cls, exsymbol):
        filepath = os.path.join(HIST_DIR['fuquan'], exsymbol)
        if not os.path.isfile(filepath):
            return []

        f = open(filepath, "r")
        contents = f.read()
        f.close()

        patt = re.compile(r'v_fq_%s="(.*)";' % exsymbol)
        matched = patt.match(contents)
        fq_hist = []
        if matched:
            hist_texts = matched.group(1).split('^')
            for item in hist_texts:
                data = item.split('~')
                fq_date = data[0]
                fq_ratio = float(data[1])
                fq_dt = datetime.datetime.strptime(fq_date, "%Y%m%d")
                fq_hist.append({'date': fq_date,
                    'dt': fq_dt,
                    'ratio': fq_ratio})

            fq_hist.sort(key=lambda x: x['dt'], reverse=True)
        return fq_hist
