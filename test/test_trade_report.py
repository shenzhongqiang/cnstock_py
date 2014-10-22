from stock.trade.order import *
from stock.trade.report import *
import unittest
from stock.globalvar import *

class TestTradeReport(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=True)
        Base.metadata.create_all(engine)
        self.order = Order(engine)
        self.report = Report(engine)

    def tearDown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=True)
        Base.metadata.drop_all(engine)

    def test_get_closed_tranx(self):
        self.order.buy('sh000001', 20, '140901', 1000)
        self.order.buy('sh000002', 50, '140901', 2000)
        self.order.sell('sh000001', 30, '140902', 1000)
        self.order.sell('sh000002', 60, '140902', 2000)
        closed = self.report.get_closed_tranx()
        self.assertTrue(len(closed) == 2)


