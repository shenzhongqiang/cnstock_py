from stock.utils.symbol_util import *
import unittest
import os.path

class TestSymbolUtil(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_stock_symbol(self):
        symbols = get_stock_symbols()
        self.assertTrue(len(symbols) > 0)
        symbols = get_stock_symbols('sh')
        self.assertTrue(len(symbols) > 0)

    def test_get_index_symbols(self):
        indice = get_index_symbols()
        self.assertListEqual(indice, ['sz399001', 'sz399006', 'sh000001'])

    def test_get_index_symbol(self):
        index = get_index_symbol('sh')
        self.assertEqual(index, 'sh000001')

    def test_download_symbols(self):
        download_symbols()
        self.assertTrue(os.path.isfile(SYM['all']))
        self.assertTrue(os.path.isfile(SYM['sh']))
        self.assertTrue(os.path.isfile(SYM['sz']))
        self.assertTrue(os.path.isfile(SYM['cy']))
