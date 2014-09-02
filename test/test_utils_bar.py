from stock.utils.bar import *
import unittest
import os.path
from stock.globalvar import *

class TestUtilsBar(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        bar = Bar(exsymbol="sz300059", symbol="300059", close=10)
        self.assertTrue(bar != None)
