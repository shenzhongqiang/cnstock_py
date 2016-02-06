from stock.trade.order import *
from stock.trade.report import *
import unittest
from stock.globalvar import *

echo=False
class TestTradeReport(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.create_all(engine)
        self.order = Order(engine)
        self.report = Report(engine)
        self.order.add_account(100000)

    def tearDown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.drop_all(engine)

    def test_get_closed_tranx(self):
        self.order.buy('sh000001', 20, '140901', 1000)
        self.order.buy('sh000002', 50, '140901', 2000)
        self.order.sell('sh000001', 30, '140902', 1000)
        balance = self.order.get_account_balance()
        self.assertAlmostEqual(balance, 109928.8)
        self.order.sell('sh000002', 60, '140902', 2000)
        balance = self.order.get_account_balance()
        self.assertAlmostEqual(balance, 129630.4)
        closed = self.report.get_closed_tranx()
        comm = closed[0].get_comm()
        self.assertEqual(comm, 71.2)
        comm = closed[1].get_comm()
        self.assertEqual(comm, 298.4)
        self.assertEqual(len(closed), 2)
        pl = self.report.get_profit_loss()
        self.assertAlmostEqual(pl, 29630.4)
        self.report.print_report()

    def test_sell_seperate(self):
        self.order.buy('sh000001', 20, '140901', 2000)
        self.order.sell('sh000001', 30, '140902', 1000)
        self.order.sell('sh000001', 40, '140903', 1000)
        closed = self.report.get_closed_tranx()
        self.assertEqual(len(closed), 2)
        pl = self.report.get_profit_loss()
        self.assertAlmostEqual(pl, 29839.6)
        self.report.print_report()

    def test_buy_seperate(self):
        self.order.buy('sh000001', 20, '140901', 2000)
        self.order.buy('sh000001', 30, '140901', 1000)
        positions = self.order.get_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].amount, 3000)
        self.order.sell('sh000001', 40, '140903', 3000)
        closed = self.report.get_closed_tranx()
        self.assertEqual(len(closed), 2)
        pl = self.report.get_profit_loss()
        self.assertAlmostEqual(pl, 49724.4)
        self.report.print_report()
