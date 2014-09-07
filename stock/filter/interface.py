from abc import *
import stock.marketdata
import threading
import Queue

class Filter(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, queue, marketdata):
        threading.Thread.__init__(self)
        self.queue = queue
        self.marketdata = marketdata

    def run(self):
        while True:
            exsymbol = self.queue.get()
            print exsymbol
            self.check(exsymbol)
            self.queue.task_done()

    @abstractmethod
    def check(self, exsymbol):
        pass
