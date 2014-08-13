from stock.utils.symbol_util import *
import unittest
import os

class TestRequest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_stock_symbol(self):
        symbols = get_stock_symbol()
        self.assertTrue(len(symbols) > 0)
        symbols = get_stock_symbol('sh')
        self.assertTrue(len(symbols) > 0)
    
    def test_get_index_symbol(self):
        index = get_index_symbol('sh')
        self.assertEqual(index, 'sh000001')

    def test_download_symbols(self):
        download_symbols()
