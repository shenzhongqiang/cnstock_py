from stock.utils.symbol_util import *
import os

class TestRequest:
    def setup(self):
        pass

    def test_download_symbols(self):
        download_symbols()
