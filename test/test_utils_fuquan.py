from stock.utils.fuquan import *
import unittest
import os.path
from stock.globalvar import *
from stock.marketdata import *

class TestUtilsFuquan(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_fuquan_data(self):
        self.assertTrue(len(Fuquan.parse_fuquan_data('sz300253')) > 0)
        marketdata = backtestdata.BackTestData(date='150618')
        history = marketdata.get_archived_history_in_file('sz300253')
        Fuquan.fuquan_history(history)
        history = marketdata.get_archived_history_in_file('sh000001')
        Fuquan.fuquan_history(history)
