from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from stock.globalvar import DBFILE

Base = declarative_base()
class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    initial = Column(Float)
    profit = Column(Float)
    positions = relationship("Position")
    Transactions = relationship("Tranx")

    def __repr__(self):
        return "<Account(initial='%f', profit='%f')>" % (
            self.initial, self.profit)

class Position(Base):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True)
    exsymbol = Column(String(8))
    amount = Column(Integer)
    account_id = Column(Integer, ForeignKey('account.id'))

    def __repr__(self):
        return "<Position(exsymbol='%s', amount='%d', account_id='%d')>" % (
        self.exsymbol, self.amount, self.account_id)

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
    account_id = Column(Integer, ForeignKey('account.id'))

    def __repr__(self):
        closed = self.closed
        if self.closed == None:
            closed = 0
        profit = self.profit
        if self.profit == None:
            profit = 0.0
        return "<Tranx(exsymbol='%s', price='%f', date='%s', amount='%d', closed='%d', profit='%f', type='%s', account_id='%d')>" % (
        self.exsymbol, self.price, self.date.strftime('%Y-%m-%d %H:%M:%S'),
        self.amount, closed, profit, self.type, self.account_id)

if __name__ == "__main__":
    engine = create_engine('sqlite:///' + DBFILE, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)
