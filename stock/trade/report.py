from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *

class ClosedTranx:
    def __init__(self, exsymbol, open_date, close_date, \
        open_price, close_price, amount):
        self.exsymbol = exsymbol
        self.open_date = open_date
        self.close_date = close_date
        self.open_price = open_price
        self.close_price = close_price
        self.amount = amount
        self.pl = (close_price - open_price) * amount



class Report:
    def __init__(self, engine=None):
        if engine == None:
            engine = create_engine('sqlite:///' + DBFILE, echo=False)
        self.Session = sessionmaker(bind=engine)

    def get_closed_tranx(self):
        Session = self.Session
        session = Session()
        tranx_rows = session.query(Tranx).order_by(Tranx.date).all()
        opened = []
        closed = []

        for row in tranx_rows:
            t = row.type
            if t == 'buy':
                opened.append(row)
            else:
                matched_row = filter(lambda x: x.exsymbol == row.exsymbol, opened)[0]
                ct = ClosedTranx(exsymbol=row.exsymbol, \
                    open_date=matched_row.date, \
                    open_price=matched_row.price, \
                    close_date=row.date, \
                    close_price=row.price, \
                    amount=row.amount)
                closed.append(ct)
                opened.remove(matched_row)

        return closed

    def get_profit_loss(self):
        closed = self.get_closed_tranx()
        total = 0
        for ct in closed:
            total += ct.pl
        return total

    def print_report(self):
        closed = self.get_closed_tranx()
        total = 0
        for ct in closed:
            print("%s, %s, %f, %d, %s, %f, %f" % (ct.exsymbol, \
                ct.open_date.strftime('%Y-%m-%d'), \
                ct.open_price, \
                ct.amount, \
                ct.close_date.strftime('%Y-%m-%d'), \
                ct.close_price, \
                ct.pl))
            total += ct.pl

        print "Total: %d" % (total)


if __name__ == "__main__":
    from stock.trade.order import *
    from sqlalchemy.ext.declarative import declarative_base
    engine = create_engine('sqlite:///' + DBFILE, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)
    buy('sh000001', 20, '140901', 1000)
    buy('sh000002', 50, '140901', 2000)
    sell('sh000001', 30, '140902', 1000)
    sell('sh000002', 60, '140902', 2000)

    report = Report(engine)
    report.print_report()
    Base.metadata.drop_all(engine)
