import urllib
import urllib2
import logging
import logging.config
from stock.globalvar import *

logging.config.fileConfig(LOGCONF)
logger = logging.getLogger(__name__)

class RequestError(Exception):
    pass

class Request:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31'
        self.timeout = 10

    def send_request(self, url, data=None):
        headers = {'User-Agent': self.user_agent}
        req = urllib2.Request(url, headers=headers)
        i = 0
        while i < 5:
            try:
                response = None
                if data:
                    params = urllib.urlencode(data)
                    response = urllib2.urlopen(req, params, timeout=self.timeout)
                else:
                    response = urllib2.urlopen(req, timeout=self.timeout)

                if response.code != 200:
                    raise RequestError('HTTP code is not 200. Error sending request to url: ' + url)
                return response.read()
            except urllib2.URLError, e:
                logger.error("Request failed for %s with reason: %s" % (url, e.reason))
            except RequestError, e:
                logger.error("Request failed for %s with reason: %s" % (url, e.reason))
            except Exception, e:
                print str(e)
                logger.error("Unknown error")
            i = i + 1

    def download_file(self, url, path):
        headers = {'User-Agent': self.user_agent}
        req = urllib2.Request(url, headers=headers)
        i = 0
        while i < 5:
            try:
                response = urllib2.urlopen(req, timeout=self.timeout)
                if response.code != 200:
                    raise RequestError('HTTP code is not 200. Error downloading file from url: ' + url)
                content = response.read()
                file = open(path, 'w')
                file.write(content)
                file.close()
                return content
            except urllib2.URLError, e:
                print "Request failed for %s with reason: %s" % (url, e.reason)
            except RequestError, e:
                print "Request failed for %s with reason: %s" % (url, e.reason)
            except Exception, e:
                print str(e)
                print "Unknown error"
            i = i + 1

