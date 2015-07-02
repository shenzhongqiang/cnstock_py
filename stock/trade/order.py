from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *
from datetime import datetime
import logging
import logging.config

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class PositionAlreadyExists(Exception):
    pass

class PositionNotExists(Exception):
    pass

class NotEnoughSharesToSell(Exception):
    pass

class IllegalPrice(Exception):
    pass

class MultiplePositionsForSameSymbol(Exception):
    pass

class NotSellingAllShares(Exception):
    pass

engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False},)
Session = sessionmaker(bind=engine)

class Order:
    def __init__(self, engine=None):
        if engine == None:
            engine = create_engine('sqlite:///' + DBFILE, echo=False)
        self.Session = sessionmaker(bind=engine)

    def buy(self, exsymbol, price, buy_date, amount):
        Session = self.Session
        session = Session()
        pos = session.query(Position).filter_by(exsymbol=exsymbol).first()

        if price <= 0:
            raise IllegalPrice("%f is not a legal price" % price)

        d = datetime.strptime(buy_date, '%y%m%d')
        if pos != None:
            pos.amount += amount
        else:
            pos = Position(exsymbol=exsymbol, amount=amount)
            session.add(pos)
        tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
            amount=amount, type='buy')
        session.add(tranx)
        session.commit()
        logger.info("bought: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, buy_date))

    def sell(self, exsymbol, price, sell_date, amount):
        Session = self.Session
        session = Session()
        positions = session.query(Position).filter_by(exsymbol=exsymbol).all()
        if len(positions) > 1:
            raise MultiplePositionsForSameSymbol(exsymbol)
        if len(positions) == 0:
            raise PositionNotExists(exsymbol)
        pos = positions[0]
        if pos.amount < amount:
            raise NotEnoughSharesToSell("You are trying to sell %d, but only %d shares %s can be sold" % \
                (amount, pos.amount, exsymbol))
        if pos.amount > amount:
            pos.amount -= amount
            #raise NotSellingAllShares("You need to sell all shares of %s" % (exsymbol))
        if price <= 0:
            raise IllegalPrice("%f is not a legal price" % price)

        d = datetime.strptime(sell_date, '%y%m%d')
        tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
            amount=amount, type='sell')
        session.add(tranx)
        session.commit()
        logger.info("sold: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, sell_date))

    def get_positions(self):
        Session = self.Session
        session = Session()
        positions = session.query(Position).all()
        return positions

    def has_position(self, exsymbol):
        Session = self.Session
        session = Session()
        exsymbol = session.query(Position).filter_by(exsymbol=exsymbol).first()
        if exsymbol == None:
            return False
        else:
            return True

