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
    def setup(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=False)
        Base.metadata.create_all(engine)

    def teardown(self):
        engine = create_engine('sqlite:///' + DBFILE, echo=False)
        Base.metadata.drop_all(engine)

    def test_buy(self):
        buy('sh500001', 20.0, '140901', 100)
        with self.assertRaises(PositionAlreadyExists):
            buy('sh500001', 20.0, '140902', 200)
        with self.assertRaises(NotEnoughSharesToSell):
            sell('sh500001', 20.0, '140902', 200)
        with self.assertRaises(PositionNotExists):
            sell('sh500002', 20.0, '140902', 200)
        sell('sh500001', 25.0, '140902', 100)

    def test_get_positions(self):
        buy('sh500001', 20.0, '140901', 100)
        pos = get_positions()
        self.assertTrue(len(pos) == 1)

