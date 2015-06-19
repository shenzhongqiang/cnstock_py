from stock.trade.models import *
from stock.trade.order import *
import unittest
from stock.globalvar import *

echo=False
class TestTradeOrder(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.create_all(engine)
        self.order = Order(engine)

    def tearDown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=echo)
        Base.metadata.drop_all(engine)

    def test_buy(self):
        self.order.buy('sh500001', 20.0, '140901', 100)
        with self.assertRaises(PositionAlreadyExists):
            self.order.buy('sh500001', 20.0, '140902', 200)
        with self.assertRaises(NotEnoughSharesToSell):
            self.order.sell('sh500001', 20.0, '140902', 200)
        with self.assertRaises(PositionNotExists):
            self.order.sell('sh500002', 20.0, '140902', 200)
        self.order.sell('sh500001', 25.0, '140902', 100)

    def test_get_positions(self):
        self.order.buy('sh500001', 20.0, '140901', 100)
        pos = self.order.get_positions()
        self.assertTrue(len(pos) == 1)

    def test_has_position(self):
        self.order.buy('sh500001', 20.0, '140901', 100)
        has_pos = self.order.has_position('sh500001')
        self.assertTrue(has_pos)

    def test_raise_exception(self):
        self.order.buy('sh500001', 10.0, '150101', 100)
        with self.assertRaises(PositionAlreadyExists):
            self.order.buy('sh500001', 20.0, '150101', 100)
        with self.assertRaises(IllegalPrice):
            self.order.sell('sh500001', -1, '150101', 100)
        with self.assertRaises(NotEnoughSharesToSell):
            self.order.sell('sh500001', 15.0, '150101', 500)
        with self.assertRaises(NotSellingAllShares):
            self.order.sell('sh500001', 15.0, '150101', 50)
