from stock.marketdata import *
import unittest
import pprint
from stock.globalvar import *

class TestBackTestData(unittest.TestCase):
    def setUp(self):
        self.backtestdata = backtestdata.BackTestData(date='140801')

    def tearDown(self):
        pass

    def test_get_history_in_file(self):
        history = self.backtestdata.get_history_in_file('sz300059')
        self.assertTrue(len(history) > 0)

    def test_get_history_by_date(self):
        history = self.backtestdata.get_history_by_date('sz300059')
        self.assertTrue(len(history) > 0)

    def test_get_data(self):
        bar_today = self.backtestdata.get_data('sz300059')
        self.assertEqual(bar_today.symbol, '300059')
        self.assertEqual(bar_today.exsymbol, 'sz300059')
        self.assertTrue(isinstance(bar_today.close, float))
