import json
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *
from stock.trade.report import ClosedTranx
from datetime import datetime
import logging

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
        self.account = account

    def set_params(self, params=None):
        self.account.params = json.dumps(params)
        self.session.add(self.account)
        self.session.commit()

    def get_account_id(self):
        return self.account.id

    def get_account_balance(self):
        account = self.account
        return account.initial + account.profit

    def buy(self, exsymbol, price, buy_date, amount):
        pos = self.session.query(Position).filter_by(exsymbol=exsymbol, account_id=self.account.id).first()

        buy_date_str = buy_date.strftime('%Y-%m-%d %H:%M:%S')
        balance = self.get_account_balance()
        if balance < price * amount:
            raise NotEnoughMoney()

        if price <= 0:
            raise IllegalPrice("%f is not a legal price" % price)

        if pos != None:
            pos.amount += amount
        else:
            pos = Position(exsymbol=exsymbol, amount=amount, account_id=self.account.id)
            self.session.add(pos)
        tranx = Tranx(exsymbol=exsymbol, price=price, date=buy_date, \
            amount=amount, closed=0, profit=0, type='buy',
            account_id=self.account.id)
        self.session.add(tranx)
        self.session.commit()
        logger.info("buy: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, buy_date_str))

    def sell(self, exsymbol, price, sell_date, amount):
        positions = self.session.query(Position).filter_by(exsymbol=exsymbol, account_id=self.account.id).all()
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
        sell_date_str = sell_date.strftime('%Y-%m-%d %H:%M:%S')
        account = self.account

        tranx_rows = self.session.query(Tranx).filter(text(
            'exsymbol=:exsymbol and account_id=:account_id and closed < amount')).params(
            exsymbol=exsymbol, account_id=self.account.id).order_by(Tranx.date).all()
        remain_to_close = amount
        for open_tranx_row in tranx_rows:
            open_amount = open_tranx_row.amount - open_tranx_row.closed
            if remain_to_close <= open_amount:
                closed_tranx = ClosedTranx(exsymbol=exsymbol,
                    open_date=open_tranx_row.date,
                    open_price=open_tranx_row.price,
                    close_date=sell_date,
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
                    close_date=sell_date,
                    close_price=price,
                    amount=open_amount)
                profit = closed_tranx.get_profit()
                open_tranx_row.profit = open_tranx_row.profit + profit
                open_tranx_row.closed = open_tranx_row.amount
                account.profit = account.profit + profit
                remain_to_close = remain_to_close - open_amount

        tranx = Tranx(exsymbol=exsymbol, price=price, date=sell_date, \
            amount=amount, type='sell', account_id=self.account.id)
        self.session.add(tranx)
        self.session.commit()
        logger.info("sell: symbol: %s, amount: %d, price: %f, date: %s" %
            (exsymbol, amount, price, sell_date_str))

    def get_positions(self):
        positions = self.session.query(Position).filter_by(account_id=self.account.id).all()
        return positions

    def get_position(self, exsymbol):
        position = self.session.query(Position).filter_by(exsymbol=exsymbol).first()
        if position == None:
            raise Exception("position %s does not exist" % exsymbol)
        return position

    def has_position(self, exsymbol):
        exsymbol = self.session.query(Position).filter_by(exsymbol=exsymbol, account_id=self.account.id).first()
        if exsymbol == None:
            return False
        else:
            return True

