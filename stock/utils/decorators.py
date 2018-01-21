import time
def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print "execute time %d secs" % (end - start)
        return result
    return wrapper
