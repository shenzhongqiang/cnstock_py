import re
from stock.marketdata.redis_store import *
import unittest
import pprint
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

