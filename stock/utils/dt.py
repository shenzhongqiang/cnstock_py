import datetime
import re

def parse_datetime(string):
    patt = re.compile("(\d\d)(\d\d)(\d\d)")
    s = patt.search(string)
    year = int(s.group(1)) + 2000
    mon = int(s.group(2))
    date = int(s.group(3))
    return datetime.datetime(year, mon, date)

if __name__ == "__main__":
    print parse_datetime("150327")
