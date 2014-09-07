from stock.filter.zhangting import *
import unittest
import Queue
from stock.globalvar import *

class TestFilterZhangTing(unittest.TestCase):
    def setUp(self):
        queue = Queue.Queue()
        self.zhangting = ZhangTing(Queue)

    def tearDown(self):
        pass

    def test_check(self):
        print self.zhangting.check('sz300059')
