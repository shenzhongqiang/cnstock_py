import os.path
import re
from stock.utils.request import *
from stock.globalvar import *

class InvalidType(Exception):
    pass

def get_stock_symbols(type='all'):
    if type not in SYM:
        raise InvalidType('Please specify the type: all|sh|sz|cy')
    filename = SYM[type]
    f = open(filename, "r")
    content = f.read()
    f.close()
    symbols = content.split('\n')
    symbols = filter(None, symbols)
    return symbols

def get_index_symbols():
    return INDEX.values()

def get_index_symbol(type):
    return INDEX[type]

def get_trading_dates():
    file = os.path.join(HIST_DIR['stock'], "latest", 'sh000001')
    f = open(file, "r")
    contents = f.read()
    f.close()
    lines = contents.split('\\n\\\n')

    dates = []
    start = 0
    i = len(lines) - 2
    while i >= 2:
        line = lines[i]
        (date, o, close, high, low, volume) = line.split(' ')
        dates.append(date)
        i = i - 1

    return dates

def get_archived_trading_dates():
    dates = []
    for year in ARCHIVED_YEARS:
        filepath = os.path.join(HIST_DIR['stock'], year, 'sh000001')
        f = open(filepath, "r")
        contents = f.read()
        f.close()
        lines = contents.split('\\n\\\n')

        start = 0
        i = len(lines) - 2
        while i >= 1:
            line = lines[i]
            (date, o, close, high, low, volume) = line.split(' ')
            dates.append(date)
            i = i - 1

    return dates

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

def is_symbol_cy(symbol):
    patt = re.compile('^sz3')
    if patt.search(symbol) and symbol != INDEX['cy']:
        return True
    else:
        return False

def is_symbol_sh(symbol):
    patt = re.compile('^sh')
    if patt.search(symbol) and symbol != INDEX['sh']:
        return True
    else:
        return False

def is_symbol_sz(symbol):
    patt = re.compile('^sz0')
    if patt.search(symbol) and symbol != INDEX['sz']:
        return True
    else:
        return False
