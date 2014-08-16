from stock.globalvar import *
import unittest
import os.path

class TestGlobal(unittest.TestCase):
    def setUp(self):
        pass

    def test_global(self):
        self.assertTrue(ROOTDIR != '')
        self.assertTrue(SYMDIR != '')
