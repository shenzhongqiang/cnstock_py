import Queue
import stock.utils

class FilterMT:
    def __init__(self, filter_cls, marketdata):
        self.filter_cls = filter_cls
        self.marketdata = marketdata

    def filter_stock(self):
        queue = Queue.Queue()
        output = []

        for i in range(1):
            t = self.filter_cls(queue, self.marketdata, output)
            t.setDaemon(True)
            t.start()

        # download stock symbols
        symbols = stock.utils.symbol_util.get_stock_symbols('all')
        for symbol in symbols:
            queue.put(symbol)

        queue.join()

        output.sort(key=lambda x: x.chgperc, reverse=True)
        return output
