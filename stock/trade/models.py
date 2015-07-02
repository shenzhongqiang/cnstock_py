from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, Enum, create_engine
from stock.globalvar import *

Base = declarative_base()
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
    date = Column(Date)
    amount = Column(Integer)
    type = Column(Enum('buy', 'sell'))

    def __repr__(self):
        return "<Tranx(exsymbol='%s', price='%s', date='%s', amount='%d', type='%s')>" % (
        self.exsymbol, self.price, self.date.strftime('%Y-%m-%d'), self.amount, self.type)

if __name__ == "__main__":
    engine = create_engine('sqlite:///' + DBFILE, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)
