from abc import *
import stock.marketdata
import threading
import Queue

class Filter(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, queue, marketdata, output):
        threading.Thread.__init__(self)
        self.queue = queue
        self.marketdata = marketdata
        self.output = output

    def run(self):
        while True:
            exsymbol = self.queue.get()
            self.check(exsymbol)
            self.queue.task_done()

    @abstractmethod
    def check(self, exsymbol):
        pass

class CheckResult:
    def __init__(self, exsymbol, result):
        self.exsymbol = exsymbol
        self.result = result


