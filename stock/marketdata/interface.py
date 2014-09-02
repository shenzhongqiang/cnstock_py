from abc import ABCMeta

class MarketData:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_data(self):
        pass

