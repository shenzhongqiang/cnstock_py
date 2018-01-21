from stock.trade.order import *
from stock.trade.report import *
import datetime
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
        buy_dt = datetime.datetime.strptime('20170601', '%Y%m%d')
        sell_dt = datetime.datetime.strptime('20170602', '%Y%m%d')
        self.order.buy('sh000001', 20, buy_dt, 1000)
        self.order.buy('sh000002', 50, buy_dt, 2000)
        self.order.sell('sh000001', 30, sell_dt, 1000)
        balance = self.order.get_account_balance()
        self.assertAlmostEqual(balance, 109928.8)
        self.order.sell('sh000002', 60, sell_dt, 2000)
        balance = self.order.get_account_balance()
        self.assertAlmostEqual(balance, 129630.4)
        closed = self.report.get_closed_tranx()
        comm = closed[0].get_comm()
        self.assertEqual(comm, 71.2)
        comm = closed[1].get_comm()
        self.assertEqual(comm, 298.4)
        self.assertEqual(len(closed), 2)
        summary = self.report.get_summary()
        self.assertAlmostEqual(summary.profit, 29630.4)

    def test_sell_seperate(self):
        buy_dt = datetime.datetime.strptime('20170601', '%Y%m%d')
        sell_dt1 = datetime.datetime.strptime('20170602', '%Y%m%d')
        sell_dt2 = datetime.datetime.strptime('20170603', '%Y%m%d')
        self.order.buy('sh000001', 20, buy_dt, 2000)
        self.order.sell('sh000001', 30, sell_dt1, 1000)
        self.order.sell('sh000001', 40, sell_dt2, 1000)
        closed = self.report.get_closed_tranx()
        self.assertEqual(len(closed), 2)
        summary = self.report.get_summary()
        self.assertAlmostEqual(summary.profit, 29839.6)

    def test_buy_seperate(self):
        buy_dt = datetime.datetime.strptime('20170601', '%Y%m%d')
        sell_dt1 = datetime.datetime.strptime('20170602', '%Y%m%d')
        sell_dt2 = datetime.datetime.strptime('20170603', '%Y%m%d')
        self.order.buy('sh000001', 20, buy_dt, 2000)
        self.order.buy('sh000001', 30, buy_dt, 1000)
        positions = self.order.get_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].amount, 3000)
        self.order.sell('sh000001', 40, sell_dt2, 3000)
        closed = self.report.get_closed_tranx()
        self.assertEqual(len(closed), 2)
        summary = self.report.get_summary()
        self.assertAlmostEqual(summary.profit, 49724.4)

    def test_max_drawdown(self):
        buy_dt1 = datetime.datetime.strptime('20170601', '%Y%m%d')
        sell_dt1 = datetime.datetime.strptime('20170602', '%Y%m%d')
        buy_dt2 = datetime.datetime.strptime('20170603', '%Y%m%d')
        sell_dt2 = datetime.datetime.strptime('20170604', '%Y%m%d')
        buy_dt3 = datetime.datetime.strptime('20170605', '%Y%m%d')
        sell_dt3 = datetime.datetime.strptime('20170606', '%Y%m%d')
        buy_dt4 = datetime.datetime.strptime('20170607', '%Y%m%d')
        sell_dt4 = datetime.datetime.strptime('20170608', '%Y%m%d')
        buy_dt5 = datetime.datetime.strptime('20170609', '%Y%m%d')
        sell_dt5 = datetime.datetime.strptime('20170610', '%Y%m%d')
        self.order.buy('sh000001', 30, buy_dt1, 1000)
        self.order.sell('sh000001', 20, sell_dt1, 1000)
        self.order.buy('sh000001', 20, buy_dt2, 1000)
        self.order.sell('sh000001', 70, sell_dt2, 1000)
        self.order.buy('sh000001', 50, buy_dt3, 1000)
        self.order.sell('sh000001', 30, sell_dt3, 1000)
        self.order.buy('sh000001', 50, buy_dt4, 1000)
        self.order.sell('sh000001', 20, sell_dt4, 1000)
        self.order.buy('sh000001', 50, buy_dt5, 1000)
        self.order.sell('sh000001', 100, sell_dt5, 1000)
        closed = self.report.get_closed_tranx()
        summary = self.report.get_summary()
        self.assertAlmostEqual(summary.profit, 39402.0)
        self.assertAlmostEqual(summary.max_drawdown, 50172.4)
        self.assertAlmostEqual(summary.comm_total, 598.0)
        self.assertAlmostEqual(summary.num_of_trades, 5)
        self.assertAlmostEqual(summary.win_rate, 0.4)

    def test_max_drawdown(self):
        buy_dt1 = datetime.datetime.strptime('20170601', '%Y%m%d')
        sell_dt1 = datetime.datetime.strptime('20170602', '%Y%m%d')
        self.order.buy('sh000001', 30, buy_dt1, 1000)
        self.order.sell('sh000001', 20, sell_dt1, 1000)
        closed = self.report.get_closed_tranx()
        summary = self.report.get_summary()
        self.assertAlmostEqual(summary.profit, -10061.2)
        self.assertAlmostEqual(summary.max_drawdown, 10061.2)
        self.assertAlmostEqual(summary.comm_total, 61.2)
        self.assertAlmostEqual(summary.num_of_trades, 1)
        self.assertAlmostEqual(summary.win_rate, 0.0)

    def test_get_commission(self):
        print get_commission(4.30, 4.31, 5000)
