import re
from stock.marketdata.redis_store import *
import unittest
import pprint
import tushare as ts
from stock.globalvar import *

class TestBackTestData(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_stock_exsymbols(self):
        store = Store()
        exsymbols = store.get_stock_exsymbols()
        self.assertTrue(len(exsymbols) > 0)

    def test_get(self):
        df1 = ts.get_k_data("000001", index=False)
        store = Store()
        df2 = store.get("id000001")
        print df2
