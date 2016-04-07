from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, create_engine
from stock.globalvar import *

Base = declarative_base()
class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    initial = Column(Float)
    profit = Column(Float)

    def __repr__(self):
        return "<Account(initial='%f', profit='%f')>" % (
            self.initial, self.profit)

class Position(Base):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True)
    exsymbol = Column(String(8))
    amount = Column(Integer)

    def __repr__(self):
        return "<Position(exsymbol='%s', amount='%d')>" % (
        self.exsymbol, self.amount)

class Tranx(Base):
    __tablename__ = 'tranx'
    id = Column(Integer, primary_key=True)
    exsymbol = Column(String(8))
    price = Column(Float)
    date = Column(DateTime)
    amount = Column(Integer)
    closed = Column(Integer)
    profit = Column(Float)
    type = Column(Enum('buy', 'sell'))

    def __repr__(self):
        return "<Tranx(exsymbol='%s', price='%s', date='%s', amount='%d', closed='%d', profit='%f', type='%s')>" % (
        self.exsymbol, self.price, self.date.strftime('%Y-%m-%d %H:%M:%S'),
        self.amount, self.closed, self.profit, self.type)

if __name__ == "__main__":
    engine = create_engine('sqlite:///' + DBFILE, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)
