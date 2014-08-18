import os.path

ROOTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
SYMDIR = os.path.join(ROOTDIR, 'data/symbol')
HIST_DIR = {
    'index': os.path.join(ROOTDIR, 'data/history/index'),
    'stock': os.path.join(ROOTDIR, 'data/history/stock'),
    'fenhong': os.path.join(ROOTDIR, 'data/history/fenhong'),
}

SYM = {
    'all': os.path.join(SYMDIR, 'symbols.all'),
    'sh':  os.path.join(SYMDIR, 'symbols.sh'),
    'sz':  os.path.join(SYMDIR, 'symbols.sz'),
    'cy':  os.path.join(SYMDIR, 'symbols.cy'),
    'id':  os.path.join(SYMDIR, 'symbols.id'),
}

INDEX = {
    'sh': 'sh000001',
    'sz': 'sz399001',
    'cy': 'sz399006',
}


