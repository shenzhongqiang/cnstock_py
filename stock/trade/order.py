from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *
from datetime import datetime

class PositionAlreadyExists(Exception):
    pass

class PositionNotExists(Exception):
    pass

class NotEnoughSharesToSell(Exception):
    pass

engine = create_engine('sqlite:///' + DBFILE, echo=False)
Session = sessionmaker(bind=engine)

def buy(exsymbol, price, buy_date, amount):
    session = Session()
    pos = session.query(Position).filter_by(exsymbol=exsymbol).first()
    if pos != None:
        raise PositionAlreadyExists(exsymbol)

    d = datetime.strptime(buy_date, '%y%m%d')
    pos = Position(exsymbol=exsymbol, price=price, date=d, \
        amount=amount)
    tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
        amount=amount, type='buy')
    session.add(pos)
    session.add(tranx)
    session.commit()

def sell(exsymbol, price, buy_date, amount):
    session = Session()
    pos = session.query(Position).filter_by(exsymbol=exsymbol).first()
    if pos == None:
        raise PositionNotExists(exsymbol)
    if pos.amount < amount:
        raise NotEnoughSharesToSell("You are trying to sell %d, but only %d shares %s can be sold" % \
            (amount, pos.amount, exsymbol))

    session.delete(pos)
    d = datetime.strptime(buy_date, '%y%m%d')
    tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
        amount=amount, type='sell')
    session.add(tranx)
    session.commit()

def get_positions():
    session = Session()
    exsymbols = session.query(Position.exsymbol).all()
    return exsymbols

