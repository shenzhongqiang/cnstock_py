import urllib
import urllib2

class RequestError(Exception):
    pass

class Request:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
        self.timeout = 10

    def send_request(self, url):
        headers = {'User-Agent': self.user_agent}
        req = urllib2.Request(url, headers=headers)
        i = 0
        while i < 5:
            try:
                response = urllib2.urlopen(req, timeout=self.timeout)
                if response.code != 200:
                    raise RequestError('HTTP code is not 200. Error sending request to url: ' + url)
                return response.read()
            except URLError, e:
                print e.reason
            except RequestError, e:
                print e.reason
            i = i + 1

    def download_file(self, url, path):
        headers = {'User-Agent': self.user_agent}
        req = urllib2.Request(url, headers=headers)
        i = 0
        while i < 5:
            try:
                response = urllib2.urlopen(req, timeout=self.timeout)
                if response.code != 200:
                    raise RequestError('HTTP code is not 200. Error sending request to url: ' + url)
                file = open(path, 'w')
                file.write(response.read())
                file.close()
                return
            except URLError, e:
                print e.reason
            except RequestError, e:
                print e.reason
            i = i + 1

