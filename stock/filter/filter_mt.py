import stock.utils

class FilterMT:
    def __init__(self, filter_cls, marketdata):
        self.filter_cls = filter_cls
        self.marketdata = marketdata
        self.output = []
        self.filter_ins = filter_cls(marketdata, self.output)

    def filter_stock(self):
        # get all stock symbols
        symbols = stock.utils.symbol_util.get_stock_symbols('all')
        for symbol in symbols:
            self.filter_ins.check(symbol)

        self.output.sort(key=lambda x: x.chgperc, reverse=True)
        return self.output
