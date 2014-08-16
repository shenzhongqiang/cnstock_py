import os.path
import re
from stock.utils.request import *
from stock.globalvar import *

class InvalidType(Exception):
    pass

def get_stock_symbol(type='all'):
    if type not in SYM:
        raise InvalidType('Please specify the type: all|sh|sz|cy|id')
    filename = SYM[type]
    f = open(filename, "r")
    content = f.read()
    f.close()
    symbols = content.split('\n')
    return symbols

def get_index_symbol(type):
    return INDEX[type]

def download_symbols():
    base_url = "http://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&o=0&l=40&v=list_data"
    request = Request()
    symbols = []
    i = 1
    while True:
        url = base_url + "&p=" + str(i)
        result = request.send_request(url)
        pattern = re.compile('data:\'(.*)\'')
        s = pattern.search(result)
        gsymbols = s.group(1).split(',')
        symbols = symbols + gsymbols
        if len(gsymbols) < 40:
            break

        i = i + 1

    sh_symbols = []
    sz_symbols = []
    cy_symbols = []

    p_sh = re.compile('^sh')
    p_sz = re.compile('^sz0')
    p_cy = re.compile('^sz3')
    for s in symbols:
        if p_sh.search(s) and s != INDEX['sh']:
            sh_symbols.append(s)
        elif p_sz.search(s) and s != INDEX['sz']:
            sz_symbols.append(s)
        elif p_cy.search(s) and s != INDEX['cy']:
            cy_symbols.append(s)

    f_all = open(SYM['all'], "w")
    f_sh = open(SYM['sh'], "w")
    f_sz = open(SYM['sz'], "w")
    f_cy = open(SYM['cy'], "w")
    f_all.write('\n'.join(symbols))
    f_sh.write('\n'.join(sh_symbols))
    f_sz.write('\n'.join(sz_symbols))
    f_cy.write('\n'.join(cy_symbols))
    f_all.close()
    f_sh.close()
    f_sz.close()
    f_cy.close()

