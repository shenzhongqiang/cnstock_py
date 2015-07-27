import os.path
import threading
import Queue
import cPickle as pickle
import datetime
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import num2date
from stock.globalvar import *

us_dir = HIST_DIR['us']
if not os.path.isdir(us_dir):
    os.makedirs(us_dir)

class Downloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            ticker = self.queue.get()
            print ticker
            self.download_history(ticker)
            self.queue.task_done()

    def download_history(self, ticker):
        date1 = datetime.date(2015,1,1)
        date2 = datetime.date.today()
        try:
            quotes = quotes_historical_yahoo(ticker, date1, date2)
            datafile = os.path.join(us_dir, ticker)
            output = open(datafile, "wb")
            pickle.dump(quotes, output)
            output.close()
        except Exception, e:
            print e

#for ticker in tickers:
#        for quote in quotes:
#            # open-high-low-close
#            day = num2date(quote[0])
#            open = quote[1]
#            close = quote[2]
#            high = quote[3]
#            low = quote[4]
#            volume = quote[5]
#            print "%s,%f,%f,%f,%f,%d" % (
#                day.strftime("%Y-%m-%d"),
#                open, high, low, close, volume)

if __name__ == "__main__":
    queue = Queue.Queue()
    for i in range(10):
        t = Downloader(queue)
        t.setDaemon(True)
        t.start()

    filepath = os.path.join(SYMDIR, "us_ticker")
    f = open(filepath)
    content = f.read()
    tickers = content.split("\n")
    f.close()
    for ticker in tickers:
        queue.put(ticker)

    queue.join()

