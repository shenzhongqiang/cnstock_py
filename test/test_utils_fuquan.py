from stock.utils import fuquan
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
        self.assertTrue(len(fuquan.parse_fuquan_data('sz300253')) > 0)
        marketdata = backtestdata.BackTestData(date='151031')
        history = marketdata.get_archived_history_in_file('sz300253')
        fuquan.fuquan_history(history)
        history = marketdata.get_archived_history_in_file('sh000001')
        fuquan.fuquan_history(history)
