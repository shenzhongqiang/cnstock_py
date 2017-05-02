import datetime

def parse_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d")

if __name__ == "__main__":
    print parse_datetime("2016-01-01")
