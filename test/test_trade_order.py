from stock.trade.models import *
from stock.trade.order import *
import unittest
from stock.globalvar import *

class TestTradeOrder(unittest.TestCase):
#    @classmethod
#    def setup_class(cls):
#        engine = create_engine('sqlite:///' + DBFILE, echo=False)
#        Base.metadata.create_all(engine)
#
#    @classmethod
#    def teardown_class(cls):
#        engine = create_engine('sqlite:///' + DBFILE, echo=False)
#        Base.metadata.drop_all(engine)
#
    def setUp(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=True)
        Base.metadata.create_all(engine)
        self.order = Order(engine)

    def tearDown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=True)
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
