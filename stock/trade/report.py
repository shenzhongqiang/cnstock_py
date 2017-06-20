import datetime
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stock.globalvar import *
from stock.trade.models import *

class NotEnoughSharesToSell(Exception):
    pass

def get_commission(open_price, close_price, amount):
    return 8e-4 * open_price * amount + \
        8e-4 * close_price * amount + \
        6e-4 * amount * 2 + \
        1e-3 * close_price * amount

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
        self.comm = get_commission(open_price, close_price, amount)
        self.pl = (close_price - open_price) * amount - self.comm

    def get_exsymbol(self):
        return self.exsymbol

    def get_open_date(self):
        return self.open_date.strftime('%Y-%m-%d %H:%M:%S')

    def get_close_date(self):
        return self.close_date.strftime('%Y-%m-%d %H:%M:%S')

    def get_open_price(self):
        return self.open_price

    def get_close_price(self):
        return self.close_price

    def get_amount(self):
        return self.amount

    def get_comm(self):
        return self.comm

    def get_profit(self):
        return self.pl

    def get_change(self):
        return self.close_price /self.open_price - 1

class Result:
    def __init__(self, profit, max_drawdown, num_of_trades=None,
        win_rate=None, comm_total=None):
        self.profit = profit
        self.max_drawdown = max_drawdown
        self.num_of_trades = num_of_trades
        self.win_rate = win_rate
        self.comm_total = comm_total

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

    def __get_profit_loss(self, closed_tranx):
        total = 0
        for ct in closed_tranx:
            total += ct.pl
        return total

    def __get_max_drawdown(self, closed_tranx):
        cum_total = 0.0
        profit_series = []
        for ct in closed_tranx:
            cum_total += ct.get_profit()
            profit_series.append(cum_total)

        if len(profit_series) == 0:
            return 0.0

        j = np.argmax(np.maximum.accumulate(profit_series) - profit_series)
        i = np.argmax(profit_series[:j+1])
        max_drawdown = profit_series[i] - profit_series[j]
        return max_drawdown

    def __get_win_trades(self, closed_tranx):
        win_trades = 0
        for ct in closed_tranx:
            chg = ct.get_change()
            if chg > 0:
                win_trades +=1
        return win_trades

    def __get_comm_total(self, closed_tranx):
        comm_total = 0.0
        for ct in closed_tranx:
            comm_total += ct.get_comm()
        return comm_total

    def get_summary(self):
        closed = self.get_closed_tranx()
        cum_total = self.__get_profit_loss(closed)
        comm_total = self.__get_comm_total(closed)
        win_trades = self.__get_win_trades(closed)
        max_drawdown = self.__get_max_drawdown(closed)
        win_rate = float(win_trades) / len(closed)
        return Result(
            profit=cum_total,
            max_drawdown=max_drawdown,
            num_of_trades=len(closed),
            win_rate=win_rate,
            comm_total=comm_total,
        )

    def print_report(self):
        closed = self.get_closed_tranx()
        cum_total = 0
        print "\nEXSymbol\tOpen Date\tOpen\tAmount\tClose Date\tClose\tProfit\tPercent"
        series = []
        win_trades = 0
        comm_total = 0
        for ct in closed:
            chg = ct.get_change()
            if chg > 0:
                win_trades +=1
            cum_total += ct.get_profit()
            comm_total += ct.get_comm()
            series.append(cum_total)
            print("%s\t%s\t%.2f\t%d\t%s\t%.2f\t%.2f\t%.4f\t" % (
                ct.get_exsymbol(),
                ct.get_open_date(),
                ct.get_open_price(),
                ct.get_amount(),
                ct.get_close_date(),
                ct.get_close_price(),
                ct.get_profit(),
                chg))

        max_drawdown = self.__get_max_drawdown(closed)
        win_rate = float(win_trades) / len(closed)
        print "Profit: %f" % (cum_total)
        print "Max Drawdown: %f" % (max_drawdown)
        print "Num of Trades: %d" % (len(closed))
        print "Win Rate: %f" % win_rate
        print "Comm Cost: %f" % comm_total

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(DateFormatter("%Y%m%d"))
        dates = [ x.open_date for x in closed ]
        min_dt = dates[0]
        max_dt = dates[-1]
        delta = datetime.timedelta(days=2)
        ax.set_xlim(min_dt - delta, max_dt + delta)
        ax.xaxis_date()
        ax.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
        plt.plot(dates, series)
        plt.show()
