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

engine = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False},)
Session = sessionmaker(bind=engine)

def buy(exsymbol, price, buy_date, amount):
    session = Session()
    pos = session.query(Position).filter_by(exsymbol=exsymbol).first()
    if pos != None:
        raise PositionAlreadyExists(exsymbol)
    if price <= 0:
        raise IllegalPrice("%f is not a legal price" % price)

    d = datetime.strptime(buy_date, '%y%m%d')
    pos = Position(exsymbol=exsymbol, price=price, date=d, \
        amount=amount)
    tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
        amount=amount, type='buy')
    session.add(pos)
    session.add(tranx)
    session.commit()
    logger.info("bought: symbol: %s, amount: %d, price: %f, date: %s" %
        (exsymbol, amount, price, buy_date))

def sell(exsymbol, price, sell_date, amount):
    session = Session()
    pos = session.query(Position).filter_by(exsymbol=exsymbol).first()
    if pos == None:
        raise PositionNotExists(exsymbol)
    if pos.amount < amount:
        raise NotEnoughSharesToSell("You are trying to sell %d, but only %d shares %s can be sold" % \
            (amount, pos.amount, exsymbol))
    if price <= 0:
        raise IllegalPrice("%f is not a legal price" % price)

    session.delete(pos)
    d = datetime.strptime(sell_date, '%y%m%d')
    tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
        amount=amount, type='sell')
    session.add(tranx)
    session.commit()
    logger.info("sold: symbol: %s, amount: %d, price: %f, date: %s" %
        (exsymbol, amount, price, sell_date))

def get_positions():
    session = Session()
    positions = session.query(Position).all()
    return positions

def has_position(exsymbol):
    session = Session()
    exsymbol = session.query(Position).filter_by(exsymbol=exsymbol).first()
    if exsymbol == None:
        return False
    else:
        return True

