#!/usr/bin/python
import os.path
import stock.utils.symbol_util
from stock.globalvar import *

if not os.path.isdir(SYMDIR):
    os.makedirs(SYMDIR)

print "start to download symbols"
stock.utils.symbol_util.download_symbols()
stock.utils.symbol_util.get_zz500_symbols()
print "download finished"

