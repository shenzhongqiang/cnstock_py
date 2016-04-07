from stock.trade.models import *
from stock.trade.order import *
import unittest
import datetime
from stock.globalvar import *

echo=False
class TestTradeOrder(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.create_all(engine)
        self.order = Order(engine)
        self.order.add_account(100000)

    def tearDown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.drop_all(engine)

    def test_buy(self):
        open_date = datetime.datetime.strptime('140901', '%y%m%d')
        close_date = datetime.datetime.strptime('140902', '%y%m%d')
        self.order.buy('sh500001', 20.0, open_date, 100)
        with self.assertRaises(NotEnoughSharesToSell):
            self.order.sell('sh500001', 20.0, close_date, 200)
        with self.assertRaises(PositionNotExists):
            self.order.sell('sh500002', 20.0, close_date, 200)
        self.order.sell('sh500001', 25.0, close_date, 100)

    def test_get_positions(self):
        open_date = datetime.datetime.strptime('140901', '%y%m%d')
        close_date = datetime.datetime.strptime('140902', '%y%m%d')
        self.order.buy('sh500001', 20.0, open_date, 100)
        pos = self.order.get_positions()
        self.assertTrue(len(pos) == 1)

    def test_has_position(self):
        open_date = datetime.datetime.strptime('140901', '%y%m%d')
        close_date = datetime.datetime.strptime('140902', '%y%m%d')
        self.order.buy('sh500001', 20.0, open_date, 100)
        has_pos = self.order.has_position('sh500001')
        self.assertTrue(has_pos)

    def test_raise_exception(self):
        open_date = datetime.datetime.strptime('150101', '%y%m%d')
        close_date = datetime.datetime.strptime('150101', '%y%m%d')
        self.order.buy('sh500001', 10.0, open_date, 100)
        with self.assertRaises(IllegalPrice):
            self.order.sell('sh500001', -1, close_date, 50)
        with self.assertRaises(NotEnoughSharesToSell):
            self.order.sell('sh500001', 15.0, close_date, 500)
        self.order.sell('sh500001', 15.0, close_date, 50)
        with self.assertRaises(PositionNotExists):
            self.order.sell('sh500001', 15.0, close_date, 500)
