import os.path
import re
import json
import pprint
from stock.utils.request import *

SYMDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    '../../data/symbol')
ALL_SYM = os.path.join(SYMDIR, 'symbols.all')
SH_SYM = os.path.join(SYMDIR, 'symbols.sh')
SZ_SYM = os.path.join(SYMDIR, 'symbols.sz')
CY_SYM = os.path.join(SYMDIR, 'symbols.cy')
ID_SYM = os.path.join(SYMDIR, 'symbols.id')

def get_stock_symbol(type):
    pass

def get_index_symbol():
    pass

def download_symbols():
    base_url = "http://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&o=0&l=40&v=list_data"
    request = Request()
    symbols = []
    i = 1
    while True:
        url = base_url + "&p=" + str(i)
        print url
        result = request.send_request(url)
        pattern = re.compile('data:\'(.*)\'')
        s = pattern.search(result)
        gsymbols = s.group(1).split(',')
        symbols = symbols + gsymbols
        print gsymbols
        if len(gsymbols) < 40:
            print "ending"
            break

        i = i + 1
    print symbols
