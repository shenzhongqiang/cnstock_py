from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *
from stock.trade.report import ClosedTranx
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
class IllegalNumOfAccounts(Exception):
    pass
class NotEnoughMoney(Exception):
    pass

ENGINE = create_engine('sqlite:///' + DBFILE, echo=False, \
    connect_args={'check_same_thread':False},)

class Order:
    def __init__(self, engine=ENGINE):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_account(self, initial):
        account = Account(initial=initial, profit=0)
        self.session.add(account)
        self.session.commit()

    def get_account(self):
        accounts = self.session.query(Account).all()
        if len(accounts) != 1:
            raise IllegalNumOfAccounts()
        return accounts[0]

    def get_account_balance(self):
        account = self.get_account()
        return account.initial + account.profit

    def buy(self, exsymbol, price, buy_date, amount):
        pos = self.session.query(Position).filter_by(exsymbol=exsymbol).first()

        balance = self.get_account_balance()
        if balance < price * amount:
            raise NotEnoughMoney()

        if price <= 0:
            raise IllegalPrice("%f is not a legal price" % price)

        d = datetime.strptime(buy_date, '%y%m%d')
        if pos != None:
            pos.amount += amount
        else:
            pos = Position(exsymbol=exsymbol, amount=amount)
            self.session.add(pos)
        tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
            amount=amount, closed=0, profit=0, type='buy')
        self.session.add(tranx)
        self.session.commit()
        logger.info("bought: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, buy_date))

    def sell(self, exsymbol, price, sell_date, amount):
        positions = self.session.query(Position).filter_by(exsymbol=exsymbol).all()
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
        elif pos.amount == amount:
            self.session.delete(pos)

        if price <= 0:
            raise IllegalPrice("%f is not a legal price" % price)

        # close existing open transactions
        d = datetime.strptime(sell_date, '%y%m%d')
        account = self.get_account()

        tranx_rows = self.session.query(Tranx).filter(text(
            'exsymbol=:exsymbol and closed < amount')).params(exsymbol=exsymbol).order_by(Tranx.date).all()
        remain_to_close = amount
        for open_tranx_row in tranx_rows:
            open_amount = open_tranx_row.amount - open_tranx_row.closed
            if remain_to_close <= open_amount:
                closed_tranx = ClosedTranx(exsymbol=exsymbol,
                    open_date=open_tranx_row.date,
                    open_price=open_tranx_row.price,
                    close_date=d,
                    close_price=price,
                    amount=remain_to_close)
                profit = closed_tranx.get_profit()
                open_tranx_row.profit = open_tranx_row.profit + profit
                open_tranx_row.closed = open_tranx_row.closed + remain_to_close
                account.profit = account.profit + profit
                break
            else:
                closed_tranx = ClosedTranx(exsymbol=exsymbol,
                    open_date=open_tranx_row.date,
                    open_price=open_tranx_row.price,
                    close_date=d,
                    close_price=price,
                    amount=open_amount)
                profit = closed_tranx.get_profit()
                open_tranx_row.profit = open_tranx_row.profit + profit
                open_tranx_row.closed = open_tranx_row.amount
                account.profit = account.profit + profit
                remain_to_close = remain_to_close - open_amount

        tranx = Tranx(exsymbol=exsymbol, price=price, date=d, \
            amount=amount, type='sell')
        self.session.add(tranx)
        self.session.commit()
        logger.info("sold: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, sell_date))

    def get_positions(self):
        positions = self.session.query(Position).all()
        return positions

    def has_position(self, exsymbol):
        exsymbol = self.session.query(Position).filter_by(exsymbol=exsymbol).first()
        if exsymbol == None:
            return False
        else:
            return True

