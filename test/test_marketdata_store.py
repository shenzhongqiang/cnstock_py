from stock.marketdata.store import *
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_exsymbols(self):
        result = get_exsymbols()
        self.assertTrue(len(result) > 1000)

    def test_get_trading_dates(self):
        dates = get_trading_dates()
        self.assertTrue(len(dates) > 100)

    def test_get(self):
        df = get('sz002140')
        self.assertTrue(len(df) > 100)
