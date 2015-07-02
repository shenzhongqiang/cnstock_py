import copy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *

class NotEnoughSharesToSell(Exception):
    pass

class OpenTranx:
    def __init__(self, exsymbol, open_date,
        open_price, amount):
        self.exsymbol = exsymbol
        self.open_date = open_date
        self.open_price = open_price
        self.amount = amount

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
        exsymbol_tranx = {}
        closed_tranx = []

        for row in tranx_rows:
            t = row.type
            if t == 'buy':
                if not row.exsymbol in exsymbol_tranx:
                    exsymbol_tranx[row.exsymbol] = {"amount": 0, "queue": []}
                exsymbol_tranx[row.exsymbol]["amount"] += row.amount
                ot = OpenTranx(exsymbol=row.exsymbol,
                    open_date=row.date,
                    open_price=row.price,
                    amount=row.amount)
                exsymbol_tranx[row.exsymbol]["queue"].append(ot)
            else:
                open_amount = exsymbol_tranx[row.exsymbol]["amount"]
                open_queue = exsymbol_tranx[row.exsymbol]["queue"]
                if open_amount < row.amount:
                    raise NotEnoughSharesToSell(
                        "%s: trying to sell %d shares while only %d shares were opened" % (
                            row.exsymbol, row.amount, open_amount))

                updated_open_queue = copy.deepcopy(open_queue)
                amount_to_close = row.amount
                for ot in open_queue:
                    if ot.amount <= amount_to_close:
                        updated_open_queue.pop(0)
                        amount_to_close -= ot.amount
                        ct = ClosedTranx(exsymbol=row.exsymbol,
                            open_date=ot.open_date,
                            open_price=ot.open_price,
                            close_date=row.date,
                            close_price=row.price,
                            amount=ot.amount)
                        closed_tranx.append(ct)
                    else:
                        if amount_to_close == 0:
                            break
                        else:
                            updated_open_queue[0].amount -= amount_to_close
                            ct = ClosedTranx(exsymbol=row.exsymbol,
                                open_date=ot.open_date,
                                open_price=ot.open_price,
                                close_date=row.date,
                                close_price=row.price,
                                amount=amount_to_close)
                            closed_tranx.append(ct)
                            amount_to_close = 0
                            break
                exsymbol_tranx[row.exsymbol]["queue"] = updated_open_queue
                exsymbol_tranx[row.exsymbol]["amount"] -= row.amount

        return closed_tranx

    def get_profit_loss(self):
        closed = self.get_closed_tranx()
        total = 0
        for ct in closed:
            total += ct.pl
        return total

    def print_report(self):
        closed = self.get_closed_tranx()
        total = 0
        print "\nEXSymbol\tOpen Date\tOpen\tAmount\tClose Date\tClose\tProfit"
        for ct in closed:
            print("%s\t%s\t%.2f\t%d\t%s\t%.2f\t%.2f" % (ct.exsymbol, \
                ct.open_date.strftime('%Y-%m-%d'), \
                ct.open_price, \
                ct.amount, \
                ct.close_date.strftime('%Y-%m-%d'), \
                ct.close_price, \
                ct.pl))
            total += ct.pl

        print "Total: %d" % (total)

