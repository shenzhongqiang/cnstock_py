import importlib

def get_store(type):
    modname = "stock.marketdata.%s" % type
    mod = importlib.import_module(modname)
    cls = getattr(mod, "Store")
    return cls
