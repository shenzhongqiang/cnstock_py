import os.path

SYMDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    '../data/symbol')
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


