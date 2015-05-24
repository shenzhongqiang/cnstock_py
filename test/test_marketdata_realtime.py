from stock.marketdata.realtimedata import *
import unittest
from stock.globalvar import *

class TestRealTimeData(unittest.TestCase):
    def setUp(self):
        self.realtimedata = RealTimeData()

    def tearDown(self):
        pass

    def test_get_history_in_file(self):
        history = self.realtimedata.get_history_in_file('sz300059')
        self.assertTrue(len(history) > 0)

    def test_get_history_by_date(self):
        history = self.realtimedata.get_history_by_date('sz300059')
        self.assertTrue(len(history) > 0)

    def test_get_data(self):
        bar_now = self.realtimedata.get_data('sz300059')
        self.assertEqual(bar_now.symbol, '300059')
        self.assertEqual(bar_now.exsymbol, 'sz300059')
        self.assertTrue(isinstance(bar_now.close, float))
